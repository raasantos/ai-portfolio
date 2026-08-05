# fonts/

This folder is empty on purpose — no font files ship with this repo. AWS Lambda has no system fonts installed, so `templates.py` needs real `.otf`/`.ttf` files bundled in the deployment package to draw any text at all.

Bring your own. Drop **4 font files** here, one per weight:

| Role | Used for | Env var (points `templates.py` at the filename) | Default filename expected |
|---|---|---|---|
| Black / Heavy | Large display headlines, big numbers | `FONT_BLACK` | `Display-Black.otf` |
| Bold | The `quote` template's quote text | `FONT_BOLD` | `Display-Bold.otf` |
| Semibold | Tags, eyebrows, letter-spaced small caps | `FONT_SEMIBOLD` | `Text-SemiBold.otf` |
| Medium | Body copy, subtext, footer wordmark | `FONT_MEDIUM` | `Text-Medium.otf` |

Two ways to wire them up:

1. **Rename your files to match the defaults above** — simplest, no config needed.
2. **Keep your own filenames and set the env vars** on the Lambda (`deploy.sh` already forwards `FONT_BLACK`, `FONT_BOLD`, `FONT_SEMIBOLD`, `FONT_MEDIUM` if you export them before running it) — e.g. `export FONT_BLACK=Poppins-Black.otf`.

All four can point at weights of the same typeface, or at genuinely different typefaces — `templates.py` doesn't care, it just loads whatever filename each `FONT_*` var resolves to.

**Before deploying:** check your font's license permits bundling/embedding in an application (most do — this is normal and expected for web/app fonts). A few commercial or "desktop only" licenses don't allow this; read the license file that came with your font if you're unsure. Good free options with permissive licenses: [Inter](https://rsms.me/inter/) (SIL OFL), [Public Sans](https://public-sans.digital.gov/) (SIL OFL), or any variable font from [Google Fonts](https://fonts.google.com/) (nearly all SIL OFL or Apache 2.0).

`deploy.sh` will zip whatever is in this folder — if it's empty, the Lambda will deploy successfully but every render call will fail at runtime with a font-not-found error. That failure is expected until you've placed real font files here.
