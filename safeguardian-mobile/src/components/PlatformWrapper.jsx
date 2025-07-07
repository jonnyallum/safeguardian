import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { 
  ArrowLeft, 
  Heart, 
  MessageCircle, 
  Send, 
  Share, 
  MoreHorizontal,
  Camera,
  Mic,
  Image,
  Smile,
  AlertTriangle,
  Shield
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const PlatformWrapper = ({ platform, monitoringActive, onAlert }) => {
  const navigate = useNavigate()
  const { platformName } = useParams()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [riskLevel, setRiskLevel] = useState('low')

  // Simulated conversation data
  const conversations = {
    instagram: [
      { id: 1, sender: 'friend_user', message: 'Hey! How was school today?', time: '2:30 PM', isUser: false },
      { id: 2, sender: 'user', message: 'It was good! Had a math test', time: '2:31 PM', isUser: true },
      { id: 3, sender: 'friend_user', message: 'Nice! Want to hang out this weekend?', time: '2:32 PM', isUser: false },
    ],
    facebook: [
      { id: 1, sender: 'family_member', message: 'Don\'t forget about dinner tonight!', time: '1:15 PM', isUser: false },
      { id: 2, sender: 'user', message: 'I won\'t forget! See you at 6', time: '1:16 PM', isUser: true },
    ],
    snapchat: [
      { id: 1, sender: 'school_friend', message: '📸 Sent a snap', time: '3:45 PM', isUser: false },
      { id: 2, sender: 'user', message: '😂 That\'s hilarious!', time: '3:46 PM', isUser: true },
    ]
  }

  useEffect(() => {
    if (platformName && conversations[platformName]) {
      setMessages(conversations[platformName])
    }
  }, [platformName])

  // Simulate AI monitoring
  useEffect(() => {
    if (monitoringActive && newMessage) {
      const suspiciousKeywords = ['meet up', 'secret', 'don\'t tell', 'address', 'phone number']
      const hasSuspiciousContent = suspiciousKeywords.some(keyword => 
        newMessage.toLowerCase().includes(keyword)
      )
      
      if (hasSuspiciousContent) {
        setRiskLevel('high')
        onAlert({
          id: Date.now(),
          type: 'suspicious_message',
          platform: platformName,
          message: 'Potentially risky content detected in message',
          timestamp: new Date().toISOString(),
          severity: 'high'
        })
      } else {
        setRiskLevel('low')
      }
    }
  }, [newMessage, monitoringActive, platformName, onAlert])

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: Date.now(),
        sender: 'user',
        message: newMessage,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isUser: true
      }
      setMessages(prev => [...prev, message])
      setNewMessage('')
      
      // Simulate response after a delay
      setTimeout(() => {
        const responses = [
          'That sounds great!',
          'Cool! 😊',
          'Awesome!',
          'Nice!',
          'Sounds fun!'
        ]
        const response = {
          id: Date.now() + 1,
          sender: 'friend_user',
          message: responses[Math.floor(Math.random() * responses.length)],
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isUser: false
        }
        setMessages(prev => [...prev, response])
      }, 1000 + Math.random() * 2000)
    }
  }

  const getPlatformTheme = () => {
    switch (platformName) {
      case 'instagram':
        return {
          primary: 'from-purple-500 to-pink-500',
          bg: 'bg-black',
          accent: 'text-pink-400'
        }
      case 'facebook':
        return {
          primary: 'from-blue-600 to-blue-700',
          bg: 'bg-blue-900',
          accent: 'text-blue-400'
        }
      case 'snapchat':
        return {
          primary: 'from-yellow-400 to-yellow-500',
          bg: 'bg-yellow-900',
          accent: 'text-yellow-400'
        }
      default:
        return {
          primary: 'from-gray-600 to-gray-700',
          bg: 'bg-gray-900',
          accent: 'text-gray-400'
        }
    }
  }

  const theme = getPlatformTheme()

  return (
    <div className={`min-h-screen ${theme.bg} text-white flex flex-col`}>
      {/* Platform Header */}
      <div className={`bg-gradient-to-r ${theme.primary} p-4 flex items-center justify-between`}>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => navigate('/')}
            className="bg-white/20 hover:bg-white/30 p-2 rounded-full"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="font-semibold capitalize">{platformName}</h1>
            <p className="text-xs text-white/80">Protected by SafeGuardian</p>
          </div>
        </div>
        
        {/* Monitoring Indicator */}
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${
            riskLevel === 'high' ? 'bg-red-500 animate-pulse' : 'bg-green-500'
          }`}></div>
          <Shield className="w-5 h-5" />
        </div>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                  msg.isUser
                    ? `bg-gradient-to-r ${theme.primary} text-white`
                    : 'bg-gray-700 text-white'
                }`}
              >
                <p className="text-sm">{msg.message}</p>
                <p className="text-xs opacity-70 mt-1">{msg.time}</p>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-700 px-4 py-2 rounded-2xl">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Risk Warning */}
        {riskLevel === 'high' && (
          <div className="bg-red-500/20 border-t border-red-500/50 p-3">
            <div className="flex items-center gap-2 text-red-300">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">SafeGuardian detected potentially risky content</span>
            </div>
          </div>
        )}

        {/* Message Input */}
        <div className="border-t border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <Button className="bg-gray-700 hover:bg-gray-600 p-2 rounded-full">
              <Camera className="w-5 h-5" />
            </Button>
            
            <div className="flex-1 relative">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type a message..."
                className={`w-full bg-gray-700 border border-gray-600 rounded-full px-4 py-2 pr-12 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-opacity-50 ${
                  riskLevel === 'high' ? 'focus:ring-red-500 border-red-500/50' : 'focus:ring-blue-500'
                }`}
              />
              <Button
                onClick={handleSendMessage}
                className={`absolute right-1 top-1/2 transform -translate-y-1/2 bg-gradient-to-r ${theme.primary} hover:opacity-80 p-2 rounded-full`}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            
            <Button className="bg-gray-700 hover:bg-gray-600 p-2 rounded-full">
              <Mic className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Monitoring Status Bar */}
      <div className="bg-green-500/20 border-t border-green-500/50 p-2">
        <div className="flex items-center justify-center gap-2 text-green-300 text-xs">
          <Shield className="w-4 h-4" />
          <span>Protected by SafeGuardian AI • Real-time monitoring active</span>
        </div>
      </div>
    </div>
  )
}

export default PlatformWrapper

