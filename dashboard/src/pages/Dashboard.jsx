import { useQuery } from '@tanstack/react-query'
import {
  Podcast,
  FileAudio,
  Radio,
  TrendingUp,
  Globe,
  Users,
  Clock,
  ArrowUp
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { analyticsApi } from '../lib/api'
import { formatNumber, formatDate } from '../lib/utils'

const StatCard = ({ icon: Icon, title, value, change, color = 'primary' }) => (
  <div className="card">
    <div className="flex items-center justify-between mb-4">
      <div className={`w-12 h-12 rounded-lg bg-${color}-100 flex items-center justify-center`}>
        <Icon className={`text-${color}-600`} size={24} />
      </div>
      {change && (
        <div className={`flex items-center gap-1 text-sm ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
          <ArrowUp size={16} className={change < 0 ? 'rotate-180' : ''} />
          <span>{Math.abs(change)}%</span>
        </div>
      )}
    </div>
    <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
    <p className="text-sm text-gray-500 mt-1">{title}</p>
  </div>
)

export default function Dashboard() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.overview({
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end_date: new Date().toISOString().split('T')[0]
    }).then(res => res.data),
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  // Mock data for demo
  const stats = [
    { icon: Podcast, title: 'Total Podcasts', value: formatNumber(analytics?.podcasts || 24), change: 12, color: 'primary' },
    { icon: FileAudio, title: 'Episodes', value: formatNumber(analytics?.episodes || 187), change: 8, color: 'blue' },
    { icon: Radio, title: 'Transcriptions', value: formatNumber(analytics?.transcriptions || 143), change: 15, color: 'purple' },
    { icon: Globe, title: 'Languages', value: analytics?.languages || 12, change: 3, color: 'green' },
  ]

  const downloadsData = [
    { date: '2024-01-01', downloads: 1200 },
    { date: '2024-01-08', downloads: 1900 },
    { date: '2024-01-15', downloads: 1500 },
    { date: '2024-01-22', downloads: 2300 },
    { date: '2024-01-29', downloads: 2800 },
  ]

  const languageData = [
    { name: 'English', value: 45, color: '#0ea5e9' },
    { name: 'Spanish', value: 25, color: '#8b5cf6' },
    { name: 'French', value: 15, color: '#10b981' },
    { name: 'German', value: 10, color: '#f59e0b' },
    { name: 'Other', value: 5, color: '#6b7280' },
  ]

  const recentJobs = [
    { id: '1', episode: 'Tech Talk #42', status: 'completed', language: 'ES', time: '2 min ago' },
    { id: '2', episode: 'Startup Stories #15', status: 'processing', language: 'FR', time: '5 min ago' },
    { id: '3', episode: 'Health Matters #8', status: 'completed', language: 'DE', time: '12 min ago' },
    { id: '4', episode: 'Music Insights #23', status: 'queued', language: 'IT', time: '15 min ago' },
  ]

  const statusColor = {
    completed: 'bg-green-100 text-green-700',
    processing: 'bg-blue-100 text-blue-700',
    queued: 'bg-gray-100 text-gray-700',
    failed: 'bg-red-100 text-red-700'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your podcast analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Downloads Trend */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Downloads Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={downloadsData}>
              <defs>
                <linearGradient id="colorDownloads" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                stroke="#999"
              />
              <YAxis stroke="#999" />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="downloads"
                stroke="#0ea5e9"
                fillOpacity={1}
                fill="url(#colorDownloads)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Language Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Languages</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={languageData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {languageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {languageData.map((lang, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: lang.color }} />
                  <span className="text-sm text-gray-600">{lang.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{lang.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Transcription Jobs</h3>
          <a href="/transcriptions" className="text-sm text-primary-600 hover:text-primary-700">
            View all
          </a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Episode</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Language</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Time</th>
              </tr>
            </thead>
            <tbody>
              {recentJobs.map((job) => (
                <tr key={job.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm text-gray-900">{job.episode}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor[job.status]}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">{job.language}</td>
                  <td className="py-3 px-4 text-sm text-gray-500">{job.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
