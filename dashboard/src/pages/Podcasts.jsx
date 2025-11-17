import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, BarChart } from 'lucide-react'
import { podcastsApi } from '../lib/api'
import { formatDate, formatNumber } from '../lib/utils'

export default function Podcasts() {
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: podcasts, isLoading } = useQuery({
    queryKey: ['podcasts'],
    queryFn: () => podcastsApi.list().then(res => res.data),
  })

  // Mock data for demo
  const mockPodcasts = [
    {
      id: '1',
      title: 'Tech Talk',
      description: 'Weekly discussions about the latest in technology',
      category: 'Technology',
      language: 'en',
      episodes: 42,
      subscribers: 12500,
      created_at: '2023-06-15'
    },
    {
      id: '2',
      title: 'Startup Stories',
      description: 'Interviews with successful entrepreneurs',
      category: 'Business',
      language: 'en',
      episodes: 28,
      subscribers: 8900,
      created_at: '2023-08-22'
    },
    {
      id: '3',
      title: 'Health Matters',
      description: 'Expert advice on health and wellness',
      category: 'Health',
      language: 'en',
      episodes: 35,
      subscribers: 15200,
      created_at: '2023-05-10'
    },
  ]

  const displayPodcasts = podcasts || mockPodcasts
  const filteredPodcasts = displayPodcasts.filter(podcast =>
    podcast.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    podcast.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Podcasts</h1>
          <p className="text-gray-500 mt-1">Manage your podcast shows</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          <span>New Podcast</span>
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search podcasts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Podcasts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPodcasts.map((podcast) => (
          <div key={podcast.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {podcast.title[0]}
                </span>
              </div>
              <div className="flex gap-2">
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <Edit size={18} className="text-gray-600" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <Trash2 size={18} className="text-red-600" />
                </button>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {podcast.title}
            </h3>
            <p className="text-sm text-gray-500 mb-4 line-clamp-2">
              {podcast.description}
            </p>

            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Episodes</span>
                <span className="font-medium text-gray-900">{podcast.episodes}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Subscribers</span>
                <span className="font-medium text-gray-900">{formatNumber(podcast.subscribers)}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Created</span>
                <span className="font-medium text-gray-900">{formatDate(podcast.created_at)}</span>
              </div>
            </div>

            <div className="flex gap-2">
              <button className="flex-1 btn btn-secondary text-sm flex items-center justify-center gap-2">
                <BarChart size={16} />
                <span>Analytics</span>
              </button>
              <button className="flex-1 btn btn-primary text-sm">
                View Episodes
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredPodcasts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No podcasts found</p>
        </div>
      )}
    </div>
  )
}
