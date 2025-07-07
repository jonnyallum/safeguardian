import { useState } from 'react'
import { 
  User, 
  Shield, 
  Bell, 
  Lock, 
  HelpCircle, 
  LogOut,
  ChevronRight,
  Toggle,
  Moon,
  Sun,
  Volume2,
  VolumeX,
  Smartphone,
  Mail,
  Phone
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const SettingsScreen = ({ user, onLogout }) => {
  const [notifications, setNotifications] = useState(true)
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [darkMode, setDarkMode] = useState(true)
  const [autoProtection, setAutoProtection] = useState(true)

  const settingsSections = [
    {
      title: 'Account',
      items: [
        {
          icon: User,
          label: 'Profile',
          value: user?.name || 'Demo User',
          action: () => console.log('Profile settings')
        },
        {
          icon: Mail,
          label: 'Email',
          value: user?.email || 'demo@safeguardian.com',
          action: () => console.log('Email settings')
        }
      ]
    },
    {
      title: 'Protection',
      items: [
        {
          icon: Shield,
          label: 'Auto Protection',
          value: autoProtection,
          type: 'toggle',
          action: () => setAutoProtection(!autoProtection)
        },
        {
          icon: Bell,
          label: 'Alert Notifications',
          value: notifications,
          type: 'toggle',
          action: () => setNotifications(!notifications)
        },
        {
          icon: Volume2,
          label: 'Sound Alerts',
          value: soundEnabled,
          type: 'toggle',
          action: () => setSoundEnabled(!soundEnabled)
        }
      ]
    },
    {
      title: 'Appearance',
      items: [
        {
          icon: Moon,
          label: 'Dark Mode',
          value: darkMode,
          type: 'toggle',
          action: () => setDarkMode(!darkMode)
        }
      ]
    },
    {
      title: 'Support',
      items: [
        {
          icon: HelpCircle,
          label: 'Help & Support',
          action: () => console.log('Help')
        },
        {
          icon: Lock,
          label: 'Privacy Policy',
          action: () => console.log('Privacy')
        }
      ]
    }
  ]

  const ToggleSwitch = ({ enabled, onChange }) => (
    <button
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-yellow-500' : 'bg-gray-600'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  )

  return (
    <div className="min-h-screen bg-black text-white p-4 pb-20">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400">Manage your SafeGuardian preferences</p>
      </div>

      {/* User Profile Card */}
      <div className="bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 rounded-2xl p-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-black" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">{user?.name || 'Demo User'}</h3>
            <p className="text-yellow-300 text-sm">{user?.email || 'demo@safeguardian.com'}</p>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-green-300">Protected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {settingsSections.map((section, sectionIndex) => (
          <div key={sectionIndex}>
            <h2 className="text-lg font-semibold mb-3 text-gray-300">{section.title}</h2>
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden">
              {section.items.map((item, itemIndex) => {
                const IconComponent = item.icon
                return (
                  <div
                    key={itemIndex}
                    onClick={item.action}
                    className={`flex items-center justify-between p-4 cursor-pointer hover:bg-gray-700/50 transition-colors ${
                      itemIndex !== section.items.length - 1 ? 'border-b border-gray-700' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-700 rounded-lg flex items-center justify-center">
                        <IconComponent className="w-5 h-5 text-gray-300" />
                      </div>
                      <div>
                        <h3 className="font-medium">{item.label}</h3>
                        {item.type !== 'toggle' && item.value && (
                          <p className="text-sm text-gray-400">{item.value}</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      {item.type === 'toggle' ? (
                        <ToggleSwitch enabled={item.value} onChange={item.action} />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Protection Status */}
      <div className="mt-6 bg-green-500/20 border border-green-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-5 h-5 text-green-400" />
          <h3 className="font-semibold text-green-300">Protection Status</h3>
        </div>
        <p className="text-sm text-green-200 mb-3">
          SafeGuardian is actively monitoring your digital activities and keeping you safe online.
        </p>
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-green-500/20 rounded-lg p-2 text-center">
            <div className="font-semibold text-green-300">3</div>
            <div className="text-green-200">Platforms Protected</div>
          </div>
          <div className="bg-green-500/20 rounded-lg p-2 text-center">
            <div className="font-semibold text-green-300">24/7</div>
            <div className="text-green-200">Monitoring Active</div>
          </div>
        </div>
      </div>

      {/* Emergency Contact */}
      <div className="mt-6 bg-red-500/20 border border-red-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-2">
          <Phone className="w-5 h-5 text-red-400" />
          <h3 className="font-semibold text-red-300">Emergency Contact</h3>
        </div>
        <p className="text-sm text-red-200 mb-3">
          In case of emergency, your guardian will be notified immediately.
        </p>
        <Button className="w-full bg-red-500 hover:bg-red-600 text-white">
          Contact Guardian Now
        </Button>
      </div>

      {/* Logout Button */}
      <div className="mt-6">
        <Button
          onClick={onLogout}
          className="w-full bg-gray-700 hover:bg-gray-600 text-white flex items-center justify-center gap-2 py-3"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </Button>
      </div>

      {/* App Version */}
      <div className="mt-6 text-center text-xs text-gray-500">
        SafeGuardian v1.0.0
        <br />
        Protecting children online since 2024
      </div>
    </div>
  )
}

export default SettingsScreen

