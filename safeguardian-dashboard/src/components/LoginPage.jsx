import { useState } from 'react'
import { Shield, Eye, EyeOff, Lock, User, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Demo credentials for different user types
      if (email === 'guardian@safeguardian.com' && password === 'guardian123') {
        const userData = {
          id: '1',
          email: 'guardian@safeguardian.com',
          name: 'Sarah Johnson',
          role: 'guardian',
          avatar: null,
          children: ['Emma Johnson']
        }
        const token = 'guardian_token_' + Date.now()
        onLogin(userData, token)
      } else if (email === 'admin@safeguardian.com' && password === 'admin123') {
        const userData = {
          id: '2',
          email: 'admin@safeguardian.com',
          name: 'Admin User',
          role: 'admin',
          avatar: null,
          permissions: ['all']
        }
        const token = 'admin_token_' + Date.now()
        onLogin(userData, token)
      } else {
        setError('Invalid credentials. Use guardian@safeguardian.com / guardian123 or admin@safeguardian.com / admin123')
      }
    } catch (err) {
      setError('Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full mb-6">
            <Shield className="w-12 h-12 text-black" />
          </div>
          <h1 className="text-4xl font-bold text-yellow-400 mb-2">SafeGuardian</h1>
          <h2 className="text-xl text-yellow-300 mb-2">Guardian Dashboard</h2>
          <p className="text-gray-400">Protecting children in the digital world</p>
        </div>

        {/* Login Form */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-yellow-500/20">
          <form onSubmit={handleLogin} className="space-y-6">
            {/* Email Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-yellow-300">Email Address</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-yellow-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-black/50 border border-yellow-500/30 rounded-lg pl-10 pr-4 py-3 text-yellow-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-yellow-300">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-yellow-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-black/50 border border-yellow-500/30 rounded-lg pl-10 pr-12 py-3 text-yellow-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-yellow-400 hover:text-yellow-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-300 text-sm flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                {error}
              </div>
            )}

            {/* Login Button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-yellow-400 to-yellow-600 hover:from-yellow-500 hover:to-yellow-700 text-black font-semibold py-3 rounded-lg transition-all duration-200 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin"></div>
                  Signing In...
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <Shield className="w-5 h-5" />
                  Access Dashboard
                </div>
              )}
            </Button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-8 space-y-4">
            <div className="p-4 bg-blue-500/20 border border-blue-500/50 rounded-lg">
              <h3 className="text-sm font-medium text-blue-300 mb-2">Guardian Access</h3>
              <div className="text-xs text-blue-200 space-y-1">
                <div>Email: guardian@safeguardian.com</div>
                <div>Password: guardian123</div>
              </div>
            </div>
            
            <div className="p-4 bg-purple-500/20 border border-purple-500/50 rounded-lg">
              <h3 className="text-sm font-medium text-purple-300 mb-2">Administrator Access</h3>
              <div className="text-xs text-purple-200 space-y-1">
                <div>Email: admin@safeguardian.com</div>
                <div>Password: admin123</div>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="mt-6 space-y-3">
            <div className="flex items-center gap-3 text-sm text-yellow-300">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              Real-time monitoring dashboard
            </div>
            <div className="flex items-center gap-3 text-sm text-yellow-300">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              Advanced threat analytics
            </div>
            <div className="flex items-center gap-3 text-sm text-yellow-300">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              Comprehensive reporting tools
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-xs text-gray-500">
          SafeGuardian Dashboard v1.0.0
          <br />
          Secure • Reliable • Professional
        </div>
      </div>
    </div>
  )
}

export default LoginPage

