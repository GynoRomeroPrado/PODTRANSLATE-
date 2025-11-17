import { describe, test, expect, beforeAll } from '@jest/globals'
import axios from 'axios'
import FormData from 'form-data'
import fs from 'fs'
import path from 'path'
import { faker } from '@faker-js/faker'

const API_URL = global.API_BASE_URL

describe('Complete Transcription Workflow', () => {
  let authToken
  let podcastId
  let episodeId
  let jobId

  beforeAll(async () => {
    // Register and login
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

  test('Step 1: Create a podcast', async () => {
    const podcast = {
      title: 'Test Podcast',
      description: 'A test podcast for E2E testing',
      language: 'en',
      category: 'Technology'
    }

    const response = await axios.post(`${API_URL}/podcasts`, podcast, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(201)
    expect(response.data.podcast).toHaveProperty('id')
    expect(response.data.podcast.title).toBe(podcast.title)

    podcastId = response.data.podcast.id
  })

  test('Step 2: Create an episode', async () => {
    const episode = {
      podcast_id: podcastId,
      title: 'Test Episode 1',
      description: 'First test episode',
      audio_url: 'https://example.com/audio.mp3'
    }

    const response = await axios.post(`${API_URL}/episodes`, episode, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(201)
    expect(response.data.episode).toHaveProperty('id')

    episodeId = response.data.episode.id
  })

  test('Step 3: Upload audio for transcription', async () => {
    const form = new FormData()

    // Create a dummy audio file for testing
    const testAudioPath = '/tmp/test-audio.mp3'
    fs.writeFileSync(testAudioPath, 'dummy audio content')

    form.append('file', fs.createReadStream(testAudioPath))
    form.append('podcast_id', podcastId)
    form.append('episode_id', episodeId)
    form.append('source_language', 'en')
    form.append('target_languages', 'es,fr')
    form.append('enable_diarization', 'true')
    form.append('enable_translation', 'true')

    const response = await axios.post(`${API_URL}/transcriptions/upload`, form, {
      headers: {
        ...form.getHeaders(),
        Authorization: `Bearer ${authToken}`
      }
    })

    expect(response.status).toBe(202)
    expect(response.data).toHaveProperty('job_id')
    expect(response.data.status).toBe('queued')

    jobId = response.data.job_id

    // Cleanup
    fs.unlinkSync(testAudioPath)
  }, 30000)

  test('Step 4: Check transcription job status', async () => {
    const response = await axios.get(`${API_URL}/transcriptions/${jobId}`, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('job_id', jobId)
    expect(response.data).toHaveProperty('status')
    expect(['queued', 'processing', 'completed', 'failed']).toContain(response.data.status)
  })

  test('Step 5: List all podcasts', async () => {
    const response = await axios.get(`${API_URL}/podcasts`, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(200)
    expect(Array.isArray(response.data.podcasts)).toBe(true)
    expect(response.data.podcasts.length).toBeGreaterThan(0)
    expect(response.data.podcasts.some(p => p.id === podcastId)).toBe(true)
  })

  test('Step 6: Get podcast by ID', async () => {
    const response = await axios.get(`${API_URL}/podcasts/${podcastId}`, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(200)
    expect(response.data.podcast.id).toBe(podcastId)
    expect(response.data.podcast.title).toBe('Test Podcast')
  })

  test('Step 7: List episodes for podcast', async () => {
    const response = await axios.get(`${API_URL}/episodes?podcast_id=${podcastId}`, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(200)
    expect(Array.isArray(response.data.episodes)).toBe(true)
    expect(response.data.episodes.some(e => e.id === episodeId)).toBe(true)
  })
})
