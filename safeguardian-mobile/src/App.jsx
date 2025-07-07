import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState(null)
  const [monitoringStatus, setMonitoringStatus] = useState('Protected')
  const [activeTab, setActiveTab] = useState('home')
  const [currentSettingsView, setCurrentSettingsView] = useState('main') // Track settings sub-screens

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

  // Handle platform access with proper event handling
  const accessPlatform = (platform) => {
    console.log('Accessing platform:', platform.name)
    setSelectedPlatform(platform)
  }

  // Open platform in browser with proper event handling
  const openPlatform = (url) => {
    console.log('Opening platform URL:', url)
    // For mobile apps, use window.open with proper target
    if (window.Capacitor) {
      // If running in Capacitor, use the Browser plugin
      window.open(url, '_system')
    } else {
      // For web, use _blank
      window.open(url, '_blank')
    }
  }

  // Handle tab navigation with proper event handling
  const navigateToTab = (tab) => {
    console.log('Navigating to tab:', tab)
    setActiveTab(tab)
    if (tab === 'home' && selectedPlatform) {
      setSelectedPlatform(null)
    }
    // Reset settings view when leaving settings
    if (tab !== 'settings') {
      setCurrentSettingsView('main')
    }
  }

  // Handle settings navigation
  const navigateToSettingsView = (view) => {
    console.log('Navigating to settings view:', view)
    setCurrentSettingsView(view)
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

  // Render platform selection screen
  const renderPlatformSelection = () => {
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-4">Choose Your Platform</h2>
        <p className="text-sm text-gray-400 mb-6">
          Access your social media safely. SafeGuardian is monitoring for your protection.
        </p>
        
        <div className="grid grid-cols-2 gap-4">
          {platforms.map((platform) => (
            <button
              key={platform.id}
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                accessPlatform(platform)
              }}
              onTouchStart={(e) => {
                e.preventDefault()
                accessPlatform(platform)
              }}
              className={`bg-gradient-to-br ${platform.color} p-4 rounded-2xl shadow-lg transform transition-all hover:scale-105 active:scale-95 cursor-pointer touch-manipulation`}
              style={{ WebkitTapHighlightColor: 'transparent' }}
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
    )
  }

  // Render platform access screen
  const renderPlatformAccess = () => {
    if (!selectedPlatform) return null;
    
    return (
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
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                openPlatform(selectedPlatform.url)
              }}
              onTouchStart={(e) => {
                e.preventDefault()
                openPlatform(selectedPlatform.url)
              }}
              className={`w-full bg-gradient-to-r ${selectedPlatform.color} text-white py-3 px-4 rounded-xl font-semibold transition-all hover:opacity-90 cursor-pointer touch-manipulation`}
              style={{ WebkitTapHighlightColor: 'transparent' }}
            >
              Open {selectedPlatform.name} Safely
            </button>
            
            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setSelectedPlatform(null)
              }}
              onTouchStart={(e) => {
                e.preventDefault()
                setSelectedPlatform(null)
              }}
              className="w-full bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-xl font-semibold transition-all cursor-pointer touch-manipulation"
              style={{ WebkitTapHighlightColor: 'transparent' }}
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
    )
  }

  // Render activity screen
  const renderActivityScreen = () => {
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-4">Activity Monitor</h2>
        <p className="text-sm text-gray-400 mb-6">
          View your recent activity and monitoring status.
        </p>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="text-xs text-gray-400 mb-2">Today, 10:23 AM</div>
            <div className="text-sm text-white">Instagram session monitored - No threats detected</div>
          </div>
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="text-xs text-gray-400 mb-2">Today, 9:15 AM</div>
            <div className="text-sm text-white">TikTok session monitored - No threats detected</div>
          </div>
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="text-xs text-gray-400 mb-2">Yesterday, 7:45 PM</div>
            <div className="text-sm text-white">WhatsApp session monitored - No threats detected</div>
          </div>
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="text-xs text-gray-400 mb-2">Yesterday, 4:30 PM</div>
            <div className="text-sm text-white">Snapchat session monitored - No threats detected</div>
          </div>
        </div>
      </div>
    )
  }

  // Render notification preferences screen
  const renderNotificationPreferences = () => {
    return (
      <div className="px-6">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('main')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('main')
            }}
            className="text-yellow-400 text-xl cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            ←
          </button>
          <h2 className="text-lg font-semibold">Notification Preferences</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">Threat Alerts</span>
              <div className="w-12 h-6 bg-green-500 rounded-full relative">
                <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
              </div>
            </div>
            <p className="text-xs text-gray-400">Get notified when potential threats are detected</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">Daily Reports</span>
              <div className="w-12 h-6 bg-green-500 rounded-full relative">
                <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
              </div>
            </div>
            <p className="text-xs text-gray-400">Receive daily activity summaries</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">App Updates</span>
              <div className="w-12 h-6 bg-gray-600 rounded-full relative">
                <div className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5"></div>
              </div>
            </div>
            <p className="text-xs text-gray-400">Get notified about app updates and new features</p>
          </div>
        </div>
      </div>
    )
  }

  // Render monitoring sensitivity screen
  const renderMonitoringSensitivity = () => {
    return (
      <div className="px-6">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('main')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('main')
            }}
            className="text-yellow-400 text-xl cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            ←
          </button>
          <h2 className="text-lg font-semibold">Monitoring Sensitivity</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">🔵 Standard</span>
              <span className="text-blue-400 text-sm">Current</span>
            </div>
            <p className="text-xs text-gray-400">Balanced protection with minimal false positives</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">🟡 High</span>
              <span className="text-gray-400 text-sm">Available</span>
            </div>
            <p className="text-xs text-gray-400">Enhanced monitoring with stricter detection</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">🟢 Low</span>
              <span className="text-gray-400 text-sm">Available</span>
            </div>
            <p className="text-xs text-gray-400">Basic monitoring for older children</p>
          </div>
        </div>
      </div>
    )
  }

  // Render parent dashboard access screen
  const renderParentDashboardAccess = () => {
    return (
      <div className="px-6">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('main')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('main')
            }}
            className="text-yellow-400 text-xl cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            ←
          </button>
          <h2 className="text-lg font-semibold">Parent Dashboard</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-green-900/30 rounded-xl border border-green-700">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">👨‍👩‍👧‍👦</span>
              <div>
                <h3 className="text-white font-medium">Connected</h3>
                <p className="text-xs text-green-400">Parent dashboard is active</p>
              </div>
            </div>
            <p className="text-xs text-gray-300">Your parents can view activity reports and receive alerts through their dashboard.</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <h3 className="text-white font-medium mb-2">Dashboard Features</h3>
            <div className="space-y-2 text-xs text-gray-300">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Real-time activity monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Threat detection alerts</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Weekly safety reports</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Emergency contact system</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render privacy settings screen
  const renderPrivacySettings = () => {
    return (
      <div className="px-6">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('main')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('main')
            }}
            className="text-yellow-400 text-xl cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            ←
          </button>
          <h2 className="text-lg font-semibold">Privacy Settings</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">Data Encryption</span>
              <span className="text-green-400 text-sm">Enabled</span>
            </div>
            <p className="text-xs text-gray-400">All data is encrypted with AES-256 encryption</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">Anonymous Analytics</span>
              <div className="w-12 h-6 bg-gray-600 rounded-full relative">
                <div className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5"></div>
              </div>
            </div>
            <p className="text-xs text-gray-400">Help improve SafeGuardian with anonymous usage data</p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">Data Retention</span>
              <span className="text-blue-400 text-sm">30 days</span>
            </div>
            <p className="text-xs text-gray-400">Activity data is automatically deleted after 30 days</p>
          </div>
        </div>
      </div>
    )
  }

  // Render about SafeGuardian screen
  const renderAboutSafeGuardian = () => {
    return (
      <div className="px-6">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('main')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('main')
            }}
            className="text-yellow-400 text-xl cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            ←
          </button>
          <h2 className="text-lg font-semibold">About SafeGuardian</h2>
        </div>
        
        <div className="space-y-4">
          <div className="text-center p-6 bg-gray-800/50 rounded-xl border border-gray-700">
            <div className="text-4xl mb-3">🛡️</div>
            <h3 className="text-xl font-bold text-white mb-2">SafeGuardian</h3>
            <p className="text-sm text-gray-400 mb-4">Version 1.0.0</p>
            <p className="text-xs text-gray-300">
              Protecting children in the digital world with AI-powered monitoring and real-time threat detection.
            </p>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <h3 className="text-white font-medium mb-3">Key Features</h3>
            <div className="space-y-2 text-xs text-gray-300">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>AI-powered threat detection</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>Real-time monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>Parent dashboard integration</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>Secure evidence collection</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>Multi-platform support</span>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <h3 className="text-white font-medium mb-2">Support</h3>
            <p className="text-xs text-gray-300 mb-3">
              Need help? Contact our support team for assistance.
            </p>
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-all cursor-pointer touch-manipulation"
                    style={{ WebkitTapHighlightColor: 'transparent' }}>
              Contact Support
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Render main settings screen
  const renderMainSettingsScreen = () => {
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-4">Settings</h2>
        <p className="text-sm text-gray-400 mb-6">
          Configure your SafeGuardian protection settings.
        </p>
        
        <div className="space-y-2">
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('notifications')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('notifications')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-white">Notification Preferences</span>
            <span className="text-gray-400">›</span>
          </button>
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('monitoring')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('monitoring')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-white">Monitoring Sensitivity</span>
            <span className="text-gray-400">›</span>
          </button>
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('dashboard')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('dashboard')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-white">Parent Dashboard Access</span>
            <span className="text-gray-400">›</span>
          </button>
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('privacy')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('privacy')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-white">Privacy Settings</span>
            <span className="text-gray-400">›</span>
          </button>
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('about')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('about')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-white">About SafeGuardian</span>
            <span className="text-gray-400">›</span>
          </button>
        </div>
      </div>
    )
  }

  // Render settings screen based on current view
  const renderSettingsScreen = () => {
    switch (currentSettingsView) {
      case 'notifications':
        return renderNotificationPreferences()
      case 'monitoring':
        return renderMonitoringSensitivity()
      case 'dashboard':
        return renderParentDashboardAccess()
      case 'privacy':
        return renderPrivacySettings()
      case 'about':
        return renderAboutSafeGuardian()
      default:
        return renderMainSettingsScreen()
    }
  }

  // Render protected screen
  const renderProtectedScreen = () => {
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-4">Protection Status</h2>
        <p className="text-sm text-gray-400 mb-6">
          Your SafeGuardian protection is active and monitoring.
        </p>
        
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="text-center mb-6">
            <div className="text-4xl mb-3">🛡️</div>
            <h2 className="text-xl font-bold mb-2">Active Protection</h2>
            <p className="text-sm text-gray-400">
              All systems operational
            </p>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-sm text-white">AI Monitoring</span>
              <span className="text-xs text-green-400">Active</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-sm text-white">Threat Detection</span>
              <span className="text-xs text-green-400">Enhanced</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-sm text-white">Parent Alerts</span>
              <span className="text-xs text-green-400">Enabled</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-sm text-white">Evidence Collection</span>
              <span className="text-xs text-green-400">Enabled</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render content based on active tab
  const renderContent = () => {
    console.log('Rendering content for tab:', activeTab, 'Selected platform:', selectedPlatform, 'Settings view:', currentSettingsView)
    
    if (activeTab === 'home') {
      return selectedPlatform ? renderPlatformAccess() : renderPlatformSelection();
    } else if (activeTab === 'activity') {
      return renderActivityScreen();
    } else if (activeTab === 'protected') {
      return renderProtectedScreen();
    } else if (activeTab === 'settings') {
      return renderSettingsScreen();
    }
    
    // Default fallback
    return renderPlatformSelection();
  }

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

      {/* Main Content */}
      {renderContent()}

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur border-t border-gray-700 p-4">
        <div className="flex justify-around">
          <button 
            className="flex flex-col items-center gap-1 cursor-pointer touch-manipulation"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToTab('home')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToTab('home')
            }}
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-lg">🏠</span>
            <span className={`text-xs ${activeTab === 'home' ? 'text-yellow-400' : 'text-gray-400'}`}>Home</span>
          </button>
          <button 
            className="flex flex-col items-center gap-1 cursor-pointer touch-manipulation"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToTab('activity')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToTab('activity')
            }}
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-lg">📊</span>
            <span className={`text-xs ${activeTab === 'activity' ? 'text-yellow-400' : 'text-gray-400'}`}>Activity</span>
          </button>
          <button 
            className="flex flex-col items-center gap-1 cursor-pointer touch-manipulation"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToTab('protected')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToTab('protected')
            }}
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-lg">🛡️</span>
            <span className={`text-xs ${activeTab === 'protected' ? 'text-yellow-400' : 'text-gray-400'}`}>Protected</span>
          </button>
          <button 
            className="flex flex-col items-center gap-1 cursor-pointer touch-manipulation"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToTab('settings')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToTab('settings')
            }}
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-lg">⚙️</span>
            <span className={`text-xs ${activeTab === 'settings' ? 'text-yellow-400' : 'text-gray-400'}`}>Settings</span>
          </button>
        </div>
      </div>

      {/* Padding for bottom nav */}
      <div className="h-20"></div>
    </div>
  )
}

export default App

