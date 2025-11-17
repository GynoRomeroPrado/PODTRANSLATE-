# PodTranslate E2E Tests

Comprehensive end-to-end integration tests for the PodTranslate platform.

## Test Coverage

### API Tests
- **Authentication**: Registration, login, token validation
- **Podcasts**: CRUD operations
- **Episodes**: CRUD operations
- **Transcriptions**: Upload, status checking
- **AI Tools**: Blog generation, social media, show notes, Q&A extraction
- **Analytics**: Event tracking, metrics retrieval
- **Distribution**: Platform publishing
- **Webhooks**: Registration, delivery

### Integration Tests
- **Complete Workflow**: End-to-end transcription pipeline
- **Multi-Service**: Cross-service communication
- **Data Consistency**: Database integrity checks

## Prerequisites

- Node.js 18+
- Docker and Docker Compose (for local testing)
- Running PodTranslate services

## Installation

```bash
cd tests/e2e
npm install
```

## Running Tests

### Start Services

```bash
# From project root
docker-compose up -d
```

### Run All Tests

```bash
npm test
```

### Run Specific Test Suites

```bash
# API tests only
npm run test:api

# Integration tests only
npm run test:integration

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage
```

### Environment Variables

Create `.env` file:

```env
API_BASE_URL=http://localhost:3000/api/v1
TEST_TIMEOUT=60000
```

## Test Structure

```
tests/e2e/
├── api/                    # API endpoint tests
│   ├── auth.test.js
│   ├── podcasts.test.js
│   ├── episodes.test.js
│   └── transcriptions.test.js
├── integration/            # Integration tests
│   ├── transcription-workflow.test.js
│   ├── ai-tools.test.js
│   ├── analytics.test.js
│   └── distribution.test.js
├── setup.js               # Test setup and utilities
├── package.json
└── jest.config.js
```

## Writing Tests

### Example Test

```javascript
import { describe, test, expect } from '@jest/globals'
import axios from 'axios'

const API_URL = global.API_BASE_URL

describe('Feature', () => {
  test('should do something', async () => {
    const response = await axios.get(`${API_URL}/endpoint`)

    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('field')
  })
})
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Clean up test data after tests
3. **Timeouts**: Set appropriate timeouts for async operations
4. **Assertions**: Use clear, specific assertions
5. **Error Cases**: Test both success and failure scenarios

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7
      rabbitmq:
        image: rabbitmq:3

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Start services
        run: docker-compose up -d

      - name: Install dependencies
        run: |
          cd tests/e2e
          npm install

      - name: Run E2E tests
        run: |
          cd tests/e2e
          npm test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./tests/e2e/coverage/lcov.info
```

## Test Data

Tests use `@faker-js/faker` for generating random test data:

```javascript
import { faker } from '@faker-js/faker'

const testUser = {
  email: faker.internet.email(),
  password: faker.internet.password({ length: 12 }),
  name: faker.person.fullName()
}
```

## Debugging

### Verbose Output

```bash
npm test -- --verbose
```

### Run Single Test

```bash
npm test -- auth.test.js
```

### Debug Mode

```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

## Performance

- Tests run sequentially (--runInBand) to avoid conflicts
- Total execution time: ~5-10 minutes
- Individual test timeout: 60 seconds

## Monitoring

Test results can be integrated with:
- **SonarQube**: Code quality and coverage
- **Datadog**: Test execution metrics
- **Slack**: Test failure notifications

## Troubleshooting

### Services Not Ready

```bash
# Check service health
curl http://localhost:3000/api/v1/health

# View service logs
docker-compose logs -f api-gateway
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Test Failures

1. Check service logs
2. Verify environment variables
3. Ensure services are running
4. Check network connectivity

## License

MIT
