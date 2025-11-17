import { describe, test, expect } from '@jest/globals'
import axios from 'axios'
import { faker } from '@faker-js/faker'

const API_URL = global.API_BASE_URL

describe('Authentication API', () => {
  let testUser
  let authToken

  test('POST /auth/register - should register a new user', async () => {
    testUser = {
      email: faker.internet.email(),
      password: faker.internet.password({ length: 12 }),
      name: faker.person.fullName()
    }

    const response = await axios.post(`${API_URL}/auth/register`, testUser)

    expect(response.status).toBe(201)
    expect(response.data).toHaveProperty('user')
    expect(response.data).toHaveProperty('token')
    expect(response.data.user.email).toBe(testUser.email)
    expect(response.data.user.name).toBe(testUser.name)
    expect(response.data.user).not.toHaveProperty('password')
  })

  test('POST /auth/register - should reject duplicate email', async () => {
    try {
      await axios.post(`${API_URL}/auth/register`, testUser)
      fail('Should have thrown an error')
    } catch (error) {
      expect(error.response.status).toBe(400)
      expect(error.response.data.error).toContain('already exists')
    }
  })

  test('POST /auth/login - should login with correct credentials', async () => {
    const response = await axios.post(`${API_URL}/auth/login`, {
      email: testUser.email,
      password: testUser.password
    })

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('user')
    expect(response.data).toHaveProperty('token')

    authToken = response.data.token
  })

  test('POST /auth/login - should reject invalid credentials', async () => {
    try {
      await axios.post(`${API_URL}/auth/login`, {
        email: testUser.email,
        password: 'wrongpassword'
      })
      fail('Should have thrown an error')
    } catch (error) {
      expect(error.response.status).toBe(401)
    }
  })

  test('GET /auth/me - should return current user with valid token', async () => {
    const response = await axios.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${authToken}` }
    })

    expect(response.status).toBe(200)
    expect(response.data.user.email).toBe(testUser.email)
  })

  test('GET /auth/me - should reject invalid token', async () => {
    try {
      await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: 'Bearer invalid-token' }
      })
      fail('Should have thrown an error')
    } catch (error) {
      expect(error.response.status).toBe(401)
    }
  })
})
