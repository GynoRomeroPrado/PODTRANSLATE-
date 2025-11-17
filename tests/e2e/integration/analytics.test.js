import { describe, test, expect, beforeAll } from '@jest/globals'
import axios from 'axios'
import { faker } from '@faker-js/faker'

const API_URL = global.API_BASE_URL

describe('Analytics Integration', () => {
  let authToken
  let podcastId

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

    // Create a test podcast
    const podcast = await axios.post(
      `${API_URL}/podcasts`,
      {
        title: 'Analytics Test Podcast',
        description: 'Test',
        language: 'en'
      },
      {
        headers: { Authorization: `Bearer ${authToken}` }
      }
    )

    podcastId = podcast.data.podcast.id
  })

  test('POST /analytics/track - should track an event', async () => {
    const event = {
      event_type: 'download',
      podcast_id: podcastId,
      language: 'en',
      metadata: {
        country: 'US',
        platform: 'web'
      }
    }

    const response = await axios.post(`${API_URL}/analytics/track`, event, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(201)
    expect(response.data).toHaveProperty('success', true)
  })

  test('GET /analytics/podcasts/:id - should get podcast analytics', async () => {
    const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    const endDate = new Date().toISOString().split('T')[0]

    const response = await axios.get(
      `${API_URL}/analytics/podcasts/${podcastId}?start_date=${startDate}&end_date=${endDate}`,
      {
        headers: { Authorization: `Bearer ${authToken}` }
      }
    )

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('metrics')
    expect(response.data.metrics).toHaveProperty('downloads')
    expect(response.data.metrics).toHaveProperty('plays')
  })

  test('GET /analytics/overview - should get overview analytics', async () => {
    const response = await axios.get(`${API_URL}/analytics/overview`, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('podcasts')
    expect(response.data).toHaveProperty('episodes')
    expect(response.data).toHaveProperty('total_downloads')
  })
})
