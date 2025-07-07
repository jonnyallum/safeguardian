import { useNavigate, useLocation } from 'react-router-dom'
import { 
  Shield, 
  Home, 
  Users, 
  AlertTriangle, 
  BarChart3, 
  Settings,
  Activity,
  Eye,
  FileText,
  HelpCircle
} from 'lucide-react'

const Sidebar = ({ isOpen, currentPage, onPageChange, alertCount = 0 }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Home,
      path: '/',
      description: 'Overview and real-time monitoring'
    },
    {
      id: 'children',
      label: 'Children',
      icon: Users,
      path: '/children',
      description: 'Manage protected children'
    },
    {
      id: 'alerts',
      label: 'Alerts',
      icon: AlertTriangle,
      path: '/alerts',
      description: 'Security alerts and notifications',
      badge: alertCount > 0 ? alertCount : null,
      badgeColor: 'bg-red-500'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      path: '/analytics',
      description: 'Reports and insights'
    },
    {
      id: 'monitoring',
      label: 'Live Monitor',
      icon: Activity,
      path: '/monitoring',
      description: 'Real-time activity monitoring'
    },
    {
      id: 'evidence',
      label: 'Evidence',
      icon: FileText,
      path: '/evidence',
      description: 'Forensic evidence management'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      path: '/settings',
      description: 'System configuration'
    }
  ]

  const handleNavigation = (item) => {
    onPageChange(item.id)
    navigate(item.path)
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <div className={`fixed left-0 top-0 h-full bg-gradient-to-b from-gray-900 to-black border-r border-yellow-500/20 transition-all duration-300 z-40 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      {/* Logo Section */}
      <div className="p-4 border-b border-yellow-500/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-black" />
          </div>
          {isOpen && (
            <div>
              <h1 className="text-lg font-bold text-yellow-400">SafeGuardian</h1>
              <p className="text-xs text-yellow-300">Guardian Dashboard</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {menuItems.map((item) => {
            const IconComponent = item.icon
            const active = isActive(item.path)
            
            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 group relative ${
                  active 
                    ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' 
                    : 'text-gray-400 hover:text-yellow-300 hover:bg-yellow-500/10'
                }`}
                title={!isOpen ? item.label : ''}
              >
                <div className="relative">
                  <IconComponent className={`w-5 h-5 ${active ? 'text-yellow-400' : ''}`} />
                  {item.badge && (
                    <div className={`absolute -top-2 -right-2 ${item.badgeColor} text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium`}>
                      {item.badge > 9 ? '9+' : item.badge}
                    </div>
                  )}
                </div>
                
                {isOpen && (
                  <div className="flex-1 text-left">
                    <div className={`font-medium ${active ? 'text-yellow-400' : ''}`}>
                      {item.label}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                )}

                {/* Active indicator */}
                {active && (
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-yellow-400 rounded-r"></div>
                )}

                {/* Tooltip for collapsed sidebar */}
                {!isOpen && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-gray-800 text-yellow-300 text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-800 rotate-45"></div>
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Status Section */}
      {isOpen && (
        <div className="p-4 border-t border-yellow-500/20">
          <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-300">System Status</span>
            </div>
            <div className="text-xs text-green-200">
              All systems operational
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      {isOpen && (
        <div className="p-4">
          <button className="w-full flex items-center gap-3 px-3 py-2 text-gray-400 hover:text-yellow-300 hover:bg-yellow-500/10 rounded-lg transition-all duration-200">
            <HelpCircle className="w-5 h-5" />
            <span className="text-sm">Help & Support</span>
          </button>
        </div>
      )}
    </div>
  )
}

export default Sidebar

