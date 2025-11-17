export default {
  testEnvironment: 'node',
  transform: {},
  testMatch: ['**/*.test.js'],
  collectCoverageFrom: [
    '../../services/**/*.{js,py}',
    '!**/node_modules/**',
    '!**/venv/**'
  ],
  coverageDirectory: './coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['./setup.js'],
  testTimeout: 60000, // 60 seconds for integration tests
  maxWorkers: 1 // Run tests sequentially
}
