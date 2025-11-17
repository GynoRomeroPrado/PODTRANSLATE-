# PodTranslate Architecture

## Overview

PodTranslate is a microservices-based platform for multi-language podcast transcription, translation, and global distribution.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Node.js)                   │
│                    Port 3000 - REST/GraphQL                  │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
    ┌────────▼─────────┐            ┌────────▼─────────┐
    │  Authentication  │            │   Rate Limiting   │
    │   & Authorization│            │   & Validation    │
    └────────┬─────────┘            └────────┬──────────┘
             │                                │
┌────────────┴────────────────────────────────┴────────────────┐
│                        Service Layer                          │
├───────────────┬──────────────┬──────────────┬────────────────┤
│               │              │              │                │
│   Audio       │ Distribution │  Analytics   │   AI Tools     │
│  Processing   │   Service    │   Service    │   Service      │
│  (Python)     │  (Node.js)   │  (Python)    │   (Python)     │
│  Port 3001    │  Port 3002   │  Port 3003   │   Port 3004    │
└───────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
        │              │              │                │
┌───────▼──────────────▼──────────────▼────────────────▼───────┐
│                    Message Queue Layer                        │
│                  RabbitMQ + Redis (Cache)                     │
└────────────────────────────┬──────────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                       Data Layer                              │
├──────────────────────┬────────────────────────────────────────┤
│   PostgreSQL         │         ClickHouse                     │
│   (Metadata)         │         (Analytics)                    │
└──────────────────────┴────────────────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                      Storage Layer                            │
│                    AWS S3 + CloudFlare CDN                    │
└───────────────────────────────────────────────────────────────┘
```

## Core Services

### 1. API Gateway (Node.js)
**Port:** 3000
**Responsibility:** Main entry point for all client requests

**Features:**
- Request routing to microservices
- Authentication & authorization (JWT)
- Rate limiting & request validation
- API documentation (Swagger/OpenAPI)
- Response caching (Redis)

**Tech Stack:**
- Express.js
- JWT for auth
- Redis for caching
- Swagger for docs

### 2. Audio Processing Service (Python)
**Port:** 3001
**Responsibility:** Audio transcription, translation, and TTS generation

**Features:**
- Audio download and preprocessing
- Noise reduction and normalization
- Speaker diarization (pyannote.audio)
- Multi-language transcription (Whisper)
- Translation (GPT-4 + DeepL)
- Text-to-speech generation (ElevenLabs/Edge TTS)

**Tech Stack:**
- FastAPI
- OpenAI Whisper (large-v3)
- Pyannote.audio for diarization
- GPT-4 for contextual translation
- DeepL API for fast translation
- FFmpeg for audio processing

**Processing Pipeline:**
```
Audio Upload → Preprocessing → Diarization → Transcription → Translation → TTS → Storage
```

### 3. Distribution Service (Node.js)
**Port:** 3002
**Responsibility:** Automatic distribution to podcast platforms

**Features:**
- Spotify for Podcasters integration
- Apple Podcasts Connect integration
- Google Podcasts Manager integration
- YouTube automation
- Multi-language RSS feed generation
- Geo-targeted distribution

**Tech Stack:**
- Node.js
- Platform-specific APIs
- RSS feed generation
- Puppeteer for automation

### 4. Analytics Service (Python)
**Port:** 3003
**Responsibility:** Analytics collection, processing, and reporting

**Features:**
- Real-time metrics collection
- Performance tracking by language/geography
- SEO metrics tracking
- Revenue analytics
- Custom reporting

**Tech Stack:**
- FastAPI
- ClickHouse (time-series analytics)
- Grafana for visualization
- Segment for tracking

### 5. AI Tools Service (Python)
**Port:** 3004
**Responsibility:** AI-powered content generation and optimization

**Features:**
- Blog post generation from transcripts
- Social media content creation
- SEO-optimized show notes
- Q&A extraction
- Growth recommendations

**Tech Stack:**
- FastAPI
- GPT-4 for content generation
- Langchain for workflows
- Vector database for semantic search

## Data Architecture

### PostgreSQL Schema
**Tables:**
- `users` - User accounts
- `podcasts` - Podcast metadata
- `episodes` - Episode information
- `transcription_jobs` - Job tracking
- `transcriptions` - Transcription data
- `distributions` - Platform distribution tracking
- `sponsors` - Sponsor information
- `ad_campaigns` - Ad campaign data
- `subscriptions` - User subscriptions

### ClickHouse Schema
**Tables:**
- `analytics_events` - Real-time event tracking
- `download_metrics` - Download statistics
- `engagement_metrics` - User engagement data
- `revenue_metrics` - Monetization tracking

## Message Queue Architecture

### RabbitMQ Queues

**1. Transcription Queue**
- Job: New episode transcription requests
- Workers: Audio processing service
- Priority: High
- Retry: 3 attempts with exponential backoff

**2. Translation Queue**
- Job: Translation requests
- Workers: Audio processing service
- Priority: Medium
- Parallel processing: Up to 5 languages simultaneously

**3. Distribution Queue**
- Job: Platform distribution requests
- Workers: Distribution service
- Priority: Low
- Rate-limited per platform

**4. Analytics Queue**
- Job: Analytics event processing
- Workers: Analytics service
- Priority: Low
- Batch processing: Every 5 minutes

## Storage Architecture

### S3 Buckets

**1. Audio Files** (`podtranslate-audio`)
```
/uploads/{podcast_id}/{episode_id}/{job_id}/original.mp3
/processed/{podcast_id}/{episode_id}/{job_id}/preprocessed.wav
/tts/{podcast_id}/{episode_id}/{job_id}/{language}.mp3
```

**2. Transcripts** (`podtranslate-transcripts`)
```
/transcripts/{podcast_id}/{episode_id}/{job_id}/original.json
/transcripts/{podcast_id}/{episode_id}/{job_id}/{language}.json
```

**3. Assets** (`podtranslate-assets`)
```
/images/{podcast_id}/cover.jpg
/images/{podcast_id}/episodes/{episode_id}.jpg
```

### CDN (CloudFlare)
- Caches all public assets
- Geo-distributed content delivery
- DDoS protection
- SSL/TLS termination

## Security

### Authentication & Authorization
- JWT-based authentication
- API key support for programmatic access
- Role-based access control (RBAC)
- OAuth 2.0 for platform integrations

### Data Protection
- Encryption at rest (S3)
- Encryption in transit (TLS 1.3)
- GDPR compliance
- SOC 2 Type II compliance (planned)

### Rate Limiting
- API Gateway: 100 requests/15 minutes per IP
- Transcription API: 10 jobs/hour per user (free tier)
- Distribution API: Platform-specific limits

## Monitoring & Observability

### Metrics
- Prometheus for metrics collection
- Grafana for visualization
- Custom dashboards for each service

### Logging
- Structured JSON logging
- Centralized log aggregation
- ELK stack (planned)

### Alerting
- PagerDuty integration
- Slack notifications
- Email alerts

### Health Checks
- `/health` - Liveness probe
- `/ready` - Readiness probe
- Dependency health checks

## Scalability

### Horizontal Scaling
- Stateless services (easy to scale)
- Load balancing with NGINX/HAProxy
- Auto-scaling based on queue depth
- Kubernetes deployment (planned)

### Vertical Scaling
- GPU instances for Whisper transcription
- High-memory instances for analytics

### Performance Optimization
- Redis caching for frequently accessed data
- CDN for static content
- Database query optimization
- Connection pooling

## Disaster Recovery

### Backups
- PostgreSQL: Daily automated backups
- ClickHouse: Incremental backups every 6 hours
- S3: Versioning enabled
- Retention: 30 days

### High Availability
- Multi-AZ deployment
- Database replication
- Message queue clustering
- Automatic failover

## Cost Optimization

### Compute
- Spot instances for batch processing
- Lambda for event-driven tasks
- Auto-scaling to match demand

### Storage
- S3 Intelligent-Tiering
- Lifecycle policies for old data
- CloudFlare for bandwidth savings

### AI APIs
- Batch processing for translations
- Model caching
- Fallback to cheaper alternatives when appropriate

## Future Enhancements

1. **Real-time Transcription**
   - WebSocket support
   - Streaming audio processing
   - Live translation

2. **Advanced Analytics**
   - ML-based predictions
   - Trend analysis
   - Audience segmentation

3. **Mobile Apps**
   - iOS and Android apps
   - Offline access
   - Push notifications

4. **Blockchain Integration**
   - NFT podcast episodes
   - Cryptocurrency payments
   - Decentralized storage

5. **Advanced AI Features**
   - Voice cloning for TTS
   - Automated video generation
   - AI-generated summaries
