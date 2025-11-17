#!/bin/bash

# Quick usage examples for PodTranslate API

BASE_URL="http://localhost:3000/api/v1"
API_KEY="your-api-key-here"

echo "🎙️ PodTranslate API Examples"
echo "============================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check"
curl -s "$BASE_URL/health" | jq
echo ""

# 2. Upload and Transcribe
echo "2️⃣ Upload Audio for Transcription"
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/transcriptions/upload" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@podcast_episode.mp3" \
  -F "podcast_id=my-podcast" \
  -F "episode_id=episode-001" \
  -F "source_language=en" \
  -F "target_languages=es,fr" \
  -F "enable_diarization=true" \
  -F "enable_translation=true")

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"
echo ""

# 3. Check Job Status
echo "3️⃣ Check Transcription Status"
curl -s "$BASE_URL/transcriptions/$JOB_ID" \
  -H "X-API-Key: $API_KEY" | jq
echo ""

# 4. Generate Blog Post
echo "4️⃣ Generate Blog Post"
curl -s -X POST "$BASE_URL/ai-tools/generate/blog" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Welcome to our podcast about technology...",
    "title": "Amazing Tech Discussion",
    "style": "informative",
    "length": "medium"
  }' | jq '.blog_post.metadata'
echo ""

# 5. Generate Social Media Posts
echo "5️⃣ Generate Social Media Posts"
curl -s -X POST "$BASE_URL/ai-tools/generate/social" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Welcome to our podcast...",
    "platforms": ["twitter", "linkedin"],
    "count": 3
  }' | jq '.social_media'
echo ""

# 6. Get Analytics
echo "6️⃣ Get Podcast Analytics"
curl -s "$BASE_URL/analytics/podcasts/my-podcast?start_date=2024-01-01&end_date=2024-01-31" \
  -H "X-API-Key: $API_KEY" | jq '.metrics.downloads'
echo ""

# 7. Register Webhook
echo "7️⃣ Register Webhook"
curl -s -X POST "$BASE_URL/webhooks" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://myapp.com/webhooks/podtranslate",
    "events": ["transcription.completed", "translation.completed"],
    "secret": "my-webhook-secret"
  }' | jq
echo ""

echo "✅ Examples completed!"
echo ""
echo "📚 For more information, visit http://localhost:3000/docs"
