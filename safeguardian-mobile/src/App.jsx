import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState(null)
  const [monitoringStatus, setMonitoringStatus] = useState('Protected')

  // Social media platforms
  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: '📷',
      color: 'from-pink-500 to-purple-600',
      url: 'https://instagram.com',
      status: 'safe'
    },
    {
      id: 'snapchat',
      name: 'Snapchat',
      icon: '👻',
      color: 'from-yellow-400 to-yellow-600',
      url: 'https://snapchat.com',
      status: 'safe'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: '👥',
      color: 'from-blue-500 to-blue-700',
      url: 'https://facebook.com',
      status: 'safe'
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: '💬',
      color: 'from-green-500 to-green-600',
      url: 'https://web.whatsapp.com',
      status: 'safe'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: '🎵',
      color: 'from-black to-red-600',
      url: 'https://tiktok.com',
      status: 'safe'
    },
    {
      id: 'discord',
      name: 'Discord',
      icon: '🎮',
      color: 'from-indigo-500 to-purple-600',
      url: 'https://discord.com',
      status: 'safe'
    }
  ]

  // Start monitoring when app loads
  useEffect(() => {
    setIsMonitoring(true)
    setMonitoringStatus('Active Protection')
  }, [])

  // Handle platform access
  const accessPlatform = (platform) => {
    setSelectedPlatform(platform)
    // In a real app, this would open the platform in a monitored webview
    // For demo purposes, we'll show a monitoring interface
    setTimeout(() => {
      window.open(platform.url, '_blank')
    }, 1000)
  }

  // Monitoring indicator component
  const MonitoringIndicator = () => (
    <div className="flex items-center gap-2 mb-6">
      <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
      <span className="text-sm text-gray-300">
        {monitoringStatus} • {isMonitoring ? 'Monitoring Active' : 'Monitoring Inactive'}
      </span>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl flex items-center justify-center">
              <span className="text-xl">🛡️</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">SafeGuardian</h1>
              <p className="text-xs text-gray-400">Protected Access</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Status</div>
            <div className="text-sm font-semibold text-green-400">Protected</div>
          </div>
        </div>
        
        <MonitoringIndicator />
      </div>

      {/* Platform Selection */}
      {!selectedPlatform ? (
        <div className="px-6">
          <h2 className="text-lg font-semibold mb-4">Choose Your Platform</h2>
          <p className="text-sm text-gray-400 mb-6">
            Access your social media safely. SafeGuardian is monitoring for your protection.
          </p>
          
          <div className="grid grid-cols-2 gap-4">
            {platforms.map((platform) => (
              <button
                key={platform.id}
                onClick={() => accessPlatform(platform)}
                className={`bg-gradient-to-br ${platform.color} p-4 rounded-2xl shadow-lg transform transition-all hover:scale-105 active:scale-95`}
              >
                <div className="text-3xl mb-2">{platform.icon}</div>
                <div className="text-white font-semibold text-sm">{platform.name}</div>
                <div className="text-xs text-white/80 mt-1">
                  {platform.status === 'safe' ? '✅ Safe' : '⚠️ Caution'}
                </div>
              </button>
            ))}
          </div>

          {/* Safety Features */}
          <div className="mt-8 p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <h3 className="text-sm font-semibold text-yellow-400 mb-2">🛡️ Active Protection Features</h3>
            <div className="space-y-1 text-xs text-gray-300">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Real-time message monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>AI-powered threat detection</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Automatic parent notifications</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Secure evidence collection</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Platform Access Screen */
        <div className="px-6">
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="text-center mb-6">
              <div className="text-4xl mb-3">{selectedPlatform.icon}</div>
              <h2 className="text-xl font-bold mb-2">Accessing {selectedPlatform.name}</h2>
              <p className="text-sm text-gray-400">
                SafeGuardian is now monitoring your session for safety
              </p>
            </div>

            {/* Monitoring Status */}
            <div className="space-y-3 mb-6">
              <div className="flex items-center justify-between p-3 bg-green-900/30 rounded-lg border border-green-700">
                <span className="text-sm">🔒 Secure Connection</span>
                <span className="text-xs text-green-400">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-900/30 rounded-lg border border-blue-700">
                <span className="text-sm">🤖 AI Monitoring</span>
                <span className="text-xs text-blue-400">Scanning</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-900/30 rounded-lg border border-purple-700">
                <span className="text-sm">👨‍👩‍👧‍👦 Parent Dashboard</span>
                <span className="text-xs text-purple-400">Connected</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={() => window.open(selectedPlatform.url, '_blank')}
                className={`w-full bg-gradient-to-r ${selectedPlatform.color} text-white py-3 px-4 rounded-xl font-semibold transition-all hover:opacity-90`}
              >
                Open {selectedPlatform.name} Safely
              </button>
              
              <button
                onClick={() => setSelectedPlatform(null)}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-xl font-semibold transition-all"
              >
                Choose Different Platform
              </button>
            </div>

            {/* Safety Reminder */}
            <div className="mt-6 p-4 bg-yellow-900/20 rounded-lg border border-yellow-700">
              <div className="flex items-start gap-3">
                <span className="text-yellow-400 text-lg">⚠️</span>
                <div>
                  <h4 className="text-sm font-semibold text-yellow-400 mb-1">Safety Reminder</h4>
                  <p className="text-xs text-gray-300">
                    Never share personal information with strangers. If someone makes you uncomfortable, 
                    close the app immediately. SafeGuardian is watching to keep you safe.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur border-t border-gray-700 p-4">
        <div className="flex justify-around">
          <button className="flex flex-col items-center gap-1">
            <span className="text-lg">🏠</span>
            <span className="text-xs text-gray-400">Home</span>
          </button>
          <button className="flex flex-col items-center gap-1">
            <span className="text-lg">📊</span>
            <span className="text-xs text-gray-400">Activity</span>
          </button>
          <button className="flex flex-col items-center gap-1">
            <span className="text-lg">🛡️</span>
            <span className="text-xs text-yellow-400">Protected</span>
          </button>
          <button className="flex flex-col items-center gap-1">
            <span className="text-lg">⚙️</span>
            <span className="text-xs text-gray-400">Settings</span>
          </button>
        </div>
      </div>

      {/* Padding for bottom nav */}
      <div className="h-20"></div>
    </div>
  )
}

export default App

