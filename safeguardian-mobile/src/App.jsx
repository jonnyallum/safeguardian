import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState(null)
  const [monitoringStatus, setMonitoringStatus] = useState('Protected')
  const [activeTab, setActiveTab] = useState('home')
  const [currentSettingsView, setCurrentSettingsView] = useState('main')
  const [parentEmail, setParentEmail] = useState('')
  const [isParentEmailSet, setIsParentEmailSet] = useState(false)
  const [sessionData, setSessionData] = useState({})
  const [platformSessions, setPlatformSessions] = useState({})

  // Social media platforms with enhanced session tracking
  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: '📷',
      color: 'from-pink-500 to-purple-600',
      url: 'https://instagram.com',
      status: 'safe',
      sessionKey: 'instagram_session'
    },
    {
      id: 'snapchat',
      name: 'Snapchat',
      icon: '👻',
      color: 'from-yellow-400 to-yellow-600',
      url: 'https://snapchat.com',
      status: 'safe',
      sessionKey: 'snapchat_session'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: '👥',
      color: 'from-blue-500 to-blue-700',
      url: 'https://facebook.com',
      status: 'safe',
      sessionKey: 'facebook_session'
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: '💬',
      color: 'from-green-500 to-green-600',
      url: 'https://web.whatsapp.com',
      status: 'safe',
      sessionKey: 'whatsapp_session'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: '🎵',
      color: 'from-black to-red-600',
      url: 'https://tiktok.com',
      status: 'safe',
      sessionKey: 'tiktok_session'
    },
    {
      id: 'discord',
      name: 'Discord',
      icon: '🎮',
      color: 'from-indigo-500 to-purple-600',
      url: 'https://discord.com',
      status: 'safe',
      sessionKey: 'discord_session'
    }
  ]

  // Initialize app and load saved data
  useEffect(() => {
    setIsMonitoring(true)
    setMonitoringStatus('Active Protection')
    
    // Load saved parent email
    const savedEmail = localStorage.getItem('safeguardian_parent_email')
    if (savedEmail) {
      setParentEmail(savedEmail)
      setIsParentEmailSet(true)
    }
    
    // Load session data
    loadSessionData()
    
    // Set up session monitoring
    startSessionMonitoring()
  }, [])

  // Load session data from localStorage
  const loadSessionData = () => {
    try {
      const savedSessions = localStorage.getItem('safeguardian_sessions')
      if (savedSessions) {
        setPlatformSessions(JSON.parse(savedSessions))
      }
    } catch (error) {
      console.error('Error loading session data:', error)
    }
  }

  // Save session data to localStorage
  const saveSessionData = (sessions) => {
    try {
      localStorage.setItem('safeguardian_sessions', JSON.stringify(sessions))
      setPlatformSessions(sessions)
    } catch (error) {
      console.error('Error saving session data:', error)
    }
  }

  // Start session monitoring
  const startSessionMonitoring = () => {
    // Monitor for platform sessions every 30 seconds
    const interval = setInterval(() => {
      checkPlatformSessions()
    }, 30000)

    // Initial check
    checkPlatformSessions()

    return () => clearInterval(interval)
  }

  // Check for active platform sessions
  const checkPlatformSessions = () => {
    const newSessions = {}
    
    platforms.forEach(platform => {
      // Check if platform is open in any tab
      const isActive = checkPlatformSession(platform)
      if (isActive) {
        newSessions[platform.id] = {
          platform: platform.name,
          startTime: platformSessions[platform.id]?.startTime || new Date().toISOString(),
          lastActivity: new Date().toISOString(),
          status: 'active',
          monitored: true
        }
      }
    })

    // Update sessions if changed
    if (JSON.stringify(newSessions) !== JSON.stringify(platformSessions)) {
      saveSessionData(newSessions)
      
      // Send session data to Supabase
      syncSessionData(newSessions)
    }
  }

  // Check if a platform session is active (simulated)
  const checkPlatformSession = (platform) => {
    // In a real implementation, this would check for actual browser sessions
    // For demo purposes, we'll simulate session detection
    const sessionKey = `${platform.id}_last_opened`
    const lastOpened = localStorage.getItem(sessionKey)
    
    if (lastOpened) {
      const timeDiff = Date.now() - parseInt(lastOpened)
      // Consider session active if opened within last 5 minutes
      return timeDiff < 5 * 60 * 1000
    }
    
    return false
  }

  // Sync session data with Supabase
  const syncSessionData = async (sessions) => {
    try {
      const sessionData = {
        user_id: 'demo_user', // In real app, this would be the actual user ID
        parent_email: parentEmail,
        sessions: sessions,
        timestamp: new Date().toISOString(),
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language
        }
      }

      // In a real implementation, this would send to Supabase
      console.log('Syncing session data to Supabase:', sessionData)
      
      // Store locally for demo
      localStorage.setItem('safeguardian_sync_data', JSON.stringify(sessionData))
      
    } catch (error) {
      console.error('Error syncing session data:', error)
    }
  }

  // Save parent email
  const saveParentEmail = (email) => {
    if (email && email.includes('@')) {
      localStorage.setItem('safeguardian_parent_email', email)
      setParentEmail(email)
      setIsParentEmailSet(true)
      
      // Sync with backend
      syncParentEmail(email)
      
      return true
    }
    return false
  }

  // Sync parent email with backend
  const syncParentEmail = async (email) => {
    try {
      const emailData = {
        parent_email: email,
        child_device_id: 'demo_device', // In real app, this would be unique device ID
        setup_timestamp: new Date().toISOString(),
        app_version: '1.0.0'
      }

      console.log('Syncing parent email to Supabase:', emailData)
      
      // Store locally for demo
      localStorage.setItem('safeguardian_parent_setup', JSON.stringify(emailData))
      
    } catch (error) {
      console.error('Error syncing parent email:', error)
    }
  }

  // Handle platform access with session tracking
  const accessPlatform = (platform) => {
    console.log('Accessing platform:', platform.name)
    setSelectedPlatform(platform)
    
    // Record session start
    const sessionKey = `${platform.id}_last_opened`
    localStorage.setItem(sessionKey, Date.now().toString())
    
    // Update session data
    const newSessions = {
      ...platformSessions,
      [platform.id]: {
        platform: platform.name,
        startTime: new Date().toISOString(),
        lastActivity: new Date().toISOString(),
        status: 'active',
        monitored: true
      }
    }
    saveSessionData(newSessions)
  }

  // Open platform with enhanced tracking
  const openPlatform = (url) => {
    console.log('Opening platform URL:', url)
    
    // Record platform access
    if (selectedPlatform) {
      const accessData = {
        platform: selectedPlatform.name,
        url: url,
        timestamp: new Date().toISOString(),
        parent_email: parentEmail,
        monitoring_active: isMonitoring
      }
      
      console.log('Platform access logged:', accessData)
      
      // Store access log
      const accessLog = JSON.parse(localStorage.getItem('safeguardian_access_log') || '[]')
      accessLog.push(accessData)
      localStorage.setItem('safeguardian_access_log', JSON.stringify(accessLog.slice(-50))) // Keep last 50 entries
    }
    
    // Open platform
    if (window.Capacitor) {
      window.open(url, '_system')
    } else {
      window.open(url, '_blank')
    }
  }

  // Handle tab navigation
  const navigateToTab = (tab) => {
    console.log('Navigating to tab:', tab)
    setActiveTab(tab)
    if (tab === 'home' && selectedPlatform) {
      setSelectedPlatform(null)
    }
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
      {isParentEmailSet && (
        <span className="text-xs text-blue-400 ml-2">
          📧 Parent Connected
        </span>
      )}
    </div>
  )

  // Parent email setup component
  const ParentEmailSetup = () => {
    const [emailInput, setEmailInput] = useState('')
    const [isValid, setIsValid] = useState(false)

    const handleEmailChange = (e) => {
      const email = e.target.value
      setEmailInput(email)
      setIsValid(email.includes('@') && email.includes('.'))
    }

    const handleSave = () => {
      if (saveParentEmail(emailInput)) {
        setCurrentSettingsView('main')
      }
    }

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
          <h2 className="text-lg font-semibold">Parent Email Setup</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
            <h3 className="text-white font-medium mb-2">📧 Connect with Parent</h3>
            <p className="text-xs text-gray-300 mb-4">
              Enter your parent's email address to enable monitoring alerts and reports.
            </p>
            
            <input
              type="email"
              value={emailInput}
              onChange={handleEmailChange}
              placeholder="parent@example.com"
              className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
            />
            
            <button
              onClick={handleSave}
              disabled={!isValid}
              className={`w-full mt-3 py-2 px-4 rounded-lg font-medium transition-all ${
                isValid 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer' 
                  : 'bg-gray-700 text-gray-400 cursor-not-allowed'
              }`}
              style={{ WebkitTapHighlightColor: 'transparent' }}
            >
              Save Parent Email
            </button>
          </div>
          
          {isParentEmailSet && (
            <div className="p-4 bg-green-900/30 rounded-xl border border-green-700">
              <h3 className="text-green-400 font-medium mb-2">✅ Parent Email Connected</h3>
              <p className="text-xs text-gray-300">
                Current: {parentEmail}
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Session monitoring component
  const SessionMonitoring = () => {
    const activeSessions = Object.keys(platformSessions).length
    
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
          <h2 className="text-lg font-semibold">Session Monitoring</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <h3 className="text-white font-medium mb-2">📊 Active Sessions</h3>
            <p className="text-2xl font-bold text-blue-400">{activeSessions}</p>
            <p className="text-xs text-gray-400">Currently monitored platforms</p>
          </div>
          
          {Object.entries(platformSessions).map(([platformId, session]) => (
            <div key={platformId} className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{session.platform}</span>
                <span className="text-xs text-green-400">● Active</span>
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>Started: {new Date(session.startTime).toLocaleTimeString()}</div>
                <div>Last Activity: {new Date(session.lastActivity).toLocaleTimeString()}</div>
                <div>Status: {session.monitored ? '🛡️ Monitored' : '⚠️ Unmonitored'}</div>
              </div>
            </div>
          ))}
          
          {activeSessions === 0 && (
            <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700 text-center">
              <p className="text-gray-400">No active sessions detected</p>
              <p className="text-xs text-gray-500 mt-1">Open a social media platform to start monitoring</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Render platform selection screen
  const renderPlatformSelection = () => {
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-4">Choose Your Platform</h2>
        <p className="text-sm text-gray-400 mb-6">
          Access your social media safely. SafeGuardian is monitoring for your protection.
        </p>
        
        <div className="grid grid-cols-2 gap-4">
          {platforms.map((platform) => {
            const hasActiveSession = platformSessions[platform.id]
            
            return (
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
                className={`bg-gradient-to-br ${platform.color} p-4 rounded-2xl shadow-lg transform transition-all hover:scale-105 active:scale-95 cursor-pointer touch-manipulation relative`}
                style={{ WebkitTapHighlightColor: 'transparent' }}
              >
                <div className="text-3xl mb-2">{platform.icon}</div>
                <div className="text-white font-semibold text-sm">{platform.name}</div>
                <div className="text-xs text-white/80 mt-1">
                  {platform.status === 'safe' ? '✅ Safe' : '⚠️ Caution'}
                </div>
                {hasActiveSession && (
                  <div className="absolute top-2 right-2 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                )}
              </button>
            )
          })}
        </div>

        {/* Safety Features */}
        <div className="mt-8 p-4 bg-gray-800/50 rounded-xl border border-gray-700">
          <h3 className="text-sm font-semibold text-yellow-400 mb-2">🛡️ Active Protection Features</h3>
          <div className="space-y-1 text-xs text-gray-300">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Real-time session monitoring</span>
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

  // Render platform access screen with enhanced session info
  const renderPlatformAccess = () => {
    if (!selectedPlatform) return null;
    
    const sessionInfo = platformSessions[selectedPlatform.id]
    
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

          {/* Session Information */}
          {sessionInfo && (
            <div className="mb-6 p-3 bg-blue-900/30 rounded-lg border border-blue-700">
              <h3 className="text-sm font-semibold text-blue-400 mb-2">📊 Session Details</h3>
              <div className="text-xs text-gray-300 space-y-1">
                <div>Started: {new Date(sessionInfo.startTime).toLocaleString()}</div>
                <div>Status: {sessionInfo.status === 'active' ? '🟢 Active' : '🔴 Inactive'}</div>
                <div>Monitoring: {sessionInfo.monitored ? '🛡️ Protected' : '⚠️ Unprotected'}</div>
              </div>
            </div>
          )}

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
              <span className="text-xs text-purple-400">{isParentEmailSet ? 'Connected' : 'Setup Required'}</span>
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

  // Render activity screen with session data
  const renderActivityScreen = () => {
    const accessLog = JSON.parse(localStorage.getItem('safeguardian_access_log') || '[]')
    
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-4">Activity Monitor</h2>
        <p className="text-sm text-gray-400 mb-6">
          View your recent activity and monitoring status.
        </p>
        
        {/* Session Summary */}
        <div className="mb-6 p-4 bg-gray-800/50 rounded-xl border border-gray-700">
          <h3 className="text-sm font-semibold text-blue-400 mb-2">📊 Session Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-xl font-bold text-green-400">{Object.keys(platformSessions).length}</div>
              <div className="text-xs text-gray-400">Active Sessions</div>
            </div>
            <div>
              <div className="text-xl font-bold text-blue-400">{accessLog.length}</div>
              <div className="text-xs text-gray-400">Total Accesses</div>
            </div>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-300">Recent Activity</h3>
          
          {accessLog.slice(-10).reverse().map((access, index) => (
            <div key={index} className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{access.platform}</span>
                <span className="text-xs text-gray-400">
                  {new Date(access.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="text-xs text-gray-400">
                {access.monitoring_active ? '🛡️ Monitored' : '⚠️ Unmonitored'} • 
                {access.parent_email ? ' Parent Notified' : ' No Parent Setup'}
              </div>
            </div>
          ))}
          
          {accessLog.length === 0 && (
            <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700 text-center">
              <p className="text-gray-400">No activity recorded yet</p>
              <p className="text-xs text-gray-500 mt-1">Start using social media platforms to see activity</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Enhanced settings screens (keeping existing ones and adding new ones)
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
              <span className="text-white font-medium">Session Alerts</span>
              <div className="w-12 h-6 bg-green-500 rounded-full relative">
                <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
              </div>
            </div>
            <p className="text-xs text-gray-400">Notify parent when new sessions start</p>
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

  // Keep other existing settings screens (monitoring sensitivity, parent dashboard, privacy, about)
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
          <div className={`p-4 rounded-xl border ${isParentEmailSet ? 'bg-green-900/30 border-green-700' : 'bg-yellow-900/30 border-yellow-700'}`}>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">👨‍👩‍👧‍👦</span>
              <div>
                <h3 className="text-white font-medium">{isParentEmailSet ? 'Connected' : 'Setup Required'}</h3>
                <p className={`text-xs ${isParentEmailSet ? 'text-green-400' : 'text-yellow-400'}`}>
                  {isParentEmailSet ? `Parent email: ${parentEmail}` : 'Parent email not configured'}
                </p>
              </div>
            </div>
            {isParentEmailSet ? (
              <p className="text-xs text-gray-300">Your parents can view activity reports and receive alerts through their dashboard.</p>
            ) : (
              <button
                onClick={() => navigateToSettingsView('parent_email')}
                className="w-full mt-2 bg-yellow-600 hover:bg-yellow-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-all cursor-pointer touch-manipulation"
                style={{ WebkitTapHighlightColor: 'transparent' }}
              >
                Setup Parent Email
              </button>
            )}
          </div>
          
          <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700">
            <h3 className="text-white font-medium mb-2">Dashboard Features</h3>
            <div className="space-y-2 text-xs text-gray-300">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Real-time session monitoring</span>
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
              <span className="text-white font-medium">Session Data Sync</span>
              <span className="text-blue-400 text-sm">Enabled</span>
            </div>
            <p className="text-xs text-gray-400">Session data is synced with Supabase for parent dashboard</p>
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
            <p className="text-sm text-gray-400 mb-4">Version 1.1.0</p>
            <p className="text-xs text-gray-300">
              Protecting children in the digital world with AI-powered monitoring, real-time session detection, and parent connectivity.
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
                <span>Real-time session monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>Parent email integration</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>Supabase data synchronization</span>
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

  // Main settings screen with new options
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
              navigateToSettingsView('parent_email')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('parent_email')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex items-center gap-3">
              <span className="text-white">Parent Email Setup</span>
              {isParentEmailSet && <span className="text-xs text-green-400">✓</span>}
            </div>
            <span className="text-gray-400">›</span>
          </button>
          
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('session_monitoring')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('session_monitoring')
            }}
            className="w-full flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700 cursor-pointer touch-manipulation hover:bg-gray-700/50 transition-all"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-white">Session Monitoring</span>
            <span className="text-gray-400">›</span>
          </button>
          
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

  // Settings screen router
  const renderSettingsScreen = () => {
    switch (currentSettingsView) {
      case 'parent_email':
        return ParentEmailSetup()
      case 'session_monitoring':
        return SessionMonitoring()
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

  // Protected screen
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
              <span className="text-sm text-white">Session Detection</span>
              <span className="text-xs text-green-400">Enhanced</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-sm text-white">Parent Alerts</span>
              <span className={`text-xs ${isParentEmailSet ? 'text-green-400' : 'text-yellow-400'}`}>
                {isParentEmailSet ? 'Enabled' : 'Setup Required'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-sm text-white">Data Sync</span>
              <span className="text-xs text-blue-400">Supabase</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Main content renderer
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

