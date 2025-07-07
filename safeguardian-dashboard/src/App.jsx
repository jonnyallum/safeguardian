import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { 
  Shield, 
  Home, 
  Users, 
  AlertTriangle, 
  BarChart3, 
  Settings, 
  Bell,
  Search,
  Menu,
  X,
  Eye,
  Download,
  Filter,
  Calendar,
  Clock,
  MapPin,
  Smartphone,
  Monitor,
  Activity
} from 'lucide-react'
import './App.css'

// Import components
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import Dashboard from './components/Dashboard'
import ChildrenManagement from './components/ChildrenManagement'
import AlertsCenter from './components/AlertsCenter'
import Analytics from './components/Analytics'
import SettingsPanel from './components/SettingsPanel'
import LoginPage from './components/LoginPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [alerts, setAlerts] = useState([])
  const [children, setChildren] = useState([])
  const [realTimeData, setRealTimeData] = useState({
    activeMonitoring: 0,
    totalAlerts: 0,
    highRiskAlerts: 0,
    platformsConnected: 0
  })

  // Check authentication on app load
  useEffect(() => {
    const token = localStorage.getItem('safeguardian_admin_token')
    const userData = localStorage.getItem('safeguardian_admin_user')
    
    if (token && userData) {
      setIsAuthenticated(true)
      setUser(JSON.parse(userData))
      loadDashboardData()
    }
  }, [])

  // Simulate real-time data updates
  useEffect(() => {
    if (isAuthenticated) {
      const interval = setInterval(() => {
        // Simulate real-time updates
        setRealTimeData(prev => ({
          ...prev,
          activeMonitoring: Math.floor(Math.random() * 10) + 5,
          totalAlerts: prev.totalAlerts + (Math.random() > 0.8 ? 1 : 0),
          highRiskAlerts: prev.highRiskAlerts + (Math.random() > 0.95 ? 1 : 0),
          platformsConnected: 8
        }))

        // Simulate new alerts
        if (Math.random() > 0.9) {
          const newAlert = {
            id: Date.now(),
            childName: ['Emma', 'Liam', 'Sophia', 'Noah'][Math.floor(Math.random() * 4)],
            type: ['suspicious_message', 'stranger_contact', 'inappropriate_content'][Math.floor(Math.random() * 3)],
            platform: ['instagram', 'facebook', 'snapchat', 'tiktok'][Math.floor(Math.random() * 4)],
            severity: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
            timestamp: new Date().toISOString(),
            description: 'AI detected potentially risky interaction'
          }
          setAlerts(prev => [newAlert, ...prev.slice(0, 19)]) // Keep last 20 alerts
        }
      }, 3000)

      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  const loadDashboardData = () => {
    // Simulate loading children data
    setChildren([
      {
        id: 1,
        name: 'Emma Johnson',
        age: 13,
        avatar: null,
        status: 'online',
        platforms: ['instagram', 'snapchat'],
        lastActivity: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        riskLevel: 'low'
      },
      {
        id: 2,
        name: 'Liam Smith',
        age: 15,
        avatar: null,
        status: 'offline',
        platforms: ['facebook', 'tiktok', 'discord'],
        lastActivity: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        riskLevel: 'medium'
      },
      {
        id: 3,
        name: 'Sophia Davis',
        age: 12,
        avatar: null,
        status: 'online',
        platforms: ['instagram', 'facebook'],
        lastActivity: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        riskLevel: 'high'
      }
    ])

    // Initialize real-time data
    setRealTimeData({
      activeMonitoring: 7,
      totalAlerts: 23,
      highRiskAlerts: 3,
      platformsConnected: 8
    })
  }

  const handleLogin = (userData, token) => {
    setIsAuthenticated(true)
    setUser(userData)
    localStorage.setItem('safeguardian_admin_token', token)
    localStorage.setItem('safeguardian_admin_user', JSON.stringify(userData))
    loadDashboardData()
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUser(null)
    localStorage.removeItem('safeguardian_admin_token')
    localStorage.removeItem('safeguardian_admin_user')
    setCurrentPage('dashboard')
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <Router>
      <div className="min-h-screen bg-black text-yellow-100 flex">
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          alertCount={alerts.filter(a => a.severity === 'high').length}
        />

        {/* Main Content */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
          {/* Top Bar */}
          <TopBar 
            user={user}
            onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
            onLogout={handleLogout}
            alertCount={alerts.filter(a => a.severity === 'high').length}
          />

          {/* Page Content */}
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route 
                path="/" 
                element={
                  <Dashboard 
                    realTimeData={realTimeData}
                    children={children}
                    alerts={alerts.slice(0, 5)}
                    onPageChange={setCurrentPage}
                  />
                } 
              />
              <Route 
                path="/children" 
                element={
                  <ChildrenManagement 
                    children={children}
                    onChildUpdate={(id, updates) => {
                      setChildren(prev => prev.map(child => 
                        child.id === id ? { ...child, ...updates } : child
                      ))
                    }}
                  />
                } 
              />
              <Route 
                path="/alerts" 
                element={
                  <AlertsCenter 
                    alerts={alerts}
                    onAlertDismiss={(id) => {
                      setAlerts(prev => prev.filter(alert => alert.id !== id))
                    }}
                  />
                } 
              />
              <Route 
                path="/analytics" 
                element={
                  <Analytics 
                    children={children}
                    alerts={alerts}
                    realTimeData={realTimeData}
                  />
                } 
              />
              <Route 
                path="/settings" 
                element={
                  <SettingsPanel 
                    user={user}
                    onUserUpdate={setUser}
                  />
                } 
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>

        {/* Emergency Alert Overlay */}
        {alerts.some(a => a.severity === 'high') && (
          <div className="fixed top-4 right-4 z-50">
            <div className="bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg animate-pulse">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-semibold">High Risk Alert!</span>
              </div>
              <div className="text-sm mt-1">
                {alerts.filter(a => a.severity === 'high').length} critical alert(s) require attention
              </div>
            </div>
          </div>
        )}
      </div>
    </Router>
  )
}

export default App

