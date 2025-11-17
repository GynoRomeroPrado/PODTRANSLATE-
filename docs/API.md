# PodTranslate API Documentation

## Base URL
```
Production: https://api.podtranslate.com/api/v1
Development: http://localhost:3000/api/v1
```

## Authentication

All API requests require authentication using either:

### JWT Token (User Authentication)
```bash
Authorization: Bearer <jwt_token>
```

### API Key (Programmatic Access)
```bash
X-API-Key: <api_key>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Podcasts

#### Create Podcast
```http
POST /podcasts
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Awesome Podcast",
  "description": "A podcast about technology",
  "language": "en",
  "category": "Technology",
  "coverImageUrl": "https://example.com/cover.jpg"
}
```

#### Get All Podcasts
```http
GET /podcasts
Authorization: Bearer <token>
```

**Response:**
```json
{
  "podcasts": [
    {
      "id": "podcast_123",
      "title": "My Awesome Podcast",
      "description": "A podcast about technology",
      "language": "en",
      "episodeCount": 10,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Get Podcast by ID
```http
GET /podcasts/:id
Authorization: Bearer <token>
```

#### Update Podcast
```http
PUT /podcasts/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Podcast Title",
  "description": "Updated description"
}
```

#### Delete Podcast
```http
DELETE /podcasts/:id
Authorization: Bearer <token>
```

### Episodes

#### Create Episode
```http
POST /episodes
Authorization: Bearer <token>
Content-Type: application/json

{
  "podcastId": "podcast_123",
  "title": "Episode 1: Introduction",
  "description": "Our first episode",
  "audioUrl": "https://example.com/episode1.mp3",
  "durationSeconds": 3600
}
```

#### Upload Episode Audio
```http
POST /episodes/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <audio_file>
podcastId: podcast_123
title: Episode 1
description: Our first episode
```

### Transcriptions

#### Create Transcription Job
```http
POST /transcriptions
Authorization: Bearer <token>
Content-Type: application/json

{
  "episodeId": "episode_123",
  "sourceLanguage": "en",
  "targetLanguages": ["es", "fr", "de"],
  "enableDiarization": true,
  "enableTranslation": true,
  "enableTts": false
}
```

**Response:**
```json
{
  "jobId": "job_abc123",
  "status": "queued",
  "message": "Transcription job created successfully"
}
```

#### Get Transcription Job Status
```http
GET /transcriptions/:jobId
Authorization: Bearer <token>
```

**Response:**
```json
{
  "jobId": "job_abc123",
  "status": "completed",
  "progress": 100,
  "currentStep": "completed",
  "transcriptionUrl": "https://cdn.podtranslate.com/transcripts/...",
  "translations": {
    "es": "https://cdn.podtranslate.com/transcripts/.../es.json",
    "fr": "https://cdn.podtranslate.com/transcripts/.../fr.json",
    "de": "https://cdn.podtranslate.com/transcripts/.../de.json"
  },
  "audioUrls": null
}
```

### Distributions

#### Create Distribution
```http
POST /distributions
Authorization: Bearer <token>
Content-Type: application/json

{
  "episodeId": "episode_123",
  "platforms": ["spotify", "apple", "google"],
  "languages": ["en", "es", "fr"]
}
```

**Response:**
```json
{
  "distributionId": "dist_xyz789",
  "status": "pending",
  "platforms": {
    "spotify": "pending",
    "apple": "pending",
    "google": "pending"
  }
}
```

#### Get Distribution Status
```http
GET /distributions/:id
Authorization: Bearer <token>
```

### Analytics

#### Get Podcast Analytics
```http
GET /analytics/podcasts/:id
Authorization: Bearer <token>
Query Parameters:
  - startDate: ISO date string
  - endDate: ISO date string
  - metrics: downloads,completions,engagement
  - groupBy: day,week,month
```

**Response:**
```json
{
  "podcastId": "podcast_123",
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": {
    "downloads": {
      "total": 10000,
      "byLanguage": {
        "en": 6000,
        "es": 2500,
        "fr": 1500
      },
      "byRegion": {
        "US": 5000,
        "ES": 2000,
        "FR": 1500,
        "other": 1500
      }
    },
    "engagement": {
      "averageCompletionRate": 0.75,
      "averageListenTime": 2700
    }
  }
}
```

#### Get Episode Analytics
```http
GET /analytics/episodes/:id
Authorization: Bearer <token>
```

## Rate Limits

| Tier       | Requests/15min | Transcription Jobs/hour | TTS Minutes/month |
|------------|----------------|-------------------------|-------------------|
| Free       | 100            | 10                      | 100               |
| Pro        | 1000           | 100                     | 1000              |
| Enterprise | Unlimited      | Unlimited               | Unlimited         |

## Error Codes

| Code | Description              | Example                          |
|------|--------------------------|----------------------------------|
| 400  | Bad Request              | Invalid request parameters       |
| 401  | Unauthorized             | Missing or invalid token         |
| 403  | Forbidden                | Insufficient permissions         |
| 404  | Not Found                | Resource not found               |
| 429  | Too Many Requests        | Rate limit exceeded              |
| 500  | Internal Server Error    | Server-side error                |
| 503  | Service Unavailable      | Service temporarily unavailable  |

## Webhooks

Configure webhooks to receive real-time updates:

### Webhook Events

- `transcription.completed` - Transcription job completed
- `transcription.failed` - Transcription job failed
- `distribution.published` - Episode published to platform
- `analytics.daily_report` - Daily analytics summary

### Webhook Payload Example

```json
{
  "event": "transcription.completed",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "jobId": "job_abc123",
    "episodeId": "episode_123",
    "status": "completed",
    "languages": ["en", "es", "fr"],
    "transcriptionUrls": {
      "en": "https://...",
      "es": "https://...",
      "fr": "https://..."
    }
  }
}
```

## SDKs

Official SDKs are available for:

- JavaScript/TypeScript: `npm install @podtranslate/sdk`
- Python: `pip install podtranslate`
- Go: `go get github.com/podtranslate/go-sdk`

### Example Usage (JavaScript)

```javascript
const PodTranslate = require('@podtranslate/sdk');

const client = new PodTranslate({
  apiKey: 'your_api_key'
});

// Create transcription job
const job = await client.transcriptions.create({
  episodeId: 'episode_123',
  targetLanguages: ['es', 'fr']
});

// Check status
const status = await client.transcriptions.get(job.jobId);
console.log(status);
```

## Support

- Documentation: https://docs.podtranslate.com
- API Status: https://status.podtranslate.com
- Support: support@podtranslate.com
