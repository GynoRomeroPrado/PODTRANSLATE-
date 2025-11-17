# Contributing to PodTranslate

Thank you for your interest in contributing to PodTranslate! This document provides guidelines and instructions for contributing.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Git
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- A GitHub account

### Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/PODTRANSLATE-.git
cd PODTRANSLATE-

# Add upstream remote
git remote add upstream https://github.com/podtranslate/PODTRANSLATE-.git
```

### Local Setup
```bash
# Copy environment file
cp .env.example .env

# Add your API keys to .env

# Start services
docker-compose up -d

# Install dependencies
cd services/audio-processing
pip install -r requirements.txt
pip install -r requirements-dev.txt

cd ../api-gateway
npm install
```

## Development Workflow

### 1. Create a Branch
```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation

### 3. Commit Changes
```bash
# Stage changes
git add .

# Commit with a descriptive message
git commit -m "feat: add speaker identification to transcription

- Implement speaker diarization using pyannote
- Add speaker labels to transcription segments
- Update API to include speaker information"
```

### Commit Message Format
Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(transcription): add language detection
fix(api): resolve CORS issue for mobile clients
docs(readme): update installation instructions
test(translation): add unit tests for GPT-4 integration
```

### 4. Push Changes
```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request
- Go to GitHub and create a Pull Request
- Fill out the PR template
- Link related issues
- Wait for review

## Coding Standards

### Python (Audio Processing, Analytics, AI Tools)

**Style Guide:** PEP 8

```python
# Good
def transcribe_audio(audio_path: str, language: Optional[str] = None) -> Dict:
    """
    Transcribe audio file using Whisper.

    Args:
        audio_path: Path to the audio file
        language: Optional language code

    Returns:
        Transcription result dictionary
    """
    logger.info(f"Transcribing audio: {audio_path}")
    # Implementation
    return result
```

**Tools:**
- Linting: `black` + `flake8`
- Type checking: `mypy`
- Testing: `pytest`

```bash
# Format code
black src/

# Lint
flake8 src/

# Type check
mypy src/

# Run tests
pytest
```

### JavaScript/Node.js (API Gateway, Distribution)

**Style Guide:** Airbnb JavaScript Style Guide

```javascript
// Good
/**
 * Create a new transcription job
 * @param {Object} options - Transcription options
 * @param {string} options.episodeId - Episode ID
 * @param {string[]} options.targetLanguages - Target languages
 * @returns {Promise<Object>} Job details
 */
async function createTranscriptionJob({ episodeId, targetLanguages }) {
  logger.info(`Creating transcription job for episode: ${episodeId}`);
  // Implementation
  return job;
}
```

**Tools:**
- Linting: `eslint`
- Formatting: `prettier`
- Testing: `jest`

```bash
# Lint
npm run lint

# Format
npm run format

# Run tests
npm test
```

## Testing

### Unit Tests
Write unit tests for all new functionality.

**Python Example:**
```python
# tests/test_transcription.py
import pytest
from src.transcription import WhisperService

def test_transcribe_audio():
    service = WhisperService()
    result = service.transcribe("test_audio.wav")

    assert result is not None
    assert "text" in result
    assert "language" in result
```

**JavaScript Example:**
```javascript
// tests/api.test.js
const request = require('supertest');
const app = require('../src/index');

describe('GET /api/v1/health', () => {
  it('should return healthy status', async () => {
    const res = await request(app).get('/api/v1/health');

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('healthy');
  });
});
```

### Integration Tests
Test interactions between services.

```python
def test_transcription_pipeline():
    # Upload audio
    job = create_transcription_job(audio_url="...")

    # Wait for completion
    wait_for_job_completion(job.id)

    # Verify results
    result = get_transcription(job.id)
    assert result.status == "completed"
```

### Running Tests
```bash
# Python tests
cd services/audio-processing
pytest

# JavaScript tests
cd services/api-gateway
npm test

# All tests with coverage
npm run test:coverage
```

## Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process
1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

### After Merge
- Delete your feature branch
- Update your local repository
```bash
git checkout main
git pull upstream main
git branch -d feature/your-feature-name
```

## Areas for Contribution

### High Priority
- [ ] Complete distribution service implementations
- [ ] Add comprehensive test coverage
- [ ] Improve error handling and logging
- [ ] Performance optimizations
- [ ] Security enhancements

### Features
- [ ] Real-time transcription (WebSocket)
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Voice cloning for TTS
- [ ] Video generation from audio

### Documentation
- [ ] API examples in more languages
- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] Best practices guide

### Infrastructure
- [ ] Kubernetes Helm charts
- [ ] Terraform modules
- [ ] CI/CD pipeline improvements
- [ ] Monitoring dashboards

## Questions?

- Open an issue for bugs or feature requests
- Join our Discord: [link]
- Email: developers@podtranslate.com

Thank you for contributing to PodTranslate! 🎙️
