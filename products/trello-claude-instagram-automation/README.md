# Trello + Claude + Instagram automation

An end-to-end content pipeline: plan post ideas as Trello cards, have Claude write the copy, render an on-brand image with a Lambda function, approve on Trello, and auto-publish to Instagram. Two n8n workflows connect the pieces.

```
Trello (💡 Ideas)
   │  you write: content type + a one-line idea
   ▼
✍️ To Generate  ──────────────┐
   │                          │  WF1 (scheduled or manual)
   │                          ▼
   │                 Claude writes headline/quote/stat + caption
   │                          │
   │                          ▼
   │                 Lambda renders a JPEG, uploads to S3
   │                          │
   │                          ▼
   └──────────────  👀 To Approve  (image + caption on the card)
                              │
                    you review, move the card
                              ▼
                        ✅ Approved ──────────────┐
                                                   │  WF2 (polls every 10 min)
                                                   ▼
                                    Instagram Graph API: create container → publish
                                                   │
                                                   ▼
                                            🟢 Published
                       (any failure anywhere →  ❌ Error, with the reason on the card)
```

## What's included

| Path | What it is |
|---|---|
| `n8n/workflow-1-generate-image.json` | Trello → Claude → Lambda → Trello. Generates the image + caption. |
| `n8n/workflow-2-publish-instagram.json` | Trello → Instagram Graph API → Trello. Publishes approved posts. |
| `lambda/templates.py` | 6 brand-agnostic image layouts (Pillow), each taking simple text fields. |
| `lambda/lambda_handler.py` | Lambda entry point: validates the request, renders, uploads to S3. |
| `lambda/deploy.sh` | One-shot script: S3 bucket, IAM role, Lambda, Function URL, CloudFront + OAC. |
| `lambda/update.sh` | Redeploy just the code after you edit `templates.py`/`lambda_handler.py`. |
| `lambda/fonts/` | Empty on purpose — bring your own font files, see `lambda/fonts/README.md`. |

## Prerequisites

You need accounts/setup in four places before importing anything:

1. **AWS account** with CLI v2 configured (`aws configure`), and permission to create IAM roles, S3 buckets, Lambda functions, and CloudFront distributions.
2. **Trello account** with a board laid out with (at least) these lists, in order: `To Generate`, `To Approve`, `Approved`, `Published`, `Error`. Names are up to you — you'll paste each list's ID into the workflows, not its name.
3. **Anthropic API key** (console.anthropic.com) for the Claude node.
4. **n8n instance** (Cloud or self-hosted) able to install the `@n8n/n8n-nodes-langchain` community package (usually preinstalled on n8n Cloud) and reach the public internet (to call your Lambda and the Meta Graph API).
5. **Meta / Instagram setup** — the involved one, covered in detail below:
   - An Instagram account converted to **Business or Creator**
   - That account linked to a **Facebook Page** you administer
   - A **Meta App** (developers.facebook.com) with the `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, and `business_management` permissions
   - Those permissions **approved in App Review** — this is the part that gates everything else and can take the longest, so start it first

## Setup

### 1. AWS — deploy the image-rendering Lambda

```bash
cd lambda
# bring your own fonts first — see lambda/fonts/README.md
export ASSETS_BUCKET=my-brand-ig-assets      # must be globally unique
export RENDER_API_KEY=$(openssl rand -hex 32)
export BRAND_NAME="YOUR BRAND"               # optional, shown in the templates
export BRAND_HANDLE="@yourbrand"             # optional, shown in the footer
./deploy.sh
```

This provisions, in order: a private S3 bucket, an IAM role, the Lambda function, a public Function URL gated by the `X-Render-Secret` header, a dedicated CloudFront distribution with Origin Access Control, and the bucket policy connecting them. It prints the **Function URL** and **CloudFront domain** at the end — save both, you'll need them for WF1.

Save `RENDER_API_KEY` in a password manager. It's the only thing standing between your Function URL and anyone on the internet who finds it.

After editing `templates.py` or the fonts later, redeploy code only with `./update.sh` — much faster, doesn't touch infrastructure.

### 2. Trello — get your list IDs

For each list (`To Generate`, `To Approve`, `Approved`, `Published`, `Error`), you need its ID, not its name. Easiest way: open the list's menu → the URL bar or Trello's API (`https://api.trello.com/1/boards/{board_id}/lists?key=...&token=...`) both expose it. Keep these 5 IDs handy for step 4.

Also decide the JSON schema your cards' descriptions will use — WF1 expects:
```json
{
  "content_type": "hook",
  "idea_description": "your one-line idea, in plain language",
  "caption": "",
  "image_url": "",
  "scheduled_time": "",
  "expected_generation_date": "2026-01-01T00:00:00.000Z",
  "ig_post_id": "",
  "error_message": ""
}
```
You (or whoever plans content) write `content_type` and `idea_description` when creating a card in `To Generate`. Everything else starts empty and gets filled in by the workflows as the card moves through the pipeline.

### 3. Meta — the token chain (the part that trips people up)

The Instagram Graph API never lets you address an Instagram account directly — the path is always **user → the Facebook Page you administer → the Instagram account linked to that Page.**

```
User token (short-lived, ~2h)
  → GET /oauth/access_token  (grant_type=fb_exchange_token, with your app_id + app_secret)
  → User token (long-lived, ~60 days)
  → GET /me/accounts  (called WITH the already-long-lived user token)
  → Page token (inherits non-expiring status — only if the input was already long-lived)
  → GET /{page_id}?fields=instagram_business_account
  → Instagram User ID
```

Two things that aren't obvious and will cost you time if you get them wrong:

- **Order matters.** The long-lived exchange has to happen *before* you call `/me/accounts`. "Long-lived" doesn't propagate backwards — if you call `/me/accounts` with a still-short-lived user token, the Page token you get back is short-lived too.
- **Publishing calls use the Page token, not the user token.** `POST /{ig_user_id}/media` and `POST /{ig_user_id}/media_publish` will reject a user token even with `instagram_content_publish` granted — the Instagram account is a child object of the Page in Meta's permission model, so the token has to carry Page-level authorization specifically.

Step by step, using the [Graph API Explorer](https://developers.facebook.com/tools/explorer):

1. Select your App, click **Generate Access Token**, grant it the permissions listed in Prerequisites above.
2. Exchange it for a long-lived user token:
   ```
   GET /oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={your_app_id}
     &client_secret={your_app_secret}
     &fb_exchange_token={the_short_lived_token_from_step_1}
   ```
3. With that long-lived token now active in the Explorer, run `GET /me/accounts`. Find your Page in the results — copy its `access_token`. This is the **Page token**, and it's what goes into n8n.
4. Confirm it doesn't expire: paste it into the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) — you want `expires_at: 0`. (Don't confuse this with `data_access_expires_at`, a separate 90-day data-access privacy window that renews automatically and doesn't affect whether the token works.)
5. Get your Instagram User ID:
   ```
   GET /{page_id}?fields=instagram_business_account
   ```
   The `instagram_business_account.id` in the response is what goes into WF2's "Parse & validate" node.

### 4. n8n — import and configure

Import both `n8n/workflow-1-generate-image.json` and `n8n/workflow-2-publish-instagram.json`. Each has a **sticky note pinned in the canvas** listing exactly what's left to fill in — placeholders are named things like `PASTE_YOUR_TRELLO_LIST_ID_TO_GENERATE` so they're easy to find with Ctrl+F on the node.

Broadly:
- **WF1**: 3 Trello list IDs, Trello + Anthropic credentials, the Lambda's Header Auth credential (`X-Render-Secret` = the `RENDER_API_KEY` from step 1), and the Lambda Function URL. Also edit the "Build Claude Prompt" node — `BRAND_SYSTEM` and `CONTENT_TYPE_RULES` are placeholders, replace them with your own brand voice and content pillars.
- **WF2**: 3 more Trello list IDs, Trello credential, a Header Auth credential for `Authorization: Bearer {your Page token}`, and the Instagram User ID from step 3.

n8n does not export credential *links* (only workflows reference credential IDs, and those IDs are per-instance) — this is the one manual step you'll redo on every re-import, not a bug in the files.

### 5. Test before activating

Run each workflow manually on a single real card before flipping the "Active" toggle:
- WF1: create one card in `To Generate` with a real `content_type`/`idea_description`, execute the workflow, confirm the card lands in `To Approve` with an image and caption.
- WF2: create a container without publishing first if you want an extra safety check — a container (`POST /media`) isn't public until you separately call `/media_publish`, and unused containers just expire after 24h. Then move a test card to `Approved` and run WF2 once to confirm the full publish path.

## Content safety guardrails baked into WF1

- **No fabricated data.** Content types that need a real statistic or news fact (`hook_stat`, `math_example`, `news_reaction` in the example taxonomy) instruct Claude to return `{"error": "missing_source_data"}` rather than invent one, if your idea description doesn't already contain a concrete, verifiable number or fact. The workflow routes that straight to the Error list instead of publishing.
- **JPEG only.** The Instagram Content Publishing API rejects PNG (error code 24) — the Lambda always outputs JPEG.
- **Duplicate-publish protection.** WF2 skips any card that already has `ig_post_id` set, so a card that loops back to `Approved` by mistake doesn't get posted twice.
- **Format validation before spending an API call.** WF2 checks `image_url` is a public `.jpg`/`.jpeg` URL before calling Meta at all.

## Known limitations (not fixed on purpose — decide these for your own use case)

- **No per-run publish throttle.** If multiple cards are in `Approved` when WF2's poll fires, it publishes all of them in that run, with no spacing between posts. Pace this manually via how you approve cards, or add a rate limit yourself if you need one.
- **Polling, not webhooks.** Both workflows poll on a timer rather than reacting to Trello webhooks — simpler to reason about and test manually, at the cost of up to one poll interval of latency.

## License

MIT — see `LICENSE`. Bring your own fonts and read their license before bundling them (see `lambda/fonts/README.md`); this repo's MIT license does not cover any font files you add.
