# PodTranslate Quick Start Guide

## Get Started in 5 Minutes

### 1. Prerequisites
```bash
# Check installations
docker --version  # Should be 24.0+
docker-compose --version  # Should be 2.0+
```

### 2. Clone and Setup
```bash
# Clone repository
git clone <repository-url>
cd PODTRANSLATE-

# Copy environment file
cp .env.example .env
```

### 3. Configure API Keys

Edit `.env` and add your API keys:

```bash
# REQUIRED - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# REQUIRED - Get from https://aws.amazon.com/
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_AUDIO=your-bucket-name
S3_BUCKET_TRANSCRIPTS=your-bucket-name

# REQUIRED - Get from https://huggingface.co/settings/tokens
PYANNOTE_AUTH_TOKEN=hf_your-token-here

# OPTIONAL - For faster translation
DEEPL_API_KEY=your-deepl-key
```

### 4. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Wait for services to be healthy (about 1-2 minutes)
docker-compose ps
```

### 5. Verify Installation
```bash
# Check API Gateway
curl http://localhost:3000/api/v1/health

# Expected output:
# {"status":"healthy","timestamp":"...","service":"api-gateway"}

# Check Audio Processing Service
curl http://localhost:3001/health

# Expected output:
# {"status":"healthy","service":"audio-processing"}
```

### 6. View API Documentation
Open your browser and navigate to:
```
http://localhost:3000/docs
```

### 7. Create Your First Transcription

**Using cURL:**
```bash
# 1. Upload an audio file and create transcription job
curl -X POST http://localhost:3001/transcribe/upload \
  -F "file=@/path/to/your/podcast.mp3" \
  -F "podcast_id=my-podcast" \
  -F "episode_id=episode-001" \
  -F "source_language=en" \
  -F "target_languages=es,fr,de" \
  -F "enable_diarization=true" \
  -F "enable_translation=true"

# Response will include job_id
# {"job_id":"abc-123","status":"queued"}

# 2. Check job status
curl http://localhost:3001/jobs/abc-123

# 3. View logs to monitor progress
docker-compose logs -f audio-processing
```

**Using Python:**
```python
import requests

# Upload audio file
with open('podcast.mp3', 'rb') as f:
    response = requests.post(
        'http://localhost:3001/transcribe/upload',
        files={'file': f},
        data={
            'podcast_id': 'my-podcast',
            'episode_id': 'episode-001',
            'source_language': 'en',
            'target_languages': 'es,fr,de',
            'enable_diarization': True,
            'enable_translation': True
        }
    )

job_id = response.json()['job_id']
print(f"Job created: {job_id}")

# Check status
status = requests.get(f'http://localhost:3001/jobs/{job_id}')
print(status.json())
```

**Using JavaScript:**
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

// Upload audio file
const form = new FormData();
form.append('file', fs.createReadStream('podcast.mp3'));
form.append('podcast_id', 'my-podcast');
form.append('episode_id', 'episode-001');
form.append('source_language', 'en');
form.append('target_languages', 'es,fr,de');
form.append('enable_diarization', 'true');
form.append('enable_translation', 'true');

const response = await axios.post(
  'http://localhost:3001/transcribe/upload',
  form,
  { headers: form.getHeaders() }
);

console.log('Job created:', response.data.job_id);

// Check status
const status = await axios.get(
  `http://localhost:3001/jobs/${response.data.job_id}`
);
console.log('Status:', status.data);
```

## What Happens During Transcription?

1. **Upload & Preprocessing** (1-2 min)
   - Audio file uploaded to S3
   - Converted to WAV 16kHz mono
   - Noise reduction applied
   - Audio normalized

2. **Speaker Diarization** (2-5 min)
   - Identifies different speakers
   - Creates speaker segments
   - Labels speakers (SPEAKER_00, SPEAKER_01, etc.)

3. **Transcription** (varies by length)
   - Whisper large-v3 transcribes audio
   - Word-level timestamps generated
   - Speaker labels attached to segments

4. **Translation** (varies by # of languages)
   - GPT-4 translates to target languages
   - Maintains conversational tone
   - Preserves speaker labels
   - Uploaded to S3

5. **Completion**
   - Job status updated to "completed"
   - Transcription URLs available
   - Ready for distribution

## Example Output

### Original Transcription (English)
```json
{
  "text": "Welcome to our podcast about technology...",
  "language": "en",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Welcome to our podcast about technology",
      "speaker": "SPEAKER_00",
      "words": [
        {"word": "Welcome", "start": 0.0, "end": 0.5},
        {"word": "to", "start": 0.5, "end": 0.7},
        ...
      ]
    }
  ]
}
```

### Translation (Spanish)
```json
{
  "text": "Bienvenido a nuestro podcast sobre tecnología...",
  "language": "es",
  "source_language": "en",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Bienvenido a nuestro podcast sobre tecnología",
      "speaker": "SPEAKER_00"
    }
  ]
}
```

## Next Steps

### 1. Set Up Distribution
Configure platform credentials for automatic distribution:

```bash
# Spotify
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret

# Apple Podcasts
APPLE_KEY_ID=your-key-id
APPLE_TEAM_ID=your-team-id
APPLE_PRIVATE_KEY_PATH=/path/to/key.p8
```

### 2. Enable Analytics
Start collecting analytics data:

```bash
# Configure analytics
SEGMENT_WRITE_KEY=your-segment-key
MIXPANEL_TOKEN=your-mixpanel-token
```

### 3. Try AI Content Tools
Generate blog posts, social media content, and more from your transcripts.

### 4. Explore the Dashboard
```bash
# Start the frontend dashboard (coming soon)
cd frontend/dashboard
npm install
npm run dev
```

## Common Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f audio-processing

# Restart a service
docker-compose restart audio-processing

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Update services
git pull
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Audio Processing Service Won't Start
```bash
# Check logs
docker-compose logs audio-processing

# Common issues:
# 1. Missing OPENAI_API_KEY - Add to .env
# 2. Missing PYANNOTE_AUTH_TOKEN - Get from HuggingFace
# 3. Insufficient memory - Increase Docker memory limit
```

### Transcription Job Stuck
```bash
# Check job status
curl http://localhost:3001/jobs/{job_id}

# Check RabbitMQ queue
# Open http://localhost:15672 (guest/guest)

# Restart audio processing service
docker-compose restart audio-processing
```

### Out of Memory
```bash
# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory -> 8GB+

# Or use smaller Whisper model in .env:
WHISPER_MODEL=medium  # Instead of large-v3
```

## Resource Requirements

### Minimum (Testing)
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB
- GPU: None (CPU mode)

### Recommended (Production)
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 100+ GB SSD
- GPU: NVIDIA GPU with 8GB+ VRAM (optional, for faster transcription)

### Processing Times (Approximate)

| Audio Length | CPU Mode | GPU Mode (RTX 3080) |
|--------------|----------|---------------------|
| 30 min       | 15 min   | 3 min               |
| 1 hour       | 30 min   | 6 min               |
| 2 hours      | 60 min   | 12 min              |

## Getting Help

- **Documentation**: [docs/](../docs/)
- **API Reference**: http://localhost:3000/docs
- **Issues**: GitHub Issues
- **Email**: support@podtranslate.com

## What's Next?

Explore the full documentation:

- [Architecture Overview](ARCHITECTURE.md)
- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

Happy podcasting! 🎙️
