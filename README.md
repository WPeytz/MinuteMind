# MinuteMind

MinuteMind generates short-form educational videos from a single topic prompt. The stack is built with a FastAPI
backend for orchestration and a Vue 3 + Vite frontend for the authoring experience.

## Repository Layout

- `backend/` – FastAPI application, LLM + TTS services, and stitching pipeline.
- `frontend/` – Vue single-page application styled with Tailwind CSS.
- `infra/` – Local docker-compose and Cloud Run deployment manifests.

## Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) [OpenAI API access](https://platform.openai.com/) for live LLM/TTS responses
- (Optional) FFmpeg & ImageMagick if you plan to enable real video rendering via MoviePy

## Environment Variables

The backend reads configuration through environment variables. When unset, it defaults to safe mock behaviour for
local development.

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | Auth token for OpenAI LLM + TTS calls | _unset → mock mode_ |
| `MINUTEMIND_LLM_MODEL` | Chat/Responses model used for script generation | `gpt-4o-mini` |
| `MINUTEMIND_TTS_MODEL` | OpenAI Speech model for narration | `gpt-4o-mini-tts` |
| `MINUTEMIND_TTS_VOICE` | Voice preset used for narration | `alloy` |
| `MINUTEMIND_MEDIA_ROOT` | Directory for generated audio/video assets | `./tmp` |
| `MINUTEMIND_STORAGE_BASE` | Public base URL mapped to `MEDIA_ROOT` | `http://localhost:8000/media` |
| `MINUTEMIND_FAKE_LLM` | Set to `1` to force mock script generation | `0` |
| `MINUTEMIND_FAKE_TTS` | Set to `1` to bypass OpenAI TTS and emit placeholder audio | `0` |
| `MINUTEMIND_FAKE_VIDEO` | Set to `1` to skip MoviePy and emit a text-based placeholder video | `0` |

> Tip: When you don't have OpenAI credentials available, exporting all three `MINUTEMIND_FAKE_*` flags to `1`
> keeps the entire pipeline fully offline.

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Run type-checking and tests:

```bash
mypy app
pytest
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend proxy under `/api` points to `http://localhost:8000`, so ensure the backend is running before starting
Vite. Tailwind CSS is preconfigured via PostCSS.

### Building against a remote API

When the backend is deployed (for example on Cloud Run), configure the frontend with that base URL:

```bash
cd frontend
cp .env.example .env.production    # edit VITE_API_BASE_URL=https://<your-run-service>.a.run.app
npm install                        # installs vue-router if you have not already
npm run build
```

The generated assets in `frontend/dist/` can be served from Firebase Hosting, CloudFront, or any static site host. Use
`npm run preview` locally to verify the production build.

## Local Demo Flow

1. Start the FastAPI server (`uvicorn app.main:app --reload`), leaving the `MINUTEMIND_FAKE_*` flags at their defaults
   unless you have OpenAI credentials configured.
2. Launch the frontend (`npm run dev`) and open `http://localhost:5173`.
3. Enter a topic on the **Generate** page to receive a structured script plus per-scene narration audio links.
4. Hit **Render Video** to produce a stitched asset (mock or real depending on your environment). The Library page
   lists previously rendered videos and the Player page lets you stream or download a selection.

## Deploying the Backend on Cloud Run

1. **Set up gcloud.**

   ```bash
   gcloud auth login
   gcloud config set project <PROJECT_ID>
   REGION=europe-west1     
   SERVICE=minutemind-api
   IMAGE=gcr.io/$PROJECT_ID/$SERVICE:$(git rev-parse --short HEAD)
   ```

2. **Build and push the container.** The Dockerfile lives under `backend/`.

   ```bash
   cd backend
   gcloud builds submit --tag "$IMAGE" .
   ```

3. **Store secrets.** (Run once.)

   ```bash
   echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
   # or update if the secret already exists
   echo -n "$OPENAI_API_KEY" | gcloud secrets versions add openai-api-key --data-file=-
   ```

4. **Deploy to Cloud Run.**

   ```bash
   gcloud run deploy $SERVICE \
     --image "$IMAGE" \
     --region "$REGION" \
     --allow-unauthenticated \
     --set-secrets OPENAI_API_KEY=openai-api-key:latest \
     --set-env-vars MINUTEMIND_MEDIA_ROOT=/tmp/media \
     --set-env-vars MINUTEMIND_STORAGE_BASE=https://$SERVICE_URL/media \
     --set-env-vars MINUTEMIND_FAKE_VIDEO=1
   ```

   Replace `$SERVICE_URL` with the hostname printed after deployment (for example
   `https://minutemind-api-abcdefgh-uc.a.run.app`). Leaving `MINUTEMIND_FAKE_VIDEO=1` keeps the stitching stage in placeholder mode so you do not need to expose
   locally-stored media. The current FastAPI app does not serve files from `/media`; add a static-file route or
   integrate `storage.py` with Cloud Storage before turning the flag off.

   You can also apply `infra/cloudrun.yaml` after replacing `PROJECT_ID`, `YOUR_CLOUDRUN_HOST`, and secret names:

   ```bash
   gcloud run services replace infra/cloudrun.yaml --region "$REGION"
   ```

5. **Test the service.**

   ```bash
   curl -X POST "$SERVICE_URL/scripts/generate" \
     -H "Content-Type: application/json" \
     -d '{"topic": "Neuroplasticity", "duration_minutes": 4, "tone": "engaging"}'
   ```

## Infrastructure

For local experimentation with Postgres and MinIO:

```bash
cd infra
docker compose up
```

Deploying to Cloud Run requires building and pushing the backend image referenced in `infra/cloudrun.yaml`.
