# AURA - AI Music Composer

> Turn a feeling into something you can hear.

AURA is an AI-assisted music composition studio built with Streamlit. Describe a scene, mood, or story and generate a playable musical sketch with melody, harmony, rhythm, and style-aware composition.

## Highlights

- Natural-language music prompts
- Genre, mood, tempo, instrument palette, and duration controls
- AI-generated melody, harmony, rhythm, and composition summary
- WAV playback directly in the browser
- Recent composition history
- Docker and Kubernetes deployment support

## How it works

1. A prompt is enriched with the selected musical parameters.
2. Groq generates a melody, harmony, and rhythm description.
3. The generated notes are converted into frequencies with `music21`.
4. A lightweight synthesizer renders the result as a WAV file.
5. Streamlit presents the composition for immediate playback.

## Requirements

- Python 3.13+
- A Groq API key
- Docker Desktop (optional)
- Kubernetes cluster (optional)

## Local setup

```powershell
git clone https://github.com/MustafaKocamann/AI-Music-Composer.git
cd AI-Music-Composer

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Start the application:

```powershell
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

## Docker

Build and run the image:

```powershell
docker build -t ai-music-composer:latest .
docker run --env-file .env -p 8501:8501 ai-music-composer:latest
```

## Kubernetes

Create the API key secret:

```powershell
kubectl create secret generic ai-music-composer-secrets `
  --from-literal=GROQ_API_KEY="your_groq_api_key"
```

Apply the deployment:

```powershell
kubectl apply -f kubernetes-deployment.yaml
```

The manifest exposes the application through a `LoadBalancer` service on port `80` and forwards traffic to Streamlit on port `8501`.

## Project structure

```text
.
├── app.py                       # Streamlit interface and composition flow
├── app/
│   ├── main.py                  # Groq/LangChain music generation
│   └── utils.py                 # Note parsing and WAV synthesis
├── Dockerfile
├── kubernetes-deployment.yaml
└── requirements.txt
```

## Notes

AURA is designed as a creative sketching tool. The current synthesizer renders generated note frequencies as a simple WAV arrangement; the output is intended for ideation and experimentation.

## License

No license has been selected yet. Add a license before distributing the project.