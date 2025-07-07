import { useState } from 'react'
import { 
  Shield, 
  Bell, 
  Menu, 
  Wifi, 
  Battery, 
  Signal,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

const TopBar = ({ user, currentPlatform, monitoringActive, alertCount = 0 }) => {
  const [showNotifications, setShowNotifications] = useState(false)

  const getCurrentTime = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getPlatformName = () => {
    if (!currentPlatform) return null
    return currentPlatform.charAt(0).toUpperCase() + currentPlatform.slice(1)
  }

  return (
    <div className="bg-black text-white">
      {/* Status Bar */}
      <div className="flex items-center justify-between px-4 py-1 text-xs">
        <div className="flex items-center gap-1">
          <span className="font-medium">{getCurrentTime()}</span>
        </div>
        <div className="flex items-center gap-1">
          <Signal className="w-3 h-3" />
          <Wifi className="w-3 h-3" />
          <Battery className="w-4 h-3" />
          <span className="text-xs">100%</span>
        </div>
      </div>

      {/* Main Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
            <Shield className="w-5 h-5 text-black" />
          </div>
          <div>
            <h1 className="font-bold text-lg">SafeGuardian</h1>
            {currentPlatform && (
              <p className="text-xs text-gray-400">
                Protecting {getPlatformName()}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Monitoring Status */}
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
            monitoringActive 
              ? 'bg-green-500/20 text-green-400' 
              : 'bg-gray-600/20 text-gray-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              monitoringActive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
            }`}></div>
            <span>{monitoringActive ? 'LIVE' : 'OFF'}</span>
          </div>

          {/* Notifications */}
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 hover:bg-gray-800 rounded-full transition-colors"
          >
            <Bell className="w-5 h-5" />
            {alertCount > 0 && (
              <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                {alertCount > 9 ? '9+' : alertCount}
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Protection Banner */}
      {monitoringActive && (
        <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 border-b border-green-500/30 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-300">
                You are protected by SafeGuardian AI
              </span>
            </div>
            <div className="text-xs text-green-400">
              Real-time monitoring
            </div>
          </div>
        </div>
      )}

      {/* Alert Banner */}
      {alertCount > 0 && (
        <div className="bg-gradient-to-r from-red-500/20 to-orange-500/20 border-b border-red-500/30 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-sm text-red-300">
                {alertCount} security alert{alertCount !== 1 ? 's' : ''} need attention
              </span>
            </div>
            <button className="text-xs text-red-400 underline">
              View All
            </button>
          </div>
        </div>
      )}

      {/* Notifications Dropdown */}
      {showNotifications && (
        <div className="absolute top-full left-0 right-0 bg-gray-900 border-b border-gray-700 z-50">
          <div className="p-4">
            <h3 className="font-semibold mb-3">Recent Notifications</h3>
            {alertCount === 0 ? (
              <div className="text-center py-4 text-gray-400">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No new notifications</p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                    <span className="text-sm font-medium text-red-300">Security Alert</span>
                  </div>
                  <p className="text-xs text-red-200">Suspicious activity detected</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TopBar

