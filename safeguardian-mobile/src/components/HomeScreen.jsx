import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Shield, 
  Instagram, 
  Facebook, 
  MessageCircle, 
  Video, 
  Music,
  Play,
  Pause,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const HomeScreen = ({ user, onPlatformSelect, monitoringActive, currentPlatform }) => {
  const navigate = useNavigate()
  const [selectedPlatform, setSelectedPlatform] = useState(currentPlatform)

  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: 'from-purple-500 to-pink-500',
      description: 'Photo & video sharing',
      status: 'connected'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'from-blue-600 to-blue-700',
      description: 'Social networking',
      status: 'connected'
    },
    {
      id: 'snapchat',
      name: 'Snapchat',
      icon: MessageCircle,
      color: 'from-yellow-400 to-yellow-500',
      description: 'Disappearing messages',
      status: 'connected'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: Music,
      color: 'from-black to-gray-800',
      description: 'Short video content',
      status: 'pending'
    },
    {
      id: 'discord',
      name: 'Discord',
      icon: Users,
      color: 'from-indigo-500 to-purple-600',
      description: 'Gaming & communities',
      status: 'disconnected'
    }
  ]

  const handlePlatformClick = (platform) => {
    if (platform.status === 'connected') {
      setSelectedPlatform(platform.id)
      onPlatformSelect(platform.id)
      navigate(`/platform/${platform.id}`)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      default:
        return <AlertTriangle className="w-4 h-4 text-red-500" />
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Protected'
      case 'pending':
        return 'Connecting...'
      default:
        return 'Not Connected'
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-4 pb-20">
      {/* Welcome Section */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Welcome back, {user?.name?.split(' ')[0] || 'User'}!</h1>
        <p className="text-gray-400">Your digital safety is our priority</p>
      </div>

      {/* Protection Status */}
      <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 border border-green-500/30 rounded-2xl p-4 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <Shield className="w-6 h-6 text-black" />
            </div>
            <div>
              <h3 className="font-semibold">Protection Status</h3>
              <p className="text-sm text-gray-300">
                {monitoringActive ? 'Actively monitoring' : 'Ready to protect'}
              </p>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            monitoringActive 
              ? 'bg-green-500 text-black' 
              : 'bg-gray-600 text-white'
          }`}>
            {monitoringActive ? 'ACTIVE' : 'STANDBY'}
          </div>
        </div>
        
        {monitoringActive && currentPlatform && (
          <div className="flex items-center gap-2 text-sm text-green-300">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            Currently protecting {platforms.find(p => p.id === currentPlatform)?.name}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-3">
          <Button
            onClick={() => navigate('/alerts')}
            className="bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 text-red-300 h-16 flex-col gap-1"
          >
            <AlertTriangle className="w-5 h-5" />
            <span className="text-xs">View Alerts</span>
          </Button>
          <Button
            onClick={() => navigate('/settings')}
            className="bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 text-blue-300 h-16 flex-col gap-1"
          >
            <Shield className="w-5 h-5" />
            <span className="text-xs">Settings</span>
          </Button>
        </div>
      </div>

      {/* Connected Platforms */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-3">Your Platforms</h2>
        <div className="space-y-3">
          {platforms.map((platform) => {
            const IconComponent = platform.icon
            return (
              <div
                key={platform.id}
                onClick={() => handlePlatformClick(platform)}
                className={`bg-gray-800/50 border border-gray-700 rounded-xl p-4 transition-all duration-200 ${
                  platform.status === 'connected' 
                    ? 'cursor-pointer hover:bg-gray-700/50 hover:border-gray-600' 
                    : 'opacity-60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 bg-gradient-to-br ${platform.color} rounded-xl flex items-center justify-center`}>
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{platform.name}</h3>
                      <p className="text-sm text-gray-400">{platform.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(platform.status)}
                    <span className="text-xs text-gray-400">{getStatusText(platform.status)}</span>
                  </div>
                </div>
                
                {platform.status === 'connected' && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <span>Tap to open with protection</span>
                      <Play className="w-4 h-4" />
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Safety Tips */}
      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
        <h3 className="font-semibold text-yellow-300 mb-2">💡 Safety Tip</h3>
        <p className="text-sm text-yellow-200">
          Never share personal information like your address, phone number, or school name with people you meet online.
        </p>
      </div>
    </div>
  )
}

export default HomeScreen

