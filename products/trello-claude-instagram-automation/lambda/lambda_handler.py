"""
lambda_handler.py — renders an Instagram post image from a template + fields,
uploads it to S3, and returns the public (CloudFront) URL.

Required header (the Function URL is public/unauthenticated at the AWS layer,
so this is the only thing stopping a random caller from invoking it):
  X-Render-Secret: <value of the RENDER_API_KEY env var>

Input (POST body, JSON):
{
  "template": "tag_headline",          # key from templates.TEMPLATES
  "fields": {                           # kwargs passed straight into that template function
    "tag": "TRUST",
    "headline": "Your bank manager\nhas a sales quota.",
    "subtext": "We don't have a product to sell."
  }
}

Output (403):
{ "error": "forbidden" }               # missing/wrong X-Render-Secret

Output (200):
{ "image_url": "https://your-distribution.cloudfront.net/posts/<uuid>.jpg" }

Output (400/500):
{ "error": "..." }

Deployment notes:
- Bundle the Inter .otf files used by templates.py into the deployment package
  (e.g. a `fonts/` folder alongside this file) and point templates.FONT_DIR at
  it — Lambda's runtime has no system fonts installed.
- The S3 bucket (ASSETS_BUCKET) should stay private (Block Public Access ON).
  Serve images through a CloudFront distribution with an Origin Access Control
  pointed at the bucket, path pattern /posts/* — never through a public S3 URL
  or bucket ACL. See ../README.md for the full CloudFront + OAC setup.
"""
import json
import io
import os
import uuid
import inspect
import hmac
import boto3

from templates import TEMPLATES, FIELD_SCHEMA

s3 = boto3.client("s3")
BUCKET = os.environ.get("ASSETS_BUCKET", "REPLACE_WITH_YOUR_BUCKET_NAME")
CLOUDFRONT_DOMAIN = os.environ.get("CLOUDFRONT_DOMAIN", "REPLACE_WITH_YOUR_CLOUDFRONT_DOMAIN")
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "")


def _filter_and_validate_fields(template_name, render_fn, fields):
    """Keeps only the kwargs render_fn actually accepts (drops extras like a
    'tag' sent for a template that doesn't use one — needed because n8n now
    sends a superset of fields when randomly picking among style variants),
    and checks every parameter without a default is present."""
    sig = inspect.signature(render_fn)
    valid_params = set(sig.parameters.keys())
    filtered = {k: v for k, v in fields.items() if k in valid_params}

    required = [
        name for name, p in sig.parameters.items()
        if p.default is inspect.Parameter.empty
    ]
    missing = [f for f in required if f not in filtered]
    if missing:
        raise ValueError(f"missing required fields for '{template_name}': {missing}")
    return filtered


def handler(event, context):
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if not hmac.compare_digest(headers.get("x-render-secret", ""), RENDER_API_KEY):
        return _response(403, {"error": "forbidden"})

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "invalid JSON body"})

    template_name = body.get("template")
    fields = body.get("fields", {})

    if template_name not in TEMPLATES:
        return _response(400, {"error": f"unknown template '{template_name}'. "
                                          f"valid: {list(TEMPLATES.keys())}"})

    render_fn = TEMPLATES[template_name]
    try:
        filtered_fields = _filter_and_validate_fields(template_name, render_fn, fields)
        img = render_fn(**filtered_fields)
    except ValueError as e:
        return _response(400, {"error": str(e)})
    except TypeError as e:
        return _response(400, {"error": f"field mismatch for template '{template_name}': {e}"})

    # JPEG, not PNG: the Instagram Content Publishing API rejects anything but
    # JPEG (error code 24). subsampling=0 keeps 4:4:4 chroma — with white text
    # on black, the default 4:2:0 leaves visible fringing on the letter edges.
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95, subsampling=0, optimize=True)
    buf.seek(0)

    key = f"posts/{uuid.uuid4()}.jpg"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf, ContentType="image/jpeg")

    image_url = f"https://{CLOUDFRONT_DOMAIN}/{key}"
    return _response(200, {"image_url": image_url})


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


# Local smoke test — simulates an API Gateway event without needing AWS at all.
# Run: python3 lambda_handler.py
if __name__ == "__main__":
    RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "local-test")
    fake_event = {
        "headers": {"x-render-secret": RENDER_API_KEY},
        "body": json.dumps({
            "template": "tag_headline",
            "fields": {
                "tag": "TRUST",
                "headline": "Your bank manager\nhas a sales quota.",
                "subtext": "We don't have a product to sell."
            }
        })
    }
    # Monkeypatch s3.put_object for the local smoke test — no AWS calls, just
    # confirms the render + dispatch + validation logic works end to end.
    class _FakeS3:
        def put_object(self, **kwargs):
            with open("/tmp/lambda_smoke_test.png", "wb") as f:
                f.write(kwargs["Body"].getvalue())
    s3 = _FakeS3()
    print(handler(fake_event, None))
