import { beforeAll, afterAll } from '@jest/globals'

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000/api/v1'
const TEST_TIMEOUT = 60000

beforeAll(async () => {
  console.log('🚀 Starting E2E tests...')
  console.log(`API Base URL: ${API_BASE_URL}`)

  // Wait for services to be ready
  await waitForServices()
}, TEST_TIMEOUT)

afterAll(async () => {
  console.log('✅ E2E tests completed')
})

async function waitForServices() {
  const maxRetries = 30
  const retryDelay = 2000

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      if (response.ok) {
        console.log('✓ Services are ready')
        return
      }
    } catch (error) {
      if (i < maxRetries - 1) {
        console.log(`Waiting for services... (${i + 1}/${maxRetries})`)
        await new Promise(resolve => setTimeout(resolve, retryDelay))
      }
    }
  }

  throw new Error('Services failed to start in time')
}

// Global test configuration
global.API_BASE_URL = API_BASE_URL
global.TEST_TIMEOUT = TEST_TIMEOUT
