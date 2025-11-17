import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Upload, Search, Download, Globe, CheckCircle, Clock, XCircle } from 'lucide-react'
import { transcriptionsApi } from '../lib/api'
import { formatDateTime } from '../lib/utils'

export default function Transcriptions() {
  const [showUploadModal, setShowUploadModal] = useState(false)

  const { data: transcriptions, isLoading } = useQuery({
    queryKey: ['transcriptions'],
    queryFn: () => transcriptionsApi.list().then(res => res.data),
    refetchInterval: 5000, // Poll every 5 seconds for status updates
  })

  // Mock data
  const mockJobs = [
    {
      id: 'job-1',
      episode_title: 'The Future of AI in Development',
      podcast_title: 'Tech Talk',
      status: 'completed',
      source_language: 'en',
      target_languages: ['es', 'fr', 'de'],
      progress: 100,
      created_at: '2024-01-15T10:30:00Z',
      completed_at: '2024-01-15T10:35:00Z',
      duration: 300
    },
    {
      id: 'job-2',
      episode_title: 'Building a Successful Startup',
      podcast_title: 'Startup Stories',
      status: 'processing',
      source_language: 'en',
      target_languages: ['es', 'pt'],
      progress: 65,
      created_at: '2024-01-15T11:00:00Z',
      duration: null
    },
    {
      id: 'job-3',
      episode_title: 'Mental Health in the Workplace',
      podcast_title: 'Health Matters',
      status: 'queued',
      source_language: 'en',
      target_languages: ['es', 'fr', 'de', 'it'],
      progress: 0,
      created_at: '2024-01-15T11:15:00Z',
      duration: null
    },
    {
      id: 'job-4',
      episode_title: 'Quantum Computing Basics',
      podcast_title: 'Tech Talk',
      status: 'failed',
      source_language: 'en',
      target_languages: ['es'],
      progress: 0,
      created_at: '2024-01-15T09:00:00Z',
      error: 'Audio file corrupted',
      duration: null
    },
  ]

  const displayJobs = transcriptions || mockJobs

  const statusConfig = {
    completed: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
    processing: { icon: Clock, color: 'text-blue-600', bg: 'bg-blue-100' },
    queued: { icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100' },
    failed: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100' },
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transcriptions</h1>
          <p className="text-gray-500 mt-1">Manage transcription and translation jobs</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Upload size={20} />
          <span>Upload Audio</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Jobs</div>
          <div className="text-2xl font-bold text-gray-900">{displayJobs.length}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Completed</div>
          <div className="text-2xl font-bold text-green-600">
            {displayJobs.filter(j => j.status === 'completed').length}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Processing</div>
          <div className="text-2xl font-bold text-blue-600">
            {displayJobs.filter(j => j.status === 'processing').length}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Failed</div>
          <div className="text-2xl font-bold text-red-600">
            {displayJobs.filter(j => j.status === 'failed').length}
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {displayJobs.map((job) => {
          const StatusIcon = statusConfig[job.status].icon
          return (
            <div key={job.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className={`p-3 rounded-lg ${statusConfig[job.status].bg}`}>
                    <StatusIcon className={statusConfig[job.status].color} size={24} />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{job.episode_title}</h3>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig[job.status].bg} ${statusConfig[job.status].color}`}>
                        {job.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      <span>{job.podcast_title}</span>
                      <span>•</span>
                      <span>{formatDateTime(job.created_at)}</span>
                      {job.duration && (
                        <>
                          <span>•</span>
                          <span>{Math.floor(job.duration / 60)}m {job.duration % 60}s</span>
                        </>
                      )}
                    </div>

                    <div className="flex items-center gap-3 mb-3">
                      <div className="flex items-center gap-2">
                        <Globe size={16} className="text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {job.source_language.toUpperCase()} → {job.target_languages.map(l => l.toUpperCase()).join(', ')}
                        </span>
                      </div>
                    </div>

                    {job.status === 'processing' && (
                      <div className="mb-2">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-600">Progress</span>
                          <span className="font-medium text-gray-900">{job.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {job.error && (
                      <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
                        Error: {job.error}
                      </div>
                    )}
                  </div>
                </div>

                {job.status === 'completed' && (
                  <div className="flex gap-2">
                    <button className="btn btn-secondary text-sm flex items-center gap-2">
                      <Download size={16} />
                      <span>Download</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {displayJobs.length === 0 && (
        <div className="card text-center py-12">
          <Upload size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No transcription jobs yet</h3>
          <p className="text-gray-500 mb-4">Upload an audio file to get started</p>
          <button onClick={() => setShowUploadModal(true)} className="btn btn-primary">
            Upload Audio
          </button>
        </div>
      )}
    </div>
  )
}
