# PodTranslate API Examples

This directory contains example code for integrating with the PodTranslate API.

## Available Examples

### 1. Python SDK (`python_sdk.py`)
Full-featured Python client library with async support.

**Installation:**
```bash
pip install requests
```

**Usage:**
```python
from python_sdk import PodTranslateClient

client = PodTranslateClient(api_key="your-api-key")

# Upload and transcribe
job = client.create_transcription(
    audio_file_path="episode.mp3",
    podcast_id="my-podcast",
    episode_id="ep-001",
    target_languages=["es", "fr"]
)

# Wait for completion
result = client.wait_for_completion(job['job_id'])

# Generate blog post
blog = client.generate_blog_post(
    transcript=result['transcript']['text'],
    title="Episode Title"
)
```

### 2. Node.js SDK (`nodejs_sdk.js`)
JavaScript/TypeScript client with Promise support.

**Installation:**
```bash
npm install axios form-data
```

**Usage:**
```javascript
const PodTranslateClient = require('./nodejs_sdk');

const client = new PodTranslateClient('your-api-key');

// Upload and transcribe
const job = await client.createTranscription({
  audioFilePath: 'episode.mp3',
  podcastId: 'my-podcast',
  episodeId: 'ep-001',
  targetLanguages: ['es', 'fr']
});

// Wait for completion
const result = await client.waitForCompletion(job.job_id);
```

### 3. cURL Examples (`curl_examples.sh`)
Quick command-line examples for testing.

**Usage:**
```bash
./curl_examples.sh
```

## Quick Start

### 1. Get your API key
```bash
# Register and get your API key from the dashboard
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password","name":"John Doe"}'
```

### 2. Upload audio for transcription
```bash
curl -X POST http://localhost:3000/api/v1/transcriptions/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@podcast.mp3" \
  -F "podcast_id=my-podcast" \
  -F "episode_id=ep-001" \
  -F "target_languages=es,fr,de"
```

### 3. Check job status
```bash
curl http://localhost:3000/api/v1/transcriptions/{job_id} \
  -H "X-API-Key: your-api-key"
```

## API Endpoints

### Transcription
- `POST /api/v1/transcriptions/upload` - Upload audio
- `GET /api/v1/transcriptions/{job_id}` - Get job status

### AI Tools
- `POST /api/v1/ai-tools/generate/blog` - Generate blog post
- `POST /api/v1/ai-tools/generate/social` - Generate social media
- `POST /api/v1/ai-tools/generate/show-notes` - Generate show notes
- `POST /api/v1/ai-tools/extract/qa` - Extract Q&A

### Analytics
- `GET /api/v1/analytics/podcasts/{id}` - Get podcast analytics
- `GET /api/v1/analytics/episodes/{id}` - Get episode analytics

### Webhooks
- `POST /api/v1/webhooks` - Register webhook
- `GET /api/v1/webhooks` - List webhooks
- `DELETE /api/v1/webhooks/{id}` - Delete webhook

## Webhook Events

Subscribe to real-time events:

```bash
curl -X POST http://localhost:3000/api/v1/webhooks \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhooks",
    "events": [
      "transcription.completed",
      "translation.completed",
      "distribution.published"
    ],
    "secret": "your-webhook-secret"
  }'
```

### Event Types
- `transcription.started`
- `transcription.completed`
- `transcription.failed`
- `translation.completed`
- `distribution.published`
- `analytics.daily_report`

## Rate Limits

| Tier       | Requests/15min | Jobs/hour | TTS Minutes/month |
|------------|----------------|-----------|-------------------|
| Free       | 100            | 10        | 100               |
| Pro        | 1000           | 100       | 1000              |
| Enterprise | Unlimited      | Unlimited | Unlimited         |

## Authentication

Two methods available:

### 1. JWT Token
```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token in requests
curl -H "Authorization: Bearer {token}" ...
```

### 2. API Key
```bash
# Use API key in header
curl -H "X-API-Key: your-api-key" ...
```

## Error Handling

All errors return JSON with consistent format:

```json
{
  "error": {
    "message": "Error description",
    "status": 400,
    "code": "ERROR_CODE"
  }
}
```

Common error codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Support

- API Documentation: http://localhost:3000/docs
- GitHub Issues: https://github.com/podtranslate/podtranslate/issues
- Email: support@podtranslate.com

## License

MIT
