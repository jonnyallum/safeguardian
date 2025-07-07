import { BarChart3 } from 'lucide-react'

const Analytics = ({ children, alerts, realTimeData }) => {
  return (
    <div className="p-6">
      <div className="text-center py-12">
        <BarChart3 className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-yellow-400 mb-2">Analytics & Reports</h2>
        <p className="text-gray-400">Comprehensive insights and reporting</p>
        <p className="text-sm text-gray-500 mt-4">Component under development</p>
      </div>
    </div>
  )
}

export default Analytics

