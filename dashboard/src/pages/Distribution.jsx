import { useState } from 'react'
import { useQuery } from '@tantml:react-query'
import { Share2, CheckCircle, XCircle, Clock, Youtube, Music } from 'lucide-react'
import { distributionApi } from '../lib/api'
import { formatDateTime } from '../lib/utils'

const platformIcons = {
  spotify: Music,
  apple: Music,
  google: Music,
  youtube: Youtube,
}

const platformColors = {
  spotify: 'bg-green-100 text-green-700',
  apple: 'bg-purple-100 text-purple-700',
  google: 'bg-blue-100 text-blue-700',
  youtube: 'bg-red-100 text-red-700',
}

export default function Distribution() {
  const [selectedPodcast, setSelectedPodcast] = useState('all')

  const { data: distributions, isLoading } = useQuery({
    queryKey: ['distributions', selectedPodcast],
    queryFn: () => distributionApi.list({ podcast_id: selectedPodcast === 'all' ? undefined : selectedPodcast }).then(res => res.data),
    refetchInterval: 10000,
  })

  // Mock data
  const mockDistributions = [
    {
      id: '1',
      episode_title: 'The Future of AI',
      podcast_title: 'Tech Talk',
      platform: 'spotify',
      language: 'en',
      status: 'published',
      published_at: '2024-01-15T10:30:00Z',
      url: 'https://spotify.com/episode/123'
    },
    {
      id: '2',
      episode_title: 'The Future of AI',
      podcast_title: 'Tech Talk',
      platform: 'spotify',
      language: 'es',
      status: 'published',
      published_at: '2024-01-15T10:32:00Z',
      url: 'https://spotify.com/episode/124'
    },
    {
      id: '3',
      episode_title: 'Building a Startup',
      podcast_title: 'Startup Stories',
      platform: 'apple',
      language: 'en',
      status: 'processing',
      published_at: null,
      url: null
    },
    {
      id: '4',
      episode_title: 'Mental Health at Work',
      podcast_title: 'Health Matters',
      platform: 'youtube',
      language: 'en',
      status: 'failed',
      published_at: null,
      url: null,
      error: 'Invalid API credentials'
    },
  ]

  const displayDistributions = distributions || mockDistributions

  const statusConfig = {
    published: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
    processing: { icon: Clock, color: 'text-blue-600', bg: 'bg-blue-100' },
    failed: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100' },
  }

  const stats = {
    total: displayDistributions.length,
    published: displayDistributions.filter(d => d.status === 'published').length,
    processing: displayDistributions.filter(d => d.status === 'processing').length,
    failed: displayDistributions.filter(d => d.status === 'failed').length,
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Distribution</h1>
          <p className="text-gray-500 mt-1">Manage multi-platform publishing</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <Share2 size={20} />
          <span>Publish Episode</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Distributions</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Published</div>
          <div className="text-2xl font-bold text-green-600">{stats.published}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Processing</div>
          <div className="text-2xl font-bold text-blue-600">{stats.processing}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Failed</div>
          <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
        </div>
      </div>

      {/* Platform Connections */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Connected Platforms</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['spotify', 'apple', 'google', 'youtube'].map((platform) => {
            const Icon = platformIcons[platform]
            return (
              <div key={platform} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`p-2 rounded-lg ${platformColors[platform]}`}>
                    <Icon size={20} />
                  </div>
                  <span className="font-medium text-gray-900 capitalize">{platform}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-gray-600">Connected</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Distributions List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Distributions</h3>
          <select
            value={selectedPodcast}
            onChange={(e) => setSelectedPodcast(e.target.value)}
            className="input w-48"
          >
            <option value="all">All Podcasts</option>
            <option value="1">Tech Talk</option>
            <option value="2">Startup Stories</option>
            <option value="3">Health Matters</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Episode</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Platform</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Language</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Published</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {displayDistributions.map((dist) => {
                const StatusIcon = statusConfig[dist.status].icon
                const PlatformIcon = platformIcons[dist.platform]

                return (
                  <tr key={dist.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div className="font-medium text-gray-900">{dist.episode_title}</div>
                      <div className="text-sm text-gray-500">{dist.podcast_title}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className={`p-1.5 rounded ${platformColors[dist.platform]}`}>
                          <PlatformIcon size={16} />
                        </div>
                        <span className="text-sm text-gray-600 capitalize">{dist.platform}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm text-gray-600 uppercase">{dist.language}</span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <StatusIcon className={statusConfig[dist.status].color} size={16} />
                        <span className="text-sm text-gray-600 capitalize">{dist.status}</span>
                      </div>
                      {dist.error && (
                        <div className="text-xs text-red-600 mt-1">{dist.error}</div>
                      )}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {dist.published_at ? formatDateTime(dist.published_at) : '-'}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center justify-end gap-2">
                        {dist.url && (
                          <a
                            href={dist.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary-600 hover:text-primary-700"
                          >
                            View
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
