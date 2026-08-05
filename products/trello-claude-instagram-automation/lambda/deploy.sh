#!/bin/bash
# ============================================================================
# Image-rendering Lambda — first-time deploy
#
# Provisions, from scratch: a private S3 bucket, an IAM role, the Lambda
# function (Python 3.12, arm64), a public Function URL gated by a shared
# secret header, a dedicated CloudFront distribution with Origin Access
# Control, and the bucket policy tying them together.
#
# Requires: AWS CLI v2 configured with credentials that can create IAM roles,
# S3 buckets, Lambda functions, and CloudFront distributions.
#
# Run once. For code updates after this, use update.sh instead — it only
# replaces the function code and is much faster.
# ============================================================================
set -euo pipefail

REGION="us-east-1"                          # CloudFront requires the S3 bucket's
                                              # ACM/edge behavior to originate from
                                              # a real region; us-east-1 is the
                                              # conventional default.
BUCKET="${ASSETS_BUCKET:?Set ASSETS_BUCKET to a globally-unique S3 bucket name, e.g. export ASSETS_BUCKET=my-brand-ig-assets}"
FUNCTION_NAME="${FUNCTION_NAME:-instagram-render-image}"
ROLE_NAME="${ROLE_NAME:-lambda-render-role}"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"

# The Function URL is public/unauthenticated at the AWS layer (needed so n8n
# can call it directly) — RENDER_API_KEY is the only thing gating it. Never
# hardcode the value here; export it in your shell before running this script.
: "${RENDER_API_KEY:?Set RENDER_API_KEY in your shell before running this script (e.g. export RENDER_API_KEY=$(openssl rand -hex 32))}"

echo "== Step 1: Create the S3 bucket (private, Block Public Access ON) =="
aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
aws s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "== Step 2: Create IAM role for the Lambda (basic execution + S3 write) =="
cat > /tmp/trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF
aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document file:///tmp/trust-policy.json

aws iam attach-role-policy --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > /tmp/s3-write-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:PutObject"],
    "Resource": "arn:aws:s3:::${BUCKET}/posts/*"
  }]
}
EOF
aws iam put-role-policy --role-name "$ROLE_NAME" --policy-name s3-write-posts \
  --policy-document file:///tmp/s3-write-policy.json

echo "== Step 3: Package the Lambda (Pillow via pip cross-platform download, arm64) =="
rm -rf build && mkdir -p build
pip install pillow --platform manylinux2014_aarch64 --target build \
  --only-binary=:all: --python-version 3.12
cp templates.py lambda_handler.py build/
cp -r fonts build/fonts
cd build && zip -r ../lambda_deploy.zip . -x '*.pyc' && cd ..
echo "Package size: $(du -sh lambda_deploy.zip | cut -f1)"

echo "== Step 4: Create the Lambda function =="
# IAM propagation lag: a role created seconds ago can 404 on create-function.
sleep 10
aws lambda create-function \
  --function-name "$FUNCTION_NAME" \
  --runtime python3.12 \
  --architectures arm64 \
  --role "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}" \
  --handler lambda_handler.handler \
  --zip-file fileb://lambda_deploy.zip \
  --environment "Variables={ASSETS_BUCKET=${BUCKET},RENDER_API_KEY=${RENDER_API_KEY},BRAND_NAME=${BRAND_NAME:-YOUR BRAND},BRAND_HANDLE=${BRAND_HANDLE:-@yourbrand},FONT_BLACK=${FONT_BLACK:-Display-Black.otf},FONT_BOLD=${FONT_BOLD:-Display-Bold.otf},FONT_SEMIBOLD=${FONT_SEMIBOLD:-Text-SemiBold.otf},FONT_MEDIUM=${FONT_MEDIUM:-Text-Medium.otf}}" \
  --timeout 15 \
  --memory-size 512

echo "== Waiting for the function to become Active =="
aws lambda wait function-active --function-name "$FUNCTION_NAME"

echo "== Step 5: Create Function URL (simplest way for n8n to call it directly) =="
aws lambda create-function-url-config \
  --function-name "$FUNCTION_NAME" \
  --auth-type NONE

aws lambda add-permission \
  --function-name "$FUNCTION_NAME" \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type NONE

# Required in addition to the grant above since ~Oct 2025 — AWS added a second
# permission gate for public Function URLs. Without this, every call 403s even
# though the resource policy above looks correct.
aws lambda add-permission \
  --function-name "$FUNCTION_NAME" \
  --statement-id FunctionURLAllowPublicInvoke \
  --action lambda:InvokeFunction \
  --principal "*"

echo "== Step 6: Create a dedicated CloudFront distribution with Origin Access Control =="
OAC_ID=$(aws cloudfront create-origin-access-control \
  --origin-access-control-config \
  Name="${FUNCTION_NAME}-oac",Description="OAC for ${BUCKET}",SigningProtocol="sigv4",SigningBehavior="always",OriginAccessControlOriginType="s3" \
  --query 'OriginAccessControl.Id' --output text)
echo "OAC created: $OAC_ID"

cat > /tmp/cf-dist-config.json << EOF
{
  "CallerReference": "${FUNCTION_NAME}-$(date +%s)",
  "Comment": "Instagram content automation - image delivery",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "assets-origin",
      "DomainName": "${BUCKET}.s3.${REGION}.amazonaws.com",
      "OriginAccessControlId": "${OAC_ID}",
      "S3OriginConfig": { "OriginAccessIdentity": "" }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "assets-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2, "Items": ["GET", "HEAD"],
      "CachedMethods": { "Quantity": 2, "Items": ["GET", "HEAD"] }
    },
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "Compress": true
  },
  "PriceClass": "PriceClass_100"
}
EOF

CF_RESULT=$(aws cloudfront create-distribution --distribution-config file:///tmp/cf-dist-config.json)
DISTRIBUTION_ID=$(echo "$CF_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['Distribution']['Id'])")
CLOUDFRONT_DOMAIN=$(echo "$CF_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['Distribution']['DomainName'])")
echo "Distribution created: $DISTRIBUTION_ID ($CLOUDFRONT_DOMAIN)"

echo "== Step 7: Bucket policy — only this distribution's OAC may read /posts/* =="
cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontServicePrincipal",
    "Effect": "Allow",
    "Principal": { "Service": "cloudfront.amazonaws.com" },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::${BUCKET}/posts/*",
    "Condition": {
      "StringEquals": { "AWS:SourceArn": "arn:aws:cloudfront::${AWS_ACCOUNT_ID}:distribution/${DISTRIBUTION_ID}" }
    }
  }]
}
EOF
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file:///tmp/bucket-policy.json

echo "== Step 8: Point the Lambda's CLOUDFRONT_DOMAIN at the new distribution =="
aws lambda update-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --environment "Variables={ASSETS_BUCKET=${BUCKET},RENDER_API_KEY=${RENDER_API_KEY},CLOUDFRONT_DOMAIN=${CLOUDFRONT_DOMAIN},BRAND_NAME=${BRAND_NAME:-YOUR BRAND},BRAND_HANDLE=${BRAND_HANDLE:-@yourbrand},FONT_BLACK=${FONT_BLACK:-Display-Black.otf},FONT_BOLD=${FONT_BOLD:-Display-Bold.otf},FONT_SEMIBOLD=${FONT_SEMIBOLD:-Text-SemiBold.otf},FONT_MEDIUM=${FONT_MEDIUM:-Text-Medium.otf}}"
aws lambda wait function-updated --function-name "$FUNCTION_NAME"

echo ""
echo "== Distribution is deploying — this takes several minutes to reach every edge =="
echo "Check status with: aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.Status'"
echo "Smoke-testing before it's fully deployed may 403 briefly; that's expected, not a bug."
echo ""
echo "== Step 9: Smoke test =="
FUNCTION_URL=$(aws lambda get-function-url-config --function-name "$FUNCTION_NAME" --query FunctionUrl --output text)
echo "Function URL: $FUNCTION_URL"
curl -s -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "X-Render-Secret: ${RENDER_API_KEY}" \
  -d '{"template":"hook_simples","fields":{"headline":"Deploy test"}}' | python3 -m json.tool

echo ""
echo "== Done. Save these — you'll need them for the n8n workflows =="
echo "FUNCTION_URL:      $FUNCTION_URL"
echo "CLOUDFRONT_DOMAIN: $CLOUDFRONT_DOMAIN"
echo "RENDER_API_KEY:    (the value you exported — store it in your password manager, not here)"
