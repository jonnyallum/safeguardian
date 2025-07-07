import { useState } from 'react'
import { 
  Menu, 
  Bell, 
  Search, 
  User, 
  LogOut, 
  Settings, 
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  ChevronDown
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const TopBar = ({ user, onMenuToggle, onLogout, alertCount = 0 }) => {
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const getCurrentTime = () => {
    return new Date().toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const recentNotifications = [
    {
      id: 1,
      type: 'alert',
      title: 'High Risk Alert',
      message: 'Suspicious activity detected for Emma Johnson',
      time: '2 minutes ago',
      severity: 'high'
    },
    {
      id: 2,
      type: 'info',
      title: 'System Update',
      message: 'AI detection models updated successfully',
      time: '1 hour ago',
      severity: 'low'
    },
    {
      id: 3,
      type: 'warning',
      title: 'Platform Connection',
      message: 'Instagram connection requires re-authentication',
      time: '3 hours ago',
      severity: 'medium'
    }
  ]

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-400" />
      case 'medium':
        return <Clock className="w-4 h-4 text-yellow-400" />
      default:
        return <CheckCircle className="w-4 h-4 text-blue-400" />
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'border-red-500/50 bg-red-500/20'
      case 'medium':
        return 'border-yellow-500/50 bg-yellow-500/20'
      default:
        return 'border-blue-500/50 bg-blue-500/20'
    }
  }

  return (
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-yellow-500/20 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <Button
            onClick={onMenuToggle}
            className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 p-2 rounded-lg"
          >
            <Menu className="w-5 h-5" />
          </Button>

          <div className="hidden md:block">
            <h2 className="text-xl font-semibold text-yellow-400">Guardian Control Center</h2>
            <p className="text-sm text-gray-400">{getCurrentTime()}</p>
          </div>
        </div>

        {/* Center Section - Search */}
        <div className="hidden lg:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search children, alerts, or activities..."
              className="w-full bg-black/50 border border-yellow-500/30 rounded-lg pl-10 pr-4 py-2 text-yellow-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* System Status */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-300">All Systems Operational</span>
          </div>

          {/* Notifications */}
          <div className="relative">
            <Button
              onClick={() => setShowNotifications(!showNotifications)}
              className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 p-2 rounded-lg relative"
            >
              <Bell className="w-5 h-5" />
              {alertCount > 0 && (
                <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                  {alertCount > 9 ? '9+' : alertCount}
                </div>
              )}
            </Button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 top-full mt-2 w-80 bg-gray-800 border border-yellow-500/30 rounded-lg shadow-xl z-50">
                <div className="p-4 border-b border-gray-700">
                  <h3 className="font-semibold text-yellow-400">Notifications</h3>
                  <p className="text-sm text-gray-400">{recentNotifications.length} new notifications</p>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {recentNotifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 border-b border-gray-700 hover:bg-gray-700/50 transition-colors ${getSeverityColor(notification.severity)}`}
                    >
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(notification.severity)}
                        <div className="flex-1">
                          <h4 className="font-medium text-yellow-300">{notification.title}</h4>
                          <p className="text-sm text-gray-300 mt-1">{notification.message}</p>
                          <p className="text-xs text-gray-500 mt-2">{notification.time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-3 border-t border-gray-700">
                  <Button className="w-full bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 text-sm">
                    View All Notifications
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* User Menu */}
          <div className="relative">
            <Button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 px-3 py-2 rounded-lg flex items-center gap-2"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-black" />
              </div>
              <div className="hidden md:block text-left">
                <div className="text-sm font-medium">{user?.name || 'User'}</div>
                <div className="text-xs text-gray-400 capitalize">{user?.role || 'Guardian'}</div>
              </div>
              <ChevronDown className="w-4 h-4" />
            </Button>

            {/* User Dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-gray-800 border border-yellow-500/30 rounded-lg shadow-xl z-50">
                <div className="p-3 border-b border-gray-700">
                  <div className="font-medium text-yellow-400">{user?.name}</div>
                  <div className="text-sm text-gray-400">{user?.email}</div>
                </div>
                <div className="p-2">
                  <button className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:text-yellow-300 hover:bg-yellow-500/10 rounded-lg transition-colors">
                    <User className="w-4 h-4" />
                    <span className="text-sm">Profile</span>
                  </button>
                  <button className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:text-yellow-300 hover:bg-yellow-500/10 rounded-lg transition-colors">
                    <Settings className="w-4 h-4" />
                    <span className="text-sm">Settings</span>
                  </button>
                  <button className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:text-yellow-300 hover:bg-yellow-500/10 rounded-lg transition-colors">
                    <Shield className="w-4 h-4" />
                    <span className="text-sm">Security</span>
                  </button>
                </div>
                <div className="p-2 border-t border-gray-700">
                  <button
                    onClick={onLogout}
                    className="w-full flex items-center gap-3 px-3 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm">Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Search */}
      <div className="lg:hidden mt-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search..."
            className="w-full bg-black/50 border border-yellow-500/30 rounded-lg pl-10 pr-4 py-2 text-yellow-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          />
        </div>
      </div>
    </header>
  )
}

export default TopBar

