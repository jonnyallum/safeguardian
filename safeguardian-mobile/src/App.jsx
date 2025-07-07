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
    if (email && email.includes('@') && email.includes('.')) {
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
        app_version: '1.1.0'
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
    const [emailInput, setEmailInput] = useState(parentEmail || '')
    const [isValid, setIsValid] = useState(false)
    const [showSuccess, setShowSuccess] = useState(false)

    useEffect(() => {
      setIsValid(emailInput.includes('@') && emailInput.includes('.') && emailInput.length > 5)
    }, [emailInput])

    const handleEmailChange = (e) => {
      const email = e.target.value
      setEmailInput(email)
    }

    const handleSave = (e) => {
      e.preventDefault()
      e.stopPropagation()
      
      if (saveParentEmail(emailInput)) {
        setShowSuccess(true)
        setTimeout(() => {
          setCurrentSettingsView('main')
        }, 1500)
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
          <h2 className="text-lg font-semibold text-white">Parent Email Setup</h2>
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
              onTouchStart={handleSave}
              disabled={!isValid}
              className={`w-full mt-3 py-2 px-4 rounded-lg font-medium transition-all touch-manipulation ${
                isValid 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer' 
                  : 'bg-gray-700 text-gray-400 cursor-not-allowed'
              }`}
              style={{ WebkitTapHighlightColor: 'transparent' }}
            >
              {showSuccess ? '✅ Saved!' : 'Save Parent Email'}
            </button>
          </div>
          
          {isParentEmailSet && !showSuccess && (
            <div className="p-4 bg-green-900/30 rounded-xl border border-green-700">
              <h3 className="text-green-400 font-medium mb-2">✅ Parent Email Connected</h3>
              <p className="text-xs text-gray-300">
                Current: {parentEmail}
              </p>
              <p className="text-xs text-gray-400 mt-2">
                You can update the email address above if needed.
              </p>
            </div>
          )}
          
          {showSuccess && (
            <div className="p-4 bg-green-900/30 rounded-xl border border-green-700 animate-pulse">
              <h3 className="text-green-400 font-medium mb-2">🎉 Success!</h3>
              <p className="text-xs text-gray-300">
                Parent email has been saved and synced successfully.
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
          <h2 className="text-lg font-semibold text-white">Session Monitoring</h2>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
            <h3 className="text-white font-medium mb-2">📊 Active Sessions</h3>
            <p className="text-2xl font-bold text-blue-400">{activeSessions}</p>
            <p className="text-xs text-gray-300">Currently monitored platforms</p>
          </div>
          
          <div className="p-4 bg-purple-900/30 rounded-xl border border-purple-700">
            <h3 className="text-white font-medium mb-2">🔍 Monitoring Status</h3>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-300">
                {isMonitoring ? 'Active Protection' : 'Monitoring Disabled'}
              </span>
            </div>
          </div>
          
          {Object.keys(platformSessions).length > 0 && (
            <div className="p-4 bg-gray-900/30 rounded-xl border border-gray-700">
              <h3 className="text-white font-medium mb-3">📱 Recent Sessions</h3>
              <div className="space-y-2">
                {Object.entries(platformSessions).map(([platformId, session]) => (
                  <div key={platformId} className="flex justify-between items-center p-2 bg-gray-800 rounded">
                    <span className="text-sm text-white">{session.platform}</span>
                    <span className="text-xs text-green-400">{session.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Settings screen component
  const SettingsScreen = () => {
    if (currentSettingsView === 'parent_email') {
      return <ParentEmailSetup />
    }
    
    if (currentSettingsView === 'session_monitoring') {
      return <SessionMonitoring />
    }
    
    if (currentSettingsView === 'notifications') {
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
            <h2 className="text-lg font-semibold text-white">Notification Preferences</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-orange-900/30 rounded-xl border border-orange-700">
              <h3 className="text-white font-medium mb-3">🔔 Alert Settings</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">Threat Alerts</span>
                  <div className="w-12 h-6 bg-green-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">Daily Reports</span>
                  <div className="w-12 h-6 bg-green-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">App Updates</span>
                  <div className="w-12 h-6 bg-gray-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    }
    
    if (currentSettingsView === 'sensitivity') {
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
            <h2 className="text-lg font-semibold text-white">Monitoring Sensitivity</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-purple-900/30 rounded-xl border border-purple-700">
              <h3 className="text-white font-medium mb-3">⚡ Detection Level</h3>
              <div className="space-y-3">
                <div className="p-3 bg-green-800 rounded-lg border-2 border-green-600">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-green-400 rounded-full"></div>
                    <span className="text-white font-medium">Standard</span>
                  </div>
                  <p className="text-xs text-gray-300 mt-1">Balanced protection and privacy</p>
                </div>
                <div className="p-3 bg-gray-800 rounded-lg border border-gray-600">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-gray-400 rounded-full"></div>
                    <span className="text-white">High</span>
                  </div>
                  <p className="text-xs text-gray-300 mt-1">Maximum protection, more alerts</p>
                </div>
                <div className="p-3 bg-gray-800 rounded-lg border border-gray-600">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-gray-400 rounded-full"></div>
                    <span className="text-white">Low</span>
                  </div>
                  <p className="text-xs text-gray-300 mt-1">Basic protection, fewer alerts</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    }
    
    if (currentSettingsView === 'dashboard') {
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
            <h2 className="text-lg font-semibold text-white">Parent Dashboard Access</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-teal-900/30 rounded-xl border border-teal-700">
              <h3 className="text-white font-medium mb-2">🔗 Connection Status</h3>
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-3 h-3 rounded-full ${isParentEmailSet ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-300">
                  {isParentEmailSet ? 'Connected' : 'Not Connected'}
                </span>
              </div>
              {isParentEmailSet && (
                <p className="text-xs text-gray-300">
                  Parent dashboard available at: dashboard.safeguardian.app
                </p>
              )}
            </div>
            
            <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
              <h3 className="text-white font-medium mb-2">📊 Available Features</h3>
              <ul className="text-xs text-gray-300 space-y-1">
                <li>• Real-time activity monitoring</li>
                <li>• Daily usage reports</li>
                <li>• Threat detection alerts</li>
                <li>• Platform access logs</li>
                <li>• Safety recommendations</li>
              </ul>
            </div>
          </div>
        </div>
      )
    }
    
    if (currentSettingsView === 'privacy') {
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
            <h2 className="text-lg font-semibold text-white">Privacy Settings</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-pink-900/30 rounded-xl border border-pink-700">
              <h3 className="text-white font-medium mb-3">🔒 Data Protection</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">Data Encryption</span>
                  <span className="text-xs text-green-400">✅ Enabled</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">Analytics Collection</span>
                  <span className="text-xs text-blue-400">📊 Minimal</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">Data Retention</span>
                  <span className="text-xs text-gray-400">⏰ 30 days</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    }
    
    if (currentSettingsView === 'about') {
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
            <h2 className="text-lg font-semibold text-white">About SafeGuardian</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gray-900/30 rounded-xl border border-gray-700">
              <h3 className="text-white font-medium mb-2">🛡️ SafeGuardian</h3>
              <p className="text-xs text-gray-300 mb-2">Version 1.1.0</p>
              <p className="text-xs text-gray-300 mb-3">
                Advanced child protection app with AI-powered monitoring and real-time threat detection.
              </p>
              
              <div className="space-y-2">
                <h4 className="text-sm text-white font-medium">Key Features:</h4>
                <ul className="text-xs text-gray-300 space-y-1">
                  <li>• Real-time session monitoring</li>
                  <li>• AI-powered threat detection</li>
                  <li>• Automatic parent notifications</li>
                  <li>• Secure evidence collection</li>
                  <li>• Cross-platform protection</li>
                </ul>
              </div>
              
              <div className="mt-4 pt-3 border-t border-gray-600">
                <p className="text-xs text-gray-400">
                  Support: support@safeguardian.app
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    }

    // Main settings screen
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-2 text-white">Settings</h2>
        <p className="text-sm text-gray-300 mb-6">Configure your SafeGuardian protection settings.</p>
        
        <div className="space-y-3">
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
            className="w-full p-4 bg-green-900/30 border border-green-700 rounded-xl text-left hover:bg-green-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">Parent Email Setup</span>
              <span className="text-green-400">›</span>
            </div>
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
            className="w-full p-4 bg-blue-900/30 border border-blue-700 rounded-xl text-left hover:bg-blue-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">Session Monitoring</span>
              <span className="text-blue-400">›</span>
            </div>
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
            className="w-full p-4 bg-orange-900/30 border border-orange-700 rounded-xl text-left hover:bg-orange-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">Notification Preferences</span>
              <span className="text-orange-400">›</span>
            </div>
          </button>
          
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToSettingsView('sensitivity')
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToSettingsView('sensitivity')
            }}
            className="w-full p-4 bg-purple-900/30 border border-purple-700 rounded-xl text-left hover:bg-purple-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">Monitoring Sensitivity</span>
              <span className="text-purple-400">›</span>
            </div>
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
            className="w-full p-4 bg-teal-900/30 border border-teal-700 rounded-xl text-left hover:bg-teal-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">Parent Dashboard Access</span>
              <span className="text-teal-400">›</span>
            </div>
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
            className="w-full p-4 bg-pink-900/30 border border-pink-700 rounded-xl text-left hover:bg-pink-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">Privacy Settings</span>
              <span className="text-pink-400">›</span>
            </div>
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
            className="w-full p-4 bg-gray-900/30 border border-gray-700 rounded-xl text-left hover:bg-gray-900/50 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">About SafeGuardian</span>
              <span className="text-gray-400">›</span>
            </div>
          </button>
        </div>
      </div>
    )
  }

  // Platform access screen
  const PlatformAccessScreen = () => {
    if (!selectedPlatform) return null

    const currentSession = platformSessions[selectedPlatform.id]
    const sessionStartTime = currentSession?.startTime ? new Date(currentSession.startTime).toLocaleTimeString() : new Date().toLocaleTimeString()

    return (
      <div className="px-6">
        <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${selectedPlatform.color} flex items-center justify-center`}>
          <span className="text-2xl">{selectedPlatform.icon}</span>
        </div>
        
        <h2 className="text-xl font-bold text-center mb-2 text-white">Accessing {selectedPlatform.name}</h2>
        <p className="text-sm text-gray-300 text-center mb-6">SafeGuardian is now monitoring your session for safety</p>
        
        <div className="space-y-4 mb-6">
          <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
            <h3 className="text-white font-medium mb-2 flex items-center gap-2">
              📊 Session Details
            </h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-300">Started:</span>
                <span className="text-white">{sessionStartTime}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Status:</span>
                <span className="text-green-400 flex items-center gap-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  Active
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Monitoring:</span>
                <span className="text-blue-400 flex items-center gap-1">
                  🛡️ Protected
                </span>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-green-900/30 rounded-xl border border-green-700">
            <h3 className="text-green-400 font-medium mb-2 flex items-center gap-2">
              🔒 Secure Connection
            </h3>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-300">Protection Status</span>
              <span className="text-green-400 text-sm font-medium">Active</span>
            </div>
          </div>
          
          <div className="p-4 bg-purple-900/30 rounded-xl border border-purple-700">
            <h3 className="text-purple-400 font-medium mb-2 flex items-center gap-2">
              🤖 AI Monitoring
            </h3>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-300">Threat Detection</span>
              <span className="text-purple-400 text-sm font-medium">Scanning</span>
            </div>
          </div>
          
          <div className="p-4 bg-orange-900/30 rounded-xl border border-orange-700">
            <h3 className="text-orange-400 font-medium mb-2 flex items-center gap-2">
              📧 Parent Dashboard
            </h3>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-300">Connection</span>
              <span className={`text-sm font-medium ${isParentEmailSet ? 'text-green-400' : 'text-orange-400'}`}>
                {isParentEmailSet ? 'Connected' : 'Setup Required'}
              </span>
            </div>
          </div>
        </div>
        
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
            className={`w-full py-3 px-4 rounded-xl font-medium transition-all cursor-pointer touch-manipulation bg-gradient-to-r ${selectedPlatform.color} text-white hover:opacity-90`}
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
            className="w-full py-2 px-4 rounded-xl font-medium bg-gray-700 text-gray-300 hover:bg-gray-600 transition-all cursor-pointer touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            Choose Different Platform
          </button>
        </div>
      </div>
    )
  }

  // Activity screen
  const ActivityScreen = () => {
    const accessLog = JSON.parse(localStorage.getItem('safeguardian_access_log') || '[]')
    const recentAccess = accessLog.slice(-10).reverse()

    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-2 text-white">Activity Monitor</h2>
        <p className="text-sm text-gray-300 mb-6">Track your social media usage and safety metrics.</p>
        
        <div className="space-y-4">
          <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
            <h3 className="text-white font-medium mb-2">📊 Today's Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-2xl font-bold text-blue-400">{Object.keys(platformSessions).length}</p>
                <p className="text-xs text-gray-300">Active Sessions</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-400">{recentAccess.length}</p>
                <p className="text-xs text-gray-300">Platform Accesses</p>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-green-900/30 rounded-xl border border-green-700">
            <h3 className="text-white font-medium mb-2">🛡️ Safety Status</h3>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">All platforms safe • No threats detected</span>
            </div>
          </div>
          
          {recentAccess.length > 0 && (
            <div className="p-4 bg-gray-900/30 rounded-xl border border-gray-700">
              <h3 className="text-white font-medium mb-3">📱 Recent Activity</h3>
              <div className="space-y-2">
                {recentAccess.map((access, index) => (
                  <div key={index} className="flex justify-between items-center p-2 bg-gray-800 rounded">
                    <div>
                      <span className="text-sm text-white">{access.platform}</span>
                      <p className="text-xs text-gray-400">
                        {new Date(access.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                    <span className="text-xs text-green-400">✅ Safe</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Protected screen
  const ProtectedScreen = () => {
    return (
      <div className="px-6">
        <h2 className="text-lg font-semibold mb-2 text-white">Protected Mode</h2>
        <p className="text-sm text-gray-300 mb-6">Advanced protection features and safety controls.</p>
        
        <div className="space-y-4">
          <div className="p-4 bg-green-900/30 rounded-xl border border-green-700">
            <h3 className="text-white font-medium mb-2">🛡️ Protection Status</h3>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 font-medium">Fully Protected</span>
            </div>
            <p className="text-xs text-gray-300">
              All social media platforms are being monitored with AI-powered threat detection.
            </p>
          </div>
          
          <div className="p-4 bg-blue-900/30 rounded-xl border border-blue-700">
            <h3 className="text-white font-medium mb-2">🔍 Active Monitoring</h3>
            <ul className="text-xs text-gray-300 space-y-1">
              <li>• Real-time content scanning</li>
              <li>• Inappropriate contact detection</li>
              <li>• Cyberbullying prevention</li>
              <li>• Privacy protection alerts</li>
            </ul>
          </div>
          
          <div className="p-4 bg-purple-900/30 rounded-xl border border-purple-700">
            <h3 className="text-white font-medium mb-2">📊 Safety Metrics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xl font-bold text-purple-400">0</p>
                <p className="text-xs text-gray-300">Threats Blocked</p>
              </div>
              <div>
                <p className="text-xl font-bold text-green-400">100%</p>
                <p className="text-xs text-gray-300">Safety Score</p>
              </div>
            </div>
          </div>
          
          {isParentEmailSet && (
            <div className="p-4 bg-orange-900/30 rounded-xl border border-orange-700">
              <h3 className="text-white font-medium mb-2">📧 Parent Notifications</h3>
              <p className="text-xs text-gray-300 mb-2">
                Connected to: {parentEmail}
              </p>
              <p className="text-xs text-gray-400">
                Parents receive real-time alerts and daily safety reports.
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Main home screen
  const HomeScreen = () => {
    if (selectedPlatform) {
      return <PlatformAccessScreen />
    }

    return (
      <div className="px-6">
        <h2 className="text-xl font-bold mb-2 text-white">Choose Your Platform</h2>
        <p className="text-sm text-gray-300 mb-6">Access your social media safely. SafeGuardian is monitoring for your protection.</p>
        
        <div className="grid grid-cols-2 gap-4 mb-6">
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
                className={`relative p-4 rounded-2xl bg-gradient-to-br ${platform.color} text-white hover:scale-105 transition-all cursor-pointer touch-manipulation`}
                style={{ WebkitTapHighlightColor: 'transparent' }}
              >
                {hasActiveSession && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-gray-900 animate-pulse"></div>
                )}
                <div className="text-2xl mb-2">{platform.icon}</div>
                <div className="text-sm font-medium">{platform.name}</div>
                <div className="text-xs opacity-80 flex items-center gap-1 mt-1">
                  ✅ Safe
                </div>
              </button>
            )
          })}
        </div>
        
        <div className="p-4 bg-gray-900/50 rounded-xl border border-gray-700">
          <h3 className="text-yellow-400 font-medium mb-2 flex items-center gap-2">
            🛡️ Active Protection Features
          </h3>
          <ul className="text-xs text-gray-300 space-y-1">
            <li>• Real-time session monitoring</li>
            <li>• AI-powered threat detection</li>
            <li>• Automatic parent notifications</li>
            <li>• Secure evidence collection</li>
          </ul>
        </div>
      </div>
    )
  }

  // Navigation component
  const Navigation = () => (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 px-4 py-2">
      <div className="flex justify-around">
        {[
          { id: 'home', icon: '🏠', label: 'Home' },
          { id: 'activity', icon: '📊', label: 'Activity' },
          { id: 'protected', icon: '🛡️', label: 'Protected' },
          { id: 'settings', icon: '⚙️', label: 'Settings' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigateToTab(tab.id)
            }}
            onTouchStart={(e) => {
              e.preventDefault()
              navigateToTab(tab.id)
            }}
            className={`flex flex-col items-center py-2 px-3 rounded-lg transition-all cursor-pointer touch-manipulation ${
              activeTab === tab.id 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            <span className="text-lg mb-1">{tab.icon}</span>
            <span className="text-xs">{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  )

  // Main render
  return (
    <div className="min-h-screen bg-gray-900 text-white pb-20">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-yellow-500 rounded-xl flex items-center justify-center">
            <span className="text-xl">🛡️</span>
          </div>
          <div>
            <h1 className="text-lg font-bold">SafeGuardian</h1>
            <p className="text-xs text-gray-400">Protected Access</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Status</p>
          <p className="text-sm font-medium text-green-400">Protected</p>
        </div>
      </div>

      {/* Monitoring Indicator */}
      <div className="px-6 pt-4">
        <MonitoringIndicator />
      </div>

      {/* Main Content */}
      <div className="flex-1">
        {activeTab === 'home' && <HomeScreen />}
        {activeTab === 'activity' && <ActivityScreen />}
        {activeTab === 'protected' && <ProtectedScreen />}
        {activeTab === 'settings' && <SettingsScreen />}
      </div>

      {/* Navigation */}
      <Navigation />
    </div>
  )
}

export default App

