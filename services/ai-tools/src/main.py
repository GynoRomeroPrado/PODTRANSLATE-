"""AI Tools Service - Content repurposing and SEO optimization."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging

from .content.blog_generator import BlogGenerator
from .content.social_media import SocialMediaGenerator
from .seo.show_notes import ShowNotesGenerator
from .engagement.qa_extractor import QAExtractor
from .engagement.highlights import HighlightGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PodTranslate AI Tools",
    version="1.0.0",
    description="AI-powered content generation and optimization"
)

# Initialize services
blog_generator = BlogGenerator()
social_generator = SocialMediaGenerator()
show_notes_generator = ShowNotesGenerator()
qa_extractor = QAExtractor()
highlight_generator = HighlightGenerator()


# Request/Response models
class TranscriptRequest(BaseModel):
    transcript: str
    metadata: Optional[Dict] = {}


class BlogPostRequest(BaseModel):
    transcript: str
    title: str
    style: Optional[str] = "informative"  # informative, casual, professional
    length: Optional[str] = "medium"  # short, medium, long


class SocialMediaRequest(BaseModel):
    transcript: str
    platforms: List[str]  # twitter, linkedin, facebook, instagram
    count: Optional[int] = 5


class ShowNotesRequest(BaseModel):
    transcript: str
    include_timestamps: Optional[bool] = True
    include_keywords: Optional[bool] = True


class QARequest(BaseModel):
    transcript: str
    max_questions: Optional[int] = 10


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-tools",
        "version": "1.0.0"
    }


# Blog post generation
@app.post("/generate/blog")
async def generate_blog_post(request: BlogPostRequest):
    """
    Generate a blog post from podcast transcript.

    Converts spoken content into written blog format with:
    - Proper structure and formatting
    - SEO optimization
    - Engaging headlines
    - Call-to-action
    """
    try:
        logger.info("Generating blog post")

        result = await blog_generator.generate(
            transcript=request.transcript,
            title=request.title,
            style=request.style,
            length=request.length
        )

        return {
            "success": True,
            "blog_post": result
        }

    except Exception as e:
        logger.error(f"Error generating blog post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Social media content
@app.post("/generate/social")
async def generate_social_media(request: SocialMediaRequest):
    """
    Generate social media posts from transcript.

    Creates platform-specific content for:
    - Twitter/X (threads and single tweets)
    - LinkedIn (professional posts)
    - Facebook (engaging updates)
    - Instagram (captions with hashtags)
    """
    try:
        logger.info(f"Generating social media content for {request.platforms}")

        result = await social_generator.generate(
            transcript=request.transcript,
            platforms=request.platforms,
            count=request.count
        )

        return {
            "success": True,
            "social_media": result
        }

    except Exception as e:
        logger.error(f"Error generating social media content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Show notes
@app.post("/generate/show-notes")
async def generate_show_notes(request: ShowNotesRequest):
    """
    Generate SEO-optimized show notes.

    Creates comprehensive show notes with:
    - Episode summary
    - Key takeaways
    - Timestamps for topics
    - Keywords and tags
    - Links and resources mentioned
    """
    try:
        logger.info("Generating show notes")

        result = await show_notes_generator.generate(
            transcript=request.transcript,
            include_timestamps=request.include_timestamps,
            include_keywords=request.include_keywords
        )

        return {
            "success": True,
            "show_notes": result
        }

    except Exception as e:
        logger.error(f"Error generating show notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Q&A extraction
@app.post("/extract/qa")
async def extract_questions_answers(request: QARequest):
    """
    Extract questions and answers from transcript.

    Identifies and extracts:
    - Questions asked during the episode
    - Corresponding answers
    - Context for each Q&A pair
    """
    try:
        logger.info("Extracting Q&A pairs")

        result = await qa_extractor.extract(
            transcript=request.transcript,
            max_questions=request.max_questions
        )

        return {
            "success": True,
            "qa_pairs": result
        }

    except Exception as e:
        logger.error(f"Error extracting Q&A: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Highlight generation
@app.post("/extract/highlights")
async def extract_highlights(request: TranscriptRequest):
    """
    Extract key highlights and quotable moments.

    Identifies:
    - Most engaging moments
    - Quotable snippets
    - Key insights
    - Timestamps for each highlight
    """
    try:
        logger.info("Extracting highlights")

        result = await highlight_generator.generate(
            transcript=request.transcript
        )

        return {
            "success": True,
            "highlights": result
        }

    except Exception as e:
        logger.error(f"Error extracting highlights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Newsletter generation
@app.post("/generate/newsletter")
async def generate_newsletter(request: TranscriptRequest):
    """
    Generate email newsletter from episode.

    Creates newsletter with:
    - Catchy subject line
    - Episode summary
    - Key points
    - Call-to-action
    """
    try:
        logger.info("Generating newsletter")

        # Use blog generator with newsletter style
        result = await blog_generator.generate(
            transcript=request.transcript,
            title=request.metadata.get('title', 'Latest Episode'),
            style='newsletter',
            length='medium'
        )

        return {
            "success": True,
            "newsletter": result
        }

    except Exception as e:
        logger.error(f"Error generating newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SEO keywords extraction
@app.post("/seo/keywords")
async def extract_keywords(request: TranscriptRequest):
    """
    Extract SEO keywords from transcript.

    Identifies:
    - Primary keywords
    - Secondary keywords
    - Long-tail keywords
    - Related topics
    """
    try:
        logger.info("Extracting SEO keywords")

        result = await show_notes_generator.extract_keywords(
            transcript=request.transcript
        )

        return {
            "success": True,
            "keywords": result
        }

    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Title suggestions
@app.post("/generate/titles")
async def generate_titles(request: TranscriptRequest):
    """
    Generate engaging title suggestions.

    Creates multiple title options optimized for:
    - SEO
    - Click-through rate
    - Social sharing
    - Different platforms
    """
    try:
        logger.info("Generating title suggestions")

        result = await blog_generator.generate_titles(
            transcript=request.transcript,
            count=10
        )

        return {
            "success": True,
            "titles": result
        }

    except Exception as e:
        logger.error(f"Error generating titles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3004)
