import { useState, useEffect } from 'react'
import { Package } from 'lucide-react'
import LiveView from './components/LiveView'
import { BottleData } from './types'

function App() {
  const [currentBottle, setCurrentBottle] = useState<BottleData | null>(null)

  // Fetch current bottle data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/current')
        const data = await response.json()
        if (data) {
          setCurrentBottle(data)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 1000) // Poll every second

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2 rounded-lg">
                <Package className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Defect Detection System</h1>
                <p className="text-sm text-slate-400">Real-time Quality Control</p>
              </div>
            </div>
            
          </div>

        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <LiveView currentBottle={currentBottle} />
      </main>
    </div>
  )
}

export default App
