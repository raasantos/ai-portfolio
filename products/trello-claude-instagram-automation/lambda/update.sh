#!/bin/bash
# ============================================================================
# Image-rendering Lambda — code update (not first deploy)
# Use this instead of deploy.sh once the function, role, bucket, Function URL
# and CloudFront origin already exist. deploy.sh uses create-* calls that fail
# once the resources are already there; this only pushes new code.
# ============================================================================
set -euo pipefail

FUNCTION_NAME="${FUNCTION_NAME:-instagram-render-image}"

echo "== Package the Lambda (Pillow via pip cross-platform download, arm64) =="
rm -rf build && mkdir -p build
pip install pillow --platform manylinux2014_aarch64 --target build \
  --only-binary=:all: --python-version 3.12
cp templates.py lambda_handler.py build/
cp -r fonts build/fonts
cd build && zip -r ../lambda_deploy.zip . -x '*.pyc' && cd ..
echo "Package size: $(du -sh lambda_deploy.zip | cut -f1)"

echo "== Update function code =="
aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file fileb://lambda_deploy.zip

echo "== Waiting for update to finish =="
aws lambda wait function-updated --function-name "$FUNCTION_NAME"

echo "== Smoke test =="
FUNCTION_URL=$(aws lambda get-function-url-config --function-name "$FUNCTION_NAME" --query FunctionUrl --output text)
RENDER_API_KEY=$(aws lambda get-function-configuration --function-name "$FUNCTION_NAME" --query 'Environment.Variables.RENDER_API_KEY' --output text)
echo "Function URL: $FUNCTION_URL"
curl -s -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "X-Render-Secret: ${RENDER_API_KEY}" \
  -d '{"template":"hook_simples","fields":{"headline":"Update test"}}' | python3 -m json.tool
