import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Podcasts from './pages/Podcasts'
import Episodes from './pages/Episodes'
import Analytics from './pages/Analytics'
import Transcriptions from './pages/Transcriptions'
import Distribution from './pages/Distribution'
import Settings from './pages/Settings'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="podcasts" element={<Podcasts />} />
          <Route path="episodes" element={<Episodes />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="transcriptions" element={<Transcriptions />} />
          <Route path="distribution" element={<Distribution />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
