import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, Play, Edit, Trash2, Clock } from 'lucide-react'
import { episodesApi } from '../lib/api'
import { formatDate, formatDuration } from '../lib/utils'

export default function Episodes() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterPodcast, setFilterPodcast] = useState('all')

  const { data: episodes, isLoading } = useQuery({
    queryKey: ['episodes', filterPodcast],
    queryFn: () => episodesApi.list({ podcast_id: filterPodcast === 'all' ? undefined : filterPodcast }).then(res => res.data),
  })

  // Mock data
  const mockEpisodes = [
    {
      id: '1',
      title: 'The Future of AI in Development',
      podcast: 'Tech Talk',
      description: 'Exploring how artificial intelligence is transforming software development',
      duration: 3245,
      published_at: '2024-01-15',
      status: 'published',
      downloads: 2340
    },
    {
      id: '2',
      title: 'Building a Successful Startup',
      podcast: 'Startup Stories',
      description: 'Interview with Sarah Chen, founder of TechFlow',
      duration: 2890,
      published_at: '2024-01-12',
      status: 'published',
      downloads: 1890
    },
    {
      id: '3',
      title: 'Mental Health in the Workplace',
      podcast: 'Health Matters',
      description: 'Expert insights on maintaining mental wellness at work',
      duration: 2456,
      published_at: '2024-01-10',
      status: 'published',
      downloads: 3120
    },
    {
      id: '4',
      title: 'Quantum Computing Explained',
      podcast: 'Tech Talk',
      description: 'Understanding the basics of quantum computing',
      duration: 3567,
      published_at: '2024-01-08',
      status: 'draft',
      downloads: 0
    },
  ]

  const displayEpisodes = episodes || mockEpisodes
  const filteredEpisodes = displayEpisodes.filter(episode =>
    episode.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const statusColor = {
    published: 'bg-green-100 text-green-700',
    draft: 'bg-gray-100 text-gray-700',
    processing: 'bg-blue-100 text-blue-700'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Episodes</h1>
          <p className="text-gray-500 mt-1">Manage your podcast episodes</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <Plus size={20} />
          <span>New Episode</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search episodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
        <select
          value={filterPodcast}
          onChange={(e) => setFilterPodcast(e.target.value)}
          className="input w-64"
        >
          <option value="all">All Podcasts</option>
          <option value="1">Tech Talk</option>
          <option value="2">Startup Stories</option>
          <option value="3">Health Matters</option>
        </select>
      </div>

      {/* Episodes List */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Episode</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Podcast</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Duration</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Published</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Downloads</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredEpisodes.map((episode) => (
                <tr key={episode.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                        <Play size={20} className="text-gray-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{episode.title}</div>
                        <div className="text-sm text-gray-500 line-clamp-1">{episode.description}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-sm text-gray-600">{episode.podcast}</td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock size={16} />
                      <span>{formatDuration(episode.duration)}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-sm text-gray-600">{formatDate(episode.published_at)}</td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor[episode.status]}`}>
                      {episode.status}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-sm font-medium text-gray-900">
                    {episode.downloads.toLocaleString()}
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                        <Edit size={18} className="text-gray-600" />
                      </button>
                      <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                        <Trash2 size={18} className="text-red-600" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredEpisodes.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No episodes found</p>
          </div>
        )}
      </div>
    </div>
  )
}
