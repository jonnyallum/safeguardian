import { useState } from 'react'
import { 
  AlertTriangle, 
  Shield, 
  Clock, 
  CheckCircle, 
  X, 
  Eye,
  MessageCircle,
  User,
  Calendar
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const AlertsScreen = ({ alerts, onClearAlert }) => {
  const [selectedAlert, setSelectedAlert] = useState(null)

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'border-red-500 bg-red-500/20 text-red-300'
      case 'medium':
        return 'border-yellow-500 bg-yellow-500/20 text-yellow-300'
      default:
        return 'border-blue-500 bg-blue-500/20 text-blue-300'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-400" />
      case 'medium':
        return <Clock className="w-5 h-5 text-yellow-400" />
      default:
        return <Shield className="w-5 h-5 text-blue-400" />
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  const getAlertDetails = (alert) => {
    const details = {
      suspicious_message: {
        title: 'Suspicious Message Detected',
        description: 'AI detected potentially inappropriate content in a conversation',
        action: 'Review the flagged message and take appropriate action'
      },
      stranger_contact: {
        title: 'Unknown Contact',
        description: 'Someone not in your contacts is trying to message you',
        action: 'Verify the identity before responding'
      },
      inappropriate_content: {
        title: 'Inappropriate Content',
        description: 'Content that may not be suitable was detected',
        action: 'Content has been filtered and guardians notified'
      }
    }
    return details[alert.type] || {
      title: 'Security Alert',
      description: alert.message,
      action: 'Please review this alert'
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-4 pb-20">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Security Alerts</h1>
        <p className="text-gray-400">
          {alerts.length === 0 ? 'No alerts - you\'re all safe!' : `${alerts.length} alert${alerts.length !== 1 ? 's' : ''} need your attention`}
        </p>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-3 text-center">
          <div className="text-2xl font-bold text-red-400">
            {alerts.filter(a => a.severity === 'high').length}
          </div>
          <div className="text-xs text-red-300">High Risk</div>
        </div>
        <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-xl p-3 text-center">
          <div className="text-2xl font-bold text-yellow-400">
            {alerts.filter(a => a.severity === 'medium').length}
          </div>
          <div className="text-xs text-yellow-300">Medium Risk</div>
        </div>
        <div className="bg-blue-500/20 border border-blue-500/50 rounded-xl p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {alerts.filter(a => a.severity === 'low').length}
          </div>
          <div className="text-xs text-blue-300">Low Risk</div>
        </div>
      </div>

      {/* Alerts List */}
      {alerts.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          <h3 className="text-lg font-semibold mb-2">All Clear!</h3>
          <p className="text-gray-400">No security alerts at this time. SafeGuardian is keeping you protected.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const details = getAlertDetails(alert)
            return (
              <div
                key={alert.id}
                className={`border rounded-xl p-4 ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {getSeverityIcon(alert.severity)}
                    <div>
                      <h3 className="font-semibold">{details.title}</h3>
                      <p className="text-sm opacity-80 capitalize">{alert.platform}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs opacity-70">{formatTime(alert.timestamp)}</span>
                    <Button
                      onClick={() => onClearAlert(alert.id)}
                      className="bg-white/20 hover:bg-white/30 p-1 rounded-full"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                
                <p className="text-sm mb-3 opacity-90">{details.description}</p>
                
                <div className="flex items-center justify-between">
                  <Button
                    onClick={() => setSelectedAlert(alert)}
                    className="bg-white/20 hover:bg-white/30 text-white text-xs px-3 py-1 rounded-full flex items-center gap-1"
                  >
                    <Eye className="w-3 h-3" />
                    View Details
                  </Button>
                  
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    alert.severity === 'high' ? 'bg-red-500 text-white' :
                    alert.severity === 'medium' ? 'bg-yellow-500 text-black' :
                    'bg-blue-500 text-white'
                  }`}>
                    {alert.severity.toUpperCase()}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-2xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Alert Details</h2>
              <Button
                onClick={() => setSelectedAlert(null)}
                className="bg-gray-700 hover:bg-gray-600 p-2 rounded-full"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                {getSeverityIcon(selectedAlert.severity)}
                <div>
                  <h3 className="font-semibold">{getAlertDetails(selectedAlert).title}</h3>
                  <p className="text-sm text-gray-400 capitalize">{selectedAlert.platform}</p>
                </div>
              </div>
              
              <div className="bg-gray-700/50 rounded-lg p-3">
                <h4 className="font-medium mb-2">Description</h4>
                <p className="text-sm text-gray-300">{getAlertDetails(selectedAlert).description}</p>
              </div>
              
              <div className="bg-gray-700/50 rounded-lg p-3">
                <h4 className="font-medium mb-2">Recommended Action</h4>
                <p className="text-sm text-gray-300">{getAlertDetails(selectedAlert).action}</p>
              </div>
              
              <div className="flex items-center gap-4 text-xs text-gray-400">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(selectedAlert.timestamp).toLocaleString()}
                </div>
              </div>
              
              <div className="flex gap-3">
                <Button
                  onClick={() => onClearAlert(selectedAlert.id)}
                  className="flex-1 bg-red-500 hover:bg-red-600 text-white"
                >
                  Dismiss Alert
                </Button>
                <Button
                  onClick={() => setSelectedAlert(null)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white"
                >
                  Keep Alert
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AlertsScreen

