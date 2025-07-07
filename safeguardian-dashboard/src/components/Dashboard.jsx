import { useState, useEffect } from 'react'
import { 
  Shield, 
  Users, 
  AlertTriangle, 
  Activity, 
  Eye, 
  Clock,
  TrendingUp,
  TrendingDown,
  MapPin,
  Smartphone,
  Monitor,
  Wifi,
  WifiOff,
  CheckCircle,
  XCircle,
  BarChart3,
  PieChart,
  Calendar,
  Filter
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const Dashboard = ({ realTimeData, children, alerts, onPageChange }) => {
  const [timeRange, setTimeRange] = useState('24h')
  const [selectedMetric, setSelectedMetric] = useState('all')

  // Calculate dashboard metrics
  const metrics = {
    totalChildren: children.length,
    activeMonitoring: children.filter(child => child.status === 'online').length,
    totalAlerts: realTimeData.totalAlerts,
    highRiskAlerts: realTimeData.highRiskAlerts,
    platformsConnected: realTimeData.platformsConnected,
    protectionRate: Math.round((realTimeData.platformsConnected / 10) * 100)
  }

  // Sample chart data
  const alertTrends = [
    { time: '00:00', alerts: 2 },
    { time: '04:00', alerts: 1 },
    { time: '08:00', alerts: 5 },
    { time: '12:00', alerts: 8 },
    { time: '16:00', alerts: 12 },
    { time: '20:00', alerts: 6 },
    { time: '24:00', alerts: 3 }
  ]

  const platformDistribution = [
    { platform: 'Instagram', count: 15, color: 'bg-purple-500' },
    { platform: 'Facebook', count: 12, color: 'bg-blue-500' },
    { platform: 'Snapchat', count: 8, color: 'bg-yellow-500' },
    { platform: 'TikTok', count: 6, color: 'bg-pink-500' },
    { platform: 'Discord', count: 4, color: 'bg-indigo-500' }
  ]

  const StatCard = ({ title, value, change, icon: Icon, color, trend }) => (
    <div className="bg-gray-800/50 border border-yellow-500/20 rounded-xl p-6 hover:border-yellow-500/40 transition-all duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 ${color} rounded-lg flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-yellow-400 mb-1">{value}</div>
      <div className="text-sm text-gray-400">{title}</div>
      {change && (
        <div className="text-xs text-gray-500 mt-2">{change}</div>
      )}
    </div>
  )

  const AlertItem = ({ alert }) => (
    <div className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg border border-gray-600">
      <div className={`w-3 h-3 rounded-full ${
        alert.severity === 'high' ? 'bg-red-500' : 
        alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
      }`}></div>
      <div className="flex-1">
        <div className="text-sm font-medium text-yellow-300">{alert.childName}</div>
        <div className="text-xs text-gray-400 capitalize">{alert.platform} • {alert.type.replace('_', ' ')}</div>
      </div>
      <div className="text-xs text-gray-500">
        {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  )

  const ChildStatusCard = ({ child }) => (
    <div className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg border border-gray-600">
      <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
        <span className="text-black font-semibold text-sm">{child.name.charAt(0)}</span>
      </div>
      <div className="flex-1">
        <div className="text-sm font-medium text-yellow-300">{child.name}</div>
        <div className="text-xs text-gray-400">Age {child.age} • {child.platforms.length} platforms</div>
      </div>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${child.status === 'online' ? 'bg-green-500' : 'bg-gray-500'}`}></div>
        <span className={`text-xs ${child.status === 'online' ? 'text-green-400' : 'text-gray-400'}`}>
          {child.status}
        </span>
      </div>
    </div>
  )

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-yellow-400">Dashboard Overview</h1>
          <p className="text-gray-400 mt-1">Real-time monitoring and protection status</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-gray-800 border border-yellow-500/30 rounded-lg px-3 py-2 text-yellow-100 text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <Button className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 border border-yellow-500/30">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Protected Children"
          value={metrics.totalChildren}
          icon={Users}
          color="bg-blue-500"
          trend={5}
          change="2 new this week"
        />
        <StatCard
          title="Active Monitoring"
          value={metrics.activeMonitoring}
          icon={Activity}
          color="bg-green-500"
          trend={12}
          change="Real-time protection"
        />
        <StatCard
          title="Total Alerts"
          value={metrics.totalAlerts}
          icon={AlertTriangle}
          color="bg-yellow-500"
          trend={-8}
          change="15% decrease from yesterday"
        />
        <StatCard
          title="High Risk Alerts"
          value={metrics.highRiskAlerts}
          icon={Shield}
          color="bg-red-500"
          trend={-25}
          change="Immediate attention required"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alert Trends Chart */}
        <div className="lg:col-span-2 bg-gray-800/50 border border-yellow-500/20 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-yellow-400">Alert Trends</h2>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              Alerts over time
            </div>
          </div>
          <div className="h-64 flex items-end justify-between gap-2">
            {alertTrends.map((point, index) => (
              <div key={index} className="flex flex-col items-center gap-2 flex-1">
                <div
                  className="bg-gradient-to-t from-yellow-500 to-yellow-400 rounded-t w-full transition-all duration-300 hover:from-yellow-400 hover:to-yellow-300"
                  style={{ height: `${(point.alerts / 12) * 100}%`, minHeight: '4px' }}
                ></div>
                <div className="text-xs text-gray-400">{point.time}</div>
              </div>
            ))}
          </div>
        </div>

        {/* System Status */}
        <div className="bg-gray-800/50 border border-yellow-500/20 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-yellow-400 mb-6">System Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">AI Detection</span>
              </div>
              <span className="text-xs text-green-400">Operational</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Real-time Monitoring</span>
              </div>
              <span className="text-xs text-green-400">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Platform Connections</span>
              </div>
              <span className="text-xs text-green-400">{metrics.platformsConnected}/10</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Evidence Storage</span>
              </div>
              <span className="text-xs text-green-400">Secure</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-yellow-400" />
                <span className="text-sm text-gray-300">Last Backup</span>
              </div>
              <span className="text-xs text-gray-400">2 hours ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <div className="bg-gray-800/50 border border-yellow-500/20 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-yellow-400">Recent Alerts</h2>
            <Button
              onClick={() => onPageChange('alerts')}
              className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 text-sm"
            >
              View All
            </Button>
          </div>
          <div className="space-y-3">
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <AlertItem key={alert.id} alert={alert} />
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No recent alerts</p>
                <p className="text-sm">All children are safe</p>
              </div>
            )}
          </div>
        </div>

        {/* Children Status */}
        <div className="bg-gray-800/50 border border-yellow-500/20 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-yellow-400">Children Status</h2>
            <Button
              onClick={() => onPageChange('children')}
              className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 text-sm"
            >
              Manage
            </Button>
          </div>
          <div className="space-y-3">
            {children.map((child) => (
              <ChildStatusCard key={child.id} child={child} />
            ))}
          </div>
        </div>
      </div>

      {/* Platform Distribution */}
      <div className="bg-gray-800/50 border border-yellow-500/20 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-yellow-400 mb-6">Platform Activity Distribution</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {platformDistribution.map((platform, index) => (
            <div key={index} className="text-center">
              <div className={`w-16 h-16 ${platform.color} rounded-full mx-auto mb-3 flex items-center justify-center`}>
                <span className="text-white font-bold">{platform.count}</span>
              </div>
              <div className="text-sm font-medium text-yellow-300">{platform.platform}</div>
              <div className="text-xs text-gray-400">Active sessions</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

