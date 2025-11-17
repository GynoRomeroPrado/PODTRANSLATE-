import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Save, Key, Bell, Globe, Shield } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

export default function Settings() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
    }
  })

  const onSubmitProfile = (data) => {
    console.log('Profile update:', data)
    // API call here
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: Shield },
    { id: 'api-keys', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'languages', label: 'Languages', icon: Globe },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account and preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Settings</h2>
              <form onSubmit={handleSubmit(onSubmitProfile)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <input
                    {...register('name', { required: 'Name is required' })}
                    className="input"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    {...register('email', { required: 'Email is required' })}
                    className="input"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company
                  </label>
                  <input {...register('company')} className="input" />
                </div>

                <button type="submit" className="btn btn-primary flex items-center gap-2">
                  <Save size={20} />
                  <span>Save Changes</span>
                </button>
              </form>
            </div>
          )}

          {activeTab === 'api-keys' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">API Keys</h2>
              <p className="text-gray-600 mb-6">
                Use API keys to authenticate requests to the PodTranslate API.
              </p>

              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">Production Key</span>
                    <span className="text-sm text-green-600">Active</span>
                  </div>
                  <code className="block text-sm bg-gray-50 px-3 py-2 rounded font-mono text-gray-600">
                    ptk_live_••••••••••••••••••••1234
                  </code>
                  <div className="flex gap-2 mt-3">
                    <button className="text-sm text-primary-600 hover:text-primary-700">
                      Regenerate
                    </button>
                    <button className="text-sm text-red-600 hover:text-red-700">
                      Revoke
                    </button>
                  </div>
                </div>

                <button className="btn btn-secondary">
                  Generate New API Key
                </button>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Preferences</h2>
              <div className="space-y-4">
                {[
                  { id: 'transcription', label: 'Transcription completed', default: true },
                  { id: 'distribution', label: 'Episode published', default: true },
                  { id: 'analytics', label: 'Weekly analytics report', default: false },
                  { id: 'errors', label: 'Error notifications', default: true },
                ].map((setting) => (
                  <div key={setting.id} className="flex items-center justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-700">{setting.label}</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        defaultChecked={setting.default}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'languages' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Supported Languages</h2>
              <p className="text-gray-600 mb-6">
                Select languages for automatic transcription and translation.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
                  'Russian', 'Japanese', 'Chinese', 'Korean', 'Arabic', 'Hindi'
                ].map((lang) => (
                  <label key={lang} className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded text-primary-600 focus:ring-primary-500" />
                    <span className="text-sm text-gray-700">{lang}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
