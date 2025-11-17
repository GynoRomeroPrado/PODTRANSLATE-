# PodTranslate Dashboard

Modern React admin dashboard for the PodTranslate platform with real-time analytics and management features.

## Features

- **Dashboard**: Overview with key metrics and visualizations
- **Podcasts**: Manage podcast shows
- **Episodes**: Track and manage episodes
- **Transcriptions**: Monitor transcription and translation jobs
- **Distribution**: Multi-platform publishing management
- **Analytics**: Detailed performance insights with charts
- **Settings**: Account, API keys, and preferences

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first styling
- **React Router**: Client-side routing
- **TanStack Query**: Data fetching and caching
- **Zustand**: State management
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **React Hook Form**: Form management

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd dashboard
npm install
```

### Development

```bash
npm run dev
```

Dashboard will be available at http://localhost:5173

### Build

```bash
npm run build
```

Build output in `dist/` directory.

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:3000/api/v1
```

## Project Structure

```
dashboard/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable components
│   │   └── Layout.jsx   # Main layout with sidebar
│   ├── lib/             # Utilities and API client
│   │   ├── api.js       # API methods
│   │   └── utils.js     # Helper functions
│   ├── pages/           # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Podcasts.jsx
│   │   ├── Episodes.jsx
│   │   ├── Transcriptions.jsx
│   │   ├── Distribution.jsx
│   │   ├── Analytics.jsx
│   │   └── Settings.jsx
│   ├── stores/          # Zustand stores
│   │   └── authStore.js
│   ├── App.jsx          # App component with routes
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## API Integration

The dashboard integrates with PodTranslate API:

- `/api/v1/auth/*` - Authentication
- `/api/v1/podcasts/*` - Podcast management
- `/api/v1/episodes/*` - Episode management
- `/api/v1/transcriptions/*` - Transcription jobs
- `/api/v1/distribution/*` - Distribution management
- `/api/v1/analytics/*` - Analytics data

## Authentication

The dashboard uses JWT authentication:

1. Login with email/password
2. Token stored in localStorage via Zustand
3. Token sent in Authorization header
4. Auto-redirect to login on 401

Demo credentials:
- Email: `admin@podtranslate.com`
- Password: `password`

## Features

### Dashboard
- Key metrics cards
- Downloads trend chart
- Language distribution pie chart
- Recent transcription jobs table

### Analytics
- Time series charts
- Geographic distribution
- Language performance
- Custom date ranges
- Podcast filtering

### Transcriptions
- Real-time job status
- Progress tracking
- Multi-language support
- Upload interface

### Distribution
- Platform connections
- Publishing status
- Multi-language distribution
- Platform-specific icons

## Deployment

### Docker

```bash
# Build
docker build -t podtranslate-dashboard .

# Run
docker run -p 80:80 podtranslate-dashboard
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboard
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: dashboard
        image: podtranslate/dashboard:latest
        ports:
        - containerPort: 80
```

## License

MIT
