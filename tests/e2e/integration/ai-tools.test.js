import { describe, test, expect, beforeAll } from '@jest/globals'
import axios from 'axios'
import { faker } from '@faker-js/faker'

const API_URL = global.API_BASE_URL

describe('AI Tools Integration', () => {
  let authToken

  beforeAll(async () => {
    const user = {
      email: faker.internet.email(),
      password: faker.internet.password({ length: 12 }),
      name: faker.person.fullName()
    }

    await axios.post(`${API_URL}/auth/register`, user)
    const loginResponse = await axios.post(`${API_URL}/auth/login`, {
      email: user.email,
      password: user.password
    })

    authToken = loginResponse.data.token
  })

  const sampleTranscript = `
    Welcome to our podcast. Today we're discussing the future of artificial intelligence
    and how it's transforming various industries. Our guest is Dr. Jane Smith,
    an AI researcher at MIT. Let's dive into the conversation.
  `

  test('POST /ai-tools/generate/blog - should generate blog post', async () => {
    const response = await axios.post(
      `${API_URL}/ai-tools/generate/blog`,
      {
        transcript: sampleTranscript,
        title: 'The Future of AI',
        style: 'informative',
        length: 'medium'
      },
      {
        headers: { Authorization: `Bearer ${authToken}` }
      }
    )

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('blog_post')
    expect(response.data.blog_post).toHaveProperty('content')
    expect(response.data.blog_post).toHaveProperty('metadata')
    expect(response.data.blog_post.metadata).toHaveProperty('word_count')
  }, 30000)

  test('POST /ai-tools/generate/social - should generate social media posts', async () => {
    const response = await axios.post(
      `${API_URL}/ai-tools/generate/social`,
      {
        transcript: sampleTranscript,
        platforms: ['twitter', 'linkedin'],
        count: 3
      },
      {
        headers: { Authorization: `Bearer ${authToken}` }
      }
    )

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('social_media')
    expect(response.data.social_media).toHaveProperty('twitter')
    expect(response.data.social_media).toHaveProperty('linkedin')
    expect(Array.isArray(response.data.social_media.twitter)).toBe(true)
    expect(response.data.social_media.twitter.length).toBe(3)
  }, 30000)

  test('POST /ai-tools/generate/show-notes - should generate show notes', async () => {
    const response = await axios.post(
      `${API_URL}/ai-tools/generate/show-notes`,
      {
        transcript: sampleTranscript,
        include_timestamps: true,
        include_links: true
      },
      {
        headers: { Authorization: `Bearer ${authToken}` }
      }
    )

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('show_notes')
    expect(response.data.show_notes).toHaveProperty('summary')
    expect(response.data.show_notes).toHaveProperty('key_points')
    expect(Array.isArray(response.data.show_notes.key_points)).toBe(true)
  }, 30000)

  test('POST /ai-tools/extract/qa - should extract Q&A', async () => {
    const response = await axios.post(
      `${API_URL}/ai-tools/extract/qa`,
      {
        transcript: sampleTranscript,
        max_questions: 5
      },
      {
        headers: { Authorization: `Bearer ${authToken}` }
      }
    )

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('questions')
    expect(Array.isArray(response.data.questions)).toBe(true)

    if (response.data.questions.length > 0) {
      expect(response.data.questions[0]).toHaveProperty('question')
      expect(response.data.questions[0]).toHaveProperty('answer')
    }
  }, 30000)
})
