import { useLocation, useNavigate } from 'react-router-dom'
import { Home, Shield, Bell, Settings } from 'lucide-react'

const BottomNavigation = ({ alertCount = 0 }) => {
  const location = useLocation()
  const navigate = useNavigate()

  const navItems = [
    {
      id: 'home',
      label: 'Home',
      icon: Home,
      path: '/',
      active: location.pathname === '/'
    },
    {
      id: 'protection',
      label: 'Protection',
      icon: Shield,
      path: '/',
      active: false
    },
    {
      id: 'alerts',
      label: 'Alerts',
      icon: Bell,
      path: '/alerts',
      active: location.pathname === '/alerts',
      badge: alertCount > 0 ? alertCount : null
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      path: '/settings',
      active: location.pathname === '/settings'
    }
  ]

  const handleNavClick = (item) => {
    if (item.id === 'protection') {
      // Special handling for protection - could open a quick menu
      return
    }
    navigate(item.path)
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-700 z-40">
      <div className="flex items-center justify-around py-2">
        {navItems.map((item) => {
          const IconComponent = item.icon
          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item)}
              className={`flex flex-col items-center justify-center p-2 min-w-0 flex-1 relative transition-colors ${
                item.active 
                  ? 'text-yellow-400' 
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <div className="relative">
                <IconComponent className={`w-6 h-6 ${item.active ? 'text-yellow-400' : ''}`} />
                {item.badge && (
                  <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                    {item.badge > 9 ? '9+' : item.badge}
                  </div>
                )}
              </div>
              <span className={`text-xs mt-1 ${item.active ? 'text-yellow-400' : 'text-gray-400'}`}>
                {item.label}
              </span>
              {item.active && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-yellow-400 rounded-full"></div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default BottomNavigation

