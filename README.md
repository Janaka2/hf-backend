# HF Backend (FastAPI) via GitHub Actions

This backend is deployed to a Hugging Face Space and reads secrets from **Space Secrets** injected by **GitHub Actions**.

## Required GitHub settings (in the *backend* repo)

- **Secrets → Actions**
  - `HF_TOKEN` — Hugging Face write token
  - `MY_API_KEY` — your real key (OpenAI, etc.)

- **Variables → Actions**
  - `SPACE_ID` — `your-username/your-space-name`
  - `ALLOWED_ORIGINS` (optional) — comma-separated list of allowed CORS origins, e.g. `https://your.github.io,https://your.github.io/your-repo`

After pushing to `main`, the Action:
- Creates/updates the FastAPI Space
- Uploads this repo
- Configures Space Secret `MY_API_KEY`
- Sets Space Variable `ALLOWED_ORIGINS` if provided
