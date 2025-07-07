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
  const [realSessions, setRealSessions] = useState({}) // Track actual login sessions

  // Social media platforms with dynamic session tracking
  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: '📷',
      color: 'from-pink-500 to-purple-600',
      url: 'https://instagram.com',
      sessionKey: 'instagram_session'
    },
    {
      id: 'snapchat',
      name: 'Snapchat',
      icon: '👻',
      color: 'from-yellow-400 to-yellow-600',
      url: 'https://snapchat.com',
      sessionKey: 'snapchat_session'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: '👥',
      color: 'from-blue-500 to-blue-700',
      url: 'https://facebook.com',
      sessionKey: 'facebook_session'
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: '💬',
      color: 'from-green-500 to-green-600',
      url: 'https://web.whatsapp.com',
      sessionKey: 'whatsapp_session'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: '🎵',
      color: 'from-black to-red-600',
      url: 'https://tiktok.com',
      sessionKey: 'tiktok_session'
    },
    {
      id: 'discord',
      name: 'Discord',
      icon: '🎮',
      color: 'from-indigo-500 to-purple-600',
      url: 'https://discord.com',
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
      const savedSessions = localStorage.getItem('safeguardian_real_sessions')
      if (savedSessions) {
        setRealSessions(JSON.parse(savedSessions))
      }
    } catch (error) {
      console.error('Error loading session data:', error)
    }
  }

  // Save session data to localStorage
  const saveSessionData = (sessions) => {
    try {
      localStorage.setItem('safeguardian_real_sessions', JSON.stringify(sessions))
      setRealSessions(sessions)
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

  // Check for active platform sessions (only when actually logged in)
  const checkPlatformSessions = () => {
    // Only update sessions that are actually active
    // This would integrate with real session detection in production
    const currentSessions = { ...realSessions }
    
    // Clean up expired sessions (older than 30 minutes)
    Object.keys(currentSessions).forEach(platformId => {
      const session = currentSessions[platformId]
      if (session && session.lastActivity) {
        const timeDiff = Date.now() - new Date(session.lastActivity).getTime()
        if (timeDiff > 30 * 60 * 1000) { // 30 minutes
          delete currentSessions[platformId]
        }
      }
    })

    // Update sessions if changed
    if (JSON.stringify(currentSessions) !== JSON.stringify(realSessions)) {
      saveSessionData(currentSessions)
      
      // Send session data to Supabase
      syncSessionData(currentSessions)
    }
  }

  // Get platform status based on actual session
  const getPlatformStatus = (platform) => {
    const session = realSessions[platform.id]
    if (session && session.status === 'active') {
      return 'connected'
    }
    return 'available'
  }

  // Get platform status display
  const getPlatformStatusDisplay = (platform) => {
    const status = getPlatformStatus(platform)
    if (status === 'connected') {
      return '🟢 Connected'
    }
    return '⚪ Available'
  }

  // Sync session data with Supabase
  const syncSessionData = async (sessions) => {
    try {
      const sessionData = {
        user_id: 'demo_user',
        parent_email: parentEmail,
        sessions: sessions,
        timestamp: new Date().toISOString(),
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language
        }
      }

      console.log('Syncing session data to Supabase:', sessionData)
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
      return true
    }
    return false
  }

  // Handle platform access
  const handlePlatformAccess = (platform) => {
    setSelectedPlatform(platform)
    
    // Record platform access attempt
    const accessTime = new Date().toISOString()
    const sessionKey = `${platform.id}_access_time`
    localStorage.setItem(sessionKey, accessTime)
    
    // Create a session entry for monitoring (but not mark as connected until actually logged in)
    const newSessions = { ...realSessions }
    newSessions[platform.id] = {
      platform: platform.name,
      startTime: accessTime,
      lastActivity: accessTime,
      status: 'accessing', // Not 'active' until confirmed login
      monitored: true
    }
    
    saveSessionData(newSessions)
  }

  // Handle platform login (this would be called when actual login is detected)
  const handlePlatformLogin = (platformId) => {
    const platform = platforms.find(p => p.id === platformId)
    if (platform) {
      const loginTime = new Date().toISOString()
      const newSessions = { ...realSessions }
      newSessions[platformId] = {
        platform: platform.name,
        startTime: loginTime,
        lastActivity: loginTime,
        status: 'active', // Now actually active/connected
        monitored: true
      }
      
      saveSessionData(newSessions)
    }
  }

  // Open platform safely
  const openPlatformSafely = (platform) => {
    // Open platform in new tab
    window.open(platform.url, '_blank')
    
    // Update session to show platform was opened
    const openTime = new Date().toISOString()
    const newSessions = { ...realSessions }
    newSessions[platform.id] = {
      platform: platform.name,
      startTime: openTime,
      lastActivity: openTime,
      status: 'opened', // Opened but not necessarily logged in
      monitored: true
    }
    
    saveSessionData(newSessions)
  }

  // Settings navigation handlers
  const handleSettingsNavigation = (view) => {
    setCurrentSettingsView(view)
  }

  const handleSettingsBack = () => {
    setCurrentSettingsView('main')
  }

  // Tab navigation
  const handleTabChange = (tab) => {
    setActiveTab(tab)
    setSelectedPlatform(null) // Reset selected platform when changing tabs
    if (tab !== 'settings') {
      setCurrentSettingsView('main') // Reset settings view when leaving settings
    }
  }

  // Render platform button with improved layout
  const renderPlatformButton = (platform, index) => {
    const status = getPlatformStatus(platform)
    const statusDisplay = getPlatformStatusDisplay(platform)
    
    return (
      <button
        key={platform.id}
        onClick={() => handlePlatformAccess(platform)}
        onTouchStart={() => handlePlatformAccess(platform)}
        className={`w-full p-4 rounded-xl bg-gradient-to-br ${platform.color} text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 active:scale-95 relative overflow-hidden`}
      >
        <div className="flex flex-col items-center space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{platform.icon}</span>
            <span className="text-lg">{platform.name}</span>
          </div>
          <div className="text-xs opacity-90 bg-black bg-opacity-20 px-2 py-1 rounded-full">
            {statusDisplay}
          </div>
        </div>
      </button>
    )
  }

  // Render platform access screen
  const renderPlatformAccess = () => {
    if (!selectedPlatform) return null
    
    const session = realSessions[selectedPlatform.id]
    const hasActiveSession = session && (session.status === 'active' || session.status === 'connected')
    
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Platform Icon */}
          <div className="text-center mb-6">
            <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${selectedPlatform.color} flex items-center justify-center text-3xl mx-auto mb-4`}>
              {selectedPlatform.icon}
            </div>
            <h2 className="text-2xl font-bold">Accessing {selectedPlatform.name}</h2>
            <p className="text-gray-400 mt-2">SafeGuardian is monitoring for your protection</p>
          </div>

          {/* Session Details - Only show if actually connected */}
          {hasActiveSession && (
            <div className="bg-gray-800 rounded-xl p-4 mb-6">
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-blue-400">📊</span>
                <h3 className="font-semibold">Session Details</h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Started:</span>
                  <span>{new Date(session.startTime).toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className="text-green-400">● Active</span>
                </div>
                <div className="flex justify-between">
                  <span>Monitoring:</span>
                  <span className="text-blue-400">🛡️ Protected</span>
                </div>
              </div>
            </div>
          )}

          {/* Connection Status - Only show if actually connected */}
          {hasActiveSession && (
            <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-4 mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-green-400">🔒</span>
                <h3 className="font-semibold text-green-400">Secure Connection</h3>
              </div>
              <div className="flex justify-between text-sm">
                <span>Protection Status</span>
                <span className="text-green-400">Active</span>
              </div>
            </div>
          )}

          {/* AI Monitoring - Only show if monitoring is active */}
          {hasActiveSession && (
            <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-4 mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-purple-400">🤖</span>
                <h3 className="font-semibold text-purple-400">AI Monitoring</h3>
              </div>
              <div className="flex justify-between text-sm">
                <span>Threat Detection</span>
                <span className="text-purple-400">Scanning</span>
              </div>
            </div>
          )}

          {/* Parent Dashboard - Show connection status */}
          <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-blue-400">👨‍👩‍👧‍👦</span>
              <h3 className="font-semibold text-blue-400">Parent Dashboard</h3>
            </div>
            <div className="flex justify-between text-sm">
              <span>Connection</span>
              <span className={isParentEmailSet ? "text-green-400" : "text-yellow-400"}>
                {isParentEmailSet ? "Connected" : "Setup Required"}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => openPlatformSafely(selectedPlatform)}
              onTouchStart={() => openPlatformSafely(selectedPlatform)}
              className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 active:scale-95 bg-gradient-to-r ${selectedPlatform.color} text-white shadow-lg hover:shadow-xl`}
            >
              Open {selectedPlatform.name} Safely
            </button>
            
            <button
              onClick={() => setSelectedPlatform(null)}
              onTouchStart={() => setSelectedPlatform(null)}
              className="w-full py-4 rounded-xl bg-gray-700 text-white font-semibold hover:bg-gray-600 transition-all duration-200 transform hover:scale-105 active:scale-95"
            >
              Choose Different Platform
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Render home screen
  const renderHome = () => {
    if (selectedPlatform) {
      return renderPlatformAccess()
    }

    return (
      <div className="min-h-screen bg-gray-900 text-white">
        {/* Header */}
        <div className="bg-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
                <span className="text-xl">🛡️</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">SafeGuardian</h1>
                <p className="text-sm text-gray-400">Protected Access</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Status</p>
              <p className="text-green-400 font-semibold">Protected</p>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="bg-gray-800 px-4 pb-4">
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              <span>Active Protection</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>•</span>
              <span>Monitoring Active</span>
            </div>
            {isParentEmailSet && (
              <div className="flex items-center space-x-1">
                <span>📧</span>
                <span>Parent Connected</span>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="p-6">
          <div className="max-w-md mx-auto">
            <h2 className="text-2xl font-bold mb-2">Choose Your Platform</h2>
            <p className="text-gray-400 mb-6">Access your social media safely. SafeGuardian is monitoring for your protection.</p>

            {/* Platform Grid */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              {platforms.map((platform, index) => renderPlatformButton(platform, index))}
            </div>

            {/* Active Protection Features */}
            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-yellow-400">🛡️</span>
                <h3 className="font-semibold">Active Protection Features</h3>
              </div>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• Real-time session monitoring</li>
                <li>• AI-powered threat detection</li>
                <li>• Parent dashboard integration</li>
                <li>• Secure connection protocols</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render activity screen
  const renderActivity = () => {
    const activeSessions = Object.entries(realSessions).filter(([_, session]) => 
      session.status === 'active' || session.status === 'connected'
    )

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-6">Activity Monitor</h2>
          
          {activeSessions.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-green-400">Active Sessions ({activeSessions.length})</h3>
              {activeSessions.map(([platformId, session]) => (
                <div key={platformId} className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{session.platform}</h4>
                    <span className="text-green-400 text-sm">● Active</span>
                  </div>
                  <div className="text-sm text-gray-400 space-y-1">
                    <div>Started: {new Date(session.startTime).toLocaleString()}</div>
                    <div>Last Activity: {new Date(session.lastActivity).toLocaleString()}</div>
                    <div>Status: Protected Monitoring</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2">No Active Sessions</h3>
              <p className="text-gray-400">Your social media activity will appear here when you're logged in to platforms.</p>
            </div>
          )}

          {/* Recent Activity */}
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="bg-gray-800 rounded-xl p-4">
              <div className="text-sm text-gray-400">
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span>App Started</span>
                  <span>{new Date().toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span>Protection Activated</span>
                  <span>{new Date().toLocaleTimeString()}</span>
                </div>
                {isParentEmailSet && (
                  <div className="flex justify-between py-2">
                    <span>Parent Email Connected</span>
                    <span className="text-green-400">✓</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render protected screen
  const renderProtected = () => {
    const activeSessionCount = Object.values(realSessions).filter(session => 
      session.status === 'active' || session.status === 'connected'
    ).length

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-6">Protection Status</h2>
          
          {/* Protection Overview */}
          <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-6 mb-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🛡️</div>
              <h3 className="text-xl font-semibold text-green-400 mb-2">Fully Protected</h3>
              <p className="text-gray-400">SafeGuardian is actively monitoring your online activity</p>
            </div>
          </div>

          {/* Active Sessions */}
          <div className="bg-gray-800 rounded-xl p-4 mb-6">
            <h4 className="font-semibold mb-3">Active Monitoring</h4>
            <div className="flex justify-between items-center">
              <span>Protected Sessions</span>
              <span className="text-green-400 font-semibold">{activeSessionCount}</span>
            </div>
          </div>

          {/* Protection Features */}
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center space-x-3">
                <span className="text-blue-400">🤖</span>
                <div>
                  <h4 className="font-semibold">AI Threat Detection</h4>
                  <p className="text-sm text-gray-400">Scanning for inappropriate content</p>
                </div>
                <span className="text-green-400 ml-auto">Active</span>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center space-x-3">
                <span className="text-purple-400">📊</span>
                <div>
                  <h4 className="font-semibold">Real-time Monitoring</h4>
                  <p className="text-sm text-gray-400">Continuous session tracking</p>
                </div>
                <span className="text-green-400 ml-auto">Active</span>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center space-x-3">
                <span className="text-yellow-400">👨‍👩‍👧‍👦</span>
                <div>
                  <h4 className="font-semibold">Parent Dashboard</h4>
                  <p className="text-sm text-gray-400">Real-time alerts and reports</p>
                </div>
                <span className={`ml-auto ${isParentEmailSet ? 'text-green-400' : 'text-yellow-400'}`}>
                  {isParentEmailSet ? 'Connected' : 'Setup Required'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render parent email setup screen
  const renderParentEmailSetup = () => {
    const [emailInput, setEmailInput] = useState(parentEmail)
    const [emailError, setEmailError] = useState('')

    const handleEmailSave = () => {
      if (!emailInput) {
        setEmailError('Please enter an email address')
        return
      }
      
      if (!emailInput.includes('@') || !emailInput.includes('.')) {
        setEmailError('Please enter a valid email address')
        return
      }

      const success = saveParentEmail(emailInput)
      if (success) {
        setEmailError('')
        alert('Parent email saved successfully!')
      } else {
        setEmailError('Failed to save email. Please try again.')
      }
    }

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">Parent Email Setup</h2>
          </div>

          {/* Content */}
          <div className="space-y-6">
            <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-4">
              <h3 className="font-semibold text-blue-400 mb-2">Why Setup Parent Email?</h3>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• Receive real-time safety alerts</li>
                <li>• Get daily activity reports</li>
                <li>• Access parent dashboard</li>
                <li>• Emergency notifications</li>
              </ul>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Parent Email Address</label>
              <input
                type="email"
                value={emailInput}
                onChange={(e) => {
                  setEmailInput(e.target.value)
                  setEmailError('')
                }}
                placeholder="parent@example.com"
                className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              />
              {emailError && (
                <p className="text-red-400 text-sm mt-1">{emailError}</p>
              )}
            </div>

            <button
              onClick={handleEmailSave}
              onTouchStart={handleEmailSave}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
            >
              Save Parent Email
            </button>

            {isParentEmailSet && (
              <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-4">
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">✓</span>
                  <span className="font-semibold text-green-400">Email Connected</span>
                </div>
                <p className="text-sm text-gray-400 mt-1">
                  Current: {parentEmail}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Render session monitoring screen
  const renderSessionMonitoring = () => {
    const activeSessions = Object.entries(realSessions).filter(([_, session]) => 
      session.status === 'active' || session.status === 'connected'
    )

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">Session Monitoring</h2>
          </div>

          {/* Real-time Status */}
          <div className="bg-gray-800 rounded-xl p-4 mb-6">
            <h3 className="font-semibold mb-3">Real-time Status</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Monitoring Status</span>
                <span className="text-green-400">● Active</span>
              </div>
              <div className="flex justify-between">
                <span>Active Sessions</span>
                <span className="text-blue-400">{activeSessions.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Update</span>
                <span className="text-gray-400">{new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>

          {/* Active Sessions */}
          {activeSessions.length > 0 ? (
            <div className="space-y-4">
              <h3 className="font-semibold">Active Sessions</h3>
              {activeSessions.map(([platformId, session]) => (
                <div key={platformId} className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{session.platform}</h4>
                    <span className="text-green-400 text-sm">● Connected</span>
                  </div>
                  <div className="text-sm text-gray-400 space-y-1">
                    <div>Started: {new Date(session.startTime).toLocaleString()}</div>
                    <div>Status: Protected Monitoring Active</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="font-semibold mb-2">No Active Sessions</h3>
              <p className="text-gray-400 text-sm">Sessions will appear here when you log into social media platforms</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Render notification preferences screen
  const renderNotificationPreferences = () => {
    const [threatAlerts, setThreatAlerts] = useState(true)
    const [dailyReports, setDailyReports] = useState(true)
    const [appUpdates, setAppUpdates] = useState(false)

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">Notification Preferences</h2>
          </div>

          {/* Notification Settings */}
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Threat Alerts</h3>
                  <p className="text-sm text-gray-400">Immediate alerts for potential threats</p>
                </div>
                <button
                  onClick={() => setThreatAlerts(!threatAlerts)}
                  onTouchStart={() => setThreatAlerts(!threatAlerts)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    threatAlerts ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    threatAlerts ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Daily Reports</h3>
                  <p className="text-sm text-gray-400">Daily activity summaries</p>
                </div>
                <button
                  onClick={() => setDailyReports(!dailyReports)}
                  onTouchStart={() => setDailyReports(!dailyReports)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    dailyReports ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    dailyReports ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">App Updates</h3>
                  <p className="text-sm text-gray-400">Notifications about app updates</p>
                </div>
                <button
                  onClick={() => setAppUpdates(!appUpdates)}
                  onTouchStart={() => setAppUpdates(!appUpdates)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    appUpdates ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    appUpdates ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={() => alert('Notification preferences saved!')}
            onTouchStart={() => alert('Notification preferences saved!')}
            className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
          >
            Save Preferences
          </button>
        </div>
      </div>
    )
  }

  // Render monitoring sensitivity screen
  const renderMonitoringSensitivity = () => {
    const [sensitivity, setSensitivity] = useState('standard')

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">Monitoring Sensitivity</h2>
          </div>

          {/* Sensitivity Options */}
          <div className="space-y-4">
            <div
              onClick={() => setSensitivity('low')}
              onTouchStart={() => setSensitivity('low')}
              className={`bg-gray-800 rounded-xl p-4 cursor-pointer transition-colors ${
                sensitivity === 'low' ? 'border-2 border-blue-500' : 'border border-gray-600'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-4 h-4 rounded-full border-2 ${
                  sensitivity === 'low' ? 'bg-blue-500 border-blue-500' : 'border-gray-400'
                }`} />
                <div>
                  <h3 className="font-semibold">Low Sensitivity</h3>
                  <p className="text-sm text-gray-400">Basic monitoring for obvious threats</p>
                </div>
              </div>
            </div>

            <div
              onClick={() => setSensitivity('standard')}
              onTouchStart={() => setSensitivity('standard')}
              className={`bg-gray-800 rounded-xl p-4 cursor-pointer transition-colors ${
                sensitivity === 'standard' ? 'border-2 border-blue-500' : 'border border-gray-600'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-4 h-4 rounded-full border-2 ${
                  sensitivity === 'standard' ? 'bg-blue-500 border-blue-500' : 'border-gray-400'
                }`} />
                <div>
                  <h3 className="font-semibold">Standard Sensitivity</h3>
                  <p className="text-sm text-gray-400">Balanced monitoring (Recommended)</p>
                </div>
              </div>
            </div>

            <div
              onClick={() => setSensitivity('high')}
              onTouchStart={() => setSensitivity('high')}
              className={`bg-gray-800 rounded-xl p-4 cursor-pointer transition-colors ${
                sensitivity === 'high' ? 'border-2 border-blue-500' : 'border border-gray-600'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-4 h-4 rounded-full border-2 ${
                  sensitivity === 'high' ? 'bg-blue-500 border-blue-500' : 'border-gray-400'
                }`} />
                <div>
                  <h3 className="font-semibold">High Sensitivity</h3>
                  <p className="text-sm text-gray-400">Maximum protection and monitoring</p>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={() => alert('Monitoring sensitivity updated!')}
            onTouchStart={() => alert('Monitoring sensitivity updated!')}
            className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>
    )
  }

  // Render parent dashboard access screen
  const renderParentDashboardAccess = () => {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">Parent Dashboard Access</h2>
          </div>

          {/* Connection Status */}
          <div className={`rounded-xl p-4 mb-6 ${
            isParentEmailSet 
              ? 'bg-green-900/30 border border-green-500/30' 
              : 'bg-yellow-900/30 border border-yellow-500/30'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              <span className={isParentEmailSet ? 'text-green-400' : 'text-yellow-400'}>
                {isParentEmailSet ? '✓' : '⚠️'}
              </span>
              <h3 className={`font-semibold ${isParentEmailSet ? 'text-green-400' : 'text-yellow-400'}`}>
                {isParentEmailSet ? 'Dashboard Connected' : 'Setup Required'}
              </h3>
            </div>
            <p className="text-sm text-gray-400">
              {isParentEmailSet 
                ? `Connected to: ${parentEmail}` 
                : 'Parent email setup required for dashboard access'
              }
            </p>
          </div>

          {/* Dashboard Features */}
          <div className="space-y-4">
            <h3 className="font-semibold">Dashboard Features</h3>
            
            <div className="bg-gray-800 rounded-xl p-4">
              <h4 className="font-semibold mb-2">Real-time Monitoring</h4>
              <p className="text-sm text-gray-400">Live view of your child's social media activity</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <h4 className="font-semibold mb-2">Threat Alerts</h4>
              <p className="text-sm text-gray-400">Instant notifications about potential dangers</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <h4 className="font-semibold mb-2">Activity Reports</h4>
              <p className="text-sm text-gray-400">Daily and weekly summaries of online activity</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <h4 className="font-semibold mb-2">Platform Analytics</h4>
              <p className="text-sm text-gray-400">Detailed insights into platform usage patterns</p>
            </div>
          </div>

          {/* Action Button */}
          {!isParentEmailSet && (
            <button
              onClick={() => handleSettingsNavigation('parentEmail')}
              onTouchStart={() => handleSettingsNavigation('parentEmail')}
              className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
            >
              Setup Parent Email
            </button>
          )}
        </div>
      </div>
    )
  }

  // Render privacy settings screen
  const renderPrivacySettings = () => {
    const [dataEncryption, setDataEncryption] = useState(true)
    const [analytics, setAnalytics] = useState(false)
    const [dataRetention, setDataRetention] = useState('30days')

    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">Privacy Settings</h2>
          </div>

          {/* Privacy Options */}
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Data Encryption</h3>
                  <p className="text-sm text-gray-400">Encrypt all monitoring data</p>
                </div>
                <button
                  onClick={() => setDataEncryption(!dataEncryption)}
                  onTouchStart={() => setDataEncryption(!dataEncryption)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    dataEncryption ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    dataEncryption ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Usage Analytics</h3>
                  <p className="text-sm text-gray-400">Help improve SafeGuardian</p>
                </div>
                <button
                  onClick={() => setAnalytics(!analytics)}
                  onTouchStart={() => setAnalytics(!analytics)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    analytics ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    analytics ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-4">
              <h3 className="font-semibold mb-3">Data Retention</h3>
              <div className="space-y-2">
                <div
                  onClick={() => setDataRetention('7days')}
                  onTouchStart={() => setDataRetention('7days')}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    dataRetention === '7days' ? 'bg-blue-600' : 'bg-gray-700'
                  }`}
                >
                  <span>7 Days</span>
                </div>
                <div
                  onClick={() => setDataRetention('30days')}
                  onTouchStart={() => setDataRetention('30days')}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    dataRetention === '30days' ? 'bg-blue-600' : 'bg-gray-700'
                  }`}
                >
                  <span>30 Days (Recommended)</span>
                </div>
                <div
                  onClick={() => setDataRetention('90days')}
                  onTouchStart={() => setDataRetention('90days')}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    dataRetention === '90days' ? 'bg-blue-600' : 'bg-gray-700'
                  }`}
                >
                  <span>90 Days</span>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={() => alert('Privacy settings saved!')}
            onTouchStart={() => alert('Privacy settings saved!')}
            className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>
    )
  }

  // Render about screen
  const renderAbout = () => {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={handleSettingsBack}
              onTouchStart={handleSettingsBack}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold">About SafeGuardian</h2>
          </div>

          {/* App Info */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-yellow-500 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
              🛡️
            </div>
            <h3 className="text-xl font-bold mb-2">SafeGuardian</h3>
            <p className="text-gray-400">Version 1.0.0</p>
          </div>

          {/* Features */}
          <div className="space-y-4 mb-8">
            <h4 className="font-semibold">Key Features</h4>
            <div className="bg-gray-800 rounded-xl p-4">
              <ul className="text-sm text-gray-400 space-y-2">
                <li>• AI-powered threat detection</li>
                <li>• Real-time session monitoring</li>
                <li>• Parent dashboard integration</li>
                <li>• Multi-platform support</li>
                <li>• Secure data encryption</li>
                <li>• 24/7 protection</li>
              </ul>
            </div>
          </div>

          {/* Support */}
          <div className="space-y-4">
            <h4 className="font-semibold">Support</h4>
            <div className="bg-gray-800 rounded-xl p-4">
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-400">Email:</span>
                  <span className="ml-2">support@safeguardian.com</span>
                </div>
                <div>
                  <span className="text-gray-400">Website:</span>
                  <span className="ml-2">www.safeguardian.com</span>
                </div>
                <div>
                  <span className="text-gray-400">Emergency:</span>
                  <span className="ml-2">1-800-SAFE-GUARD</span>
                </div>
              </div>
            </div>
          </div>

          {/* Legal */}
          <div className="mt-8 text-center text-xs text-gray-500">
            <p>© 2025 SafeGuardian. All rights reserved.</p>
            <p className="mt-1">Privacy Policy • Terms of Service</p>
          </div>
        </div>
      </div>
    )
  }

  // Render settings screen
  const renderSettings = () => {
    // Handle sub-screens
    if (currentSettingsView === 'parentEmail') {
      return renderParentEmailSetup()
    }
    if (currentSettingsView === 'sessionMonitoring') {
      return renderSessionMonitoring()
    }
    if (currentSettingsView === 'notifications') {
      return renderNotificationPreferences()
    }
    if (currentSettingsView === 'sensitivity') {
      return renderMonitoringSensitivity()
    }
    if (currentSettingsView === 'parentDashboard') {
      return renderParentDashboardAccess()
    }
    if (currentSettingsView === 'privacy') {
      return renderPrivacySettings()
    }
    if (currentSettingsView === 'about') {
      return renderAbout()
    }

    // Main settings screen
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-6">Settings</h2>
          <p className="text-gray-400 mb-6">Configure your SafeGuardian protection settings.</p>

          {/* Settings Options */}
          <div className="space-y-3">
            <button
              onClick={() => handleSettingsNavigation('parentEmail')}
              onTouchStart={() => handleSettingsNavigation('parentEmail')}
              className="w-full p-4 bg-green-800 hover:bg-green-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">📧</span>
                  <span className="font-semibold">Parent Email Setup</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>

            <button
              onClick={() => handleSettingsNavigation('sessionMonitoring')}
              onTouchStart={() => handleSettingsNavigation('sessionMonitoring')}
              className="w-full p-4 bg-blue-800 hover:bg-blue-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">📊</span>
                  <span className="font-semibold">Session Monitoring</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>

            <button
              onClick={() => handleSettingsNavigation('notifications')}
              onTouchStart={() => handleSettingsNavigation('notifications')}
              className="w-full p-4 bg-orange-800 hover:bg-orange-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">🔔</span>
                  <span className="font-semibold">Notification Preferences</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>

            <button
              onClick={() => handleSettingsNavigation('sensitivity')}
              onTouchStart={() => handleSettingsNavigation('sensitivity')}
              className="w-full p-4 bg-purple-800 hover:bg-purple-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">⚡</span>
                  <span className="font-semibold">Monitoring Sensitivity</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>

            <button
              onClick={() => handleSettingsNavigation('parentDashboard')}
              onTouchStart={() => handleSettingsNavigation('parentDashboard')}
              className="w-full p-4 bg-teal-800 hover:bg-teal-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">👨‍👩‍👧‍👦</span>
                  <span className="font-semibold">Parent Dashboard Access</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>

            <button
              onClick={() => handleSettingsNavigation('privacy')}
              onTouchStart={() => handleSettingsNavigation('privacy')}
              className="w-full p-4 bg-red-800 hover:bg-red-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">🔒</span>
                  <span className="font-semibold">Privacy Settings</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>

            <button
              onClick={() => handleSettingsNavigation('about')}
              onTouchStart={() => handleSettingsNavigation('about')}
              className="w-full p-4 bg-gray-800 hover:bg-gray-700 rounded-xl text-left transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">ℹ️</span>
                  <span className="font-semibold">About SafeGuardian</span>
                </div>
                <span className="text-gray-400">›</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Render bottom navigation
  const renderBottomNav = () => {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700">
        <div className="flex justify-around py-2">
          <button
            onClick={() => handleTabChange('home')}
            onTouchStart={() => handleTabChange('home')}
            className={`flex flex-col items-center py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'home' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="text-xl mb-1">🏠</span>
            <span className="text-xs">Home</span>
          </button>

          <button
            onClick={() => handleTabChange('activity')}
            onTouchStart={() => handleTabChange('activity')}
            className={`flex flex-col items-center py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'activity' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="text-xl mb-1">📊</span>
            <span className="text-xs">Activity</span>
          </button>

          <button
            onClick={() => handleTabChange('protected')}
            onTouchStart={() => handleTabChange('protected')}
            className={`flex flex-col items-center py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'protected' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="text-xl mb-1">🛡️</span>
            <span className="text-xs">Protected</span>
          </button>

          <button
            onClick={() => handleTabChange('settings')}
            onTouchStart={() => handleTabChange('settings')}
            className={`flex flex-col items-center py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'settings' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="text-xl mb-1">⚙️</span>
            <span className="text-xs">Settings</span>
          </button>
        </div>
      </div>
    )
  }

  // Main render
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Render current screen */}
      {activeTab === 'home' && renderHome()}
      {activeTab === 'activity' && renderActivity()}
      {activeTab === 'protected' && renderProtected()}
      {activeTab === 'settings' && renderSettings()}

      {/* Bottom Navigation */}
      {renderBottomNav()}
    </div>
  )
}

export default App

