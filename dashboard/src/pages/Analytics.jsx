import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'
import { Download, Eye, Share2, MapPin, Calendar } from 'lucide-react'
import { analyticsApi } from '../lib/api'
import { formatNumber } from '../lib/utils'

export default function Analytics() {
  const [dateRange, setDateRange] = useState('30d')
  const [selectedPodcast, setSelectedPodcast] = useState('all')

  const { data: analytics } = useQuery({
    queryKey: ['analytics', selectedPodcast, dateRange],
    queryFn: () => analyticsApi.overview({
      podcast_id: selectedPodcast === 'all' ? undefined : selectedPodcast,
      date_range: dateRange
    }).then(res => res.data),
  })

  // Mock data
  const timeSeriesData = [
    { date: '2024-01-01', downloads: 1200, plays: 980, shares: 145 },
    { date: '2024-01-08', downloads: 1900, plays: 1560, shares: 234 },
    { date: '2024-01-15', downloads: 1500, plays: 1245, shares: 189 },
    { date: '2024-01-22', downloads: 2300, plays: 1890, shares: 312 },
    { date: '2024-01-29', downloads: 2800, plays: 2340, shares: 423 },
  ]

  const geographicData = [
    { country: 'United States', downloads: 4500 },
    { country: 'United Kingdom', downloads: 2300 },
    { country: 'Canada', downloads: 1800 },
    { country: 'Australia', downloads: 1200 },
    { country: 'Germany', downloads: 980 },
  ]

  const languagePerformance = [
    { language: 'English', downloads: 5600, engagement: 85 },
    { language: 'Spanish', downloads: 3200, engagement: 78 },
    { language: 'French', downloads: 1900, engagement: 82 },
    { language: 'German', downloads: 1200, engagement: 76 },
    { language: 'Portuguese', downloads: 890, engagement: 74 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500 mt-1">Detailed performance insights</p>
        </div>
        <div className="flex gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="input w-40"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <select
            value={selectedPodcast}
            onChange={(e) => setSelectedPodcast(e.target.value)}
            className="input w-48"
          >
            <option value="all">All Podcasts</option>
            <option value="1">Tech Talk</option>
            <option value="2">Startup Stories</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <Download className="text-primary-600" size={20} />
            <span className="text-sm font-medium text-gray-500">Total Downloads</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{formatNumber(9700)}</div>
          <div className="text-sm text-green-600 mt-1">+24% vs last period</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <Eye className="text-blue-600" size={20} />
            <span className="text-sm font-medium text-gray-500">Total Plays</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{formatNumber(8015)}</div>
          <div className="text-sm text-green-600 mt-1">+18% vs last period</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <Share2 className="text-purple-600" size={20} />
            <span className="text-sm font-medium text-gray-500">Shares</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{formatNumber(1303)}</div>
          <div className="text-sm text-green-600 mt-1">+31% vs last period</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <MapPin className="text-green-600" size={20} />
            <span className="text-sm font-medium text-gray-500">Countries</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">42</div>
          <div className="text-sm text-green-600 mt-1">+5 new countries</div>
        </div>
      </div>

      {/* Time Series Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Over Time</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              stroke="#999"
            />
            <YAxis stroke="#999" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="downloads" stroke="#0ea5e9" strokeWidth={2} name="Downloads" />
            <Line type="monotone" dataKey="plays" stroke="#8b5cf6" strokeWidth={2} name="Plays" />
            <Line type="monotone" dataKey="shares" stroke="#10b981" strokeWidth={2} name="Shares" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Geographic & Language Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Countries</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={geographicData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" stroke="#999" />
              <YAxis dataKey="country" type="category" width={120} stroke="#999" />
              <Tooltip />
              <Bar dataKey="downloads" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Language Performance</h3>
          <div className="space-y-4">
            {languagePerformance.map((lang, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{lang.language}</span>
                  <span className="text-sm text-gray-500">{formatNumber(lang.downloads)} downloads</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${lang.engagement}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">{lang.engagement}% engagement rate</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
