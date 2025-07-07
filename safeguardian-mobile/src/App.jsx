import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <div className="text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">🛡️</span>
        </div>
        <h1 className="text-3xl font-bold mb-2">SafeGuardian</h1>
        <p className="text-gray-400 mb-6">Your digital protection companion</p>
        
        <button 
          onClick={() => setCount(count + 1)}
          className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black px-6 py-3 rounded-lg font-semibold hover:from-yellow-500 hover:to-yellow-700 transition-all"
        >
          Test Button (Clicked {count} times)
        </button>
        
        <div className="mt-8 text-sm text-gray-500">
          <p>SafeGuardian Mobile App - Test Version</p>
          <p>React app is working correctly!</p>
        </div>
      </div>
    </div>
  )
}

export default App

