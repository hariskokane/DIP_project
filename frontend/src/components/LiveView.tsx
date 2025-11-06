import { CheckCircle2, XCircle, AlertTriangle, Video, VideoOff } from 'lucide-react'
import { BottleData } from '../types'
import { useState, useEffect } from 'react'

interface LiveViewProps {
  currentBottle: BottleData | null
}

export default function LiveView({ currentBottle }: LiveViewProps) {
  const [cameraStatus, setCameraStatus] = useState<'loading' | 'active' | 'error'>('loading')

  useEffect(() => {
    // Check camera status
    const checkCamera = async () => {
      try {
        const response = await fetch('/api/camera-status')
        const data = await response.json()
        if (data.initialized && data.running) {
          setCameraStatus('active')
        } else {
          setCameraStatus('error')
        }
      } catch (error) {
        setCameraStatus('error')
      }
    }

    checkCamera()
    const interval = setInterval(checkCamera, 5000)
    return () => clearInterval(interval)
  }, [])

  // Audio alert for defective bottles - Loop every 5 seconds while defective
  useEffect(() => {
    let alertInterval: number | null = null
    
    const playAlert = () => {
      console.log('Playing alert sound...')
      const audio = new Audio('/alert.wav')
      audio.volume = 0.8
      audio.play()
        .then(() => console.log('Alert played'))
        .catch(error => {
          console.error('Audio error:', error)
          // Fallback
          const audioElement = document.createElement('audio')
          audioElement.src = '/alert.wav'
          audioElement.volume = 0.8
          audioElement.play().catch(e => console.error('Fallback failed:', e))
        })
    }
    
    if (currentBottle && currentBottle.Status === 'Defective') {
      // Play immediately when defective
      playAlert()
      
      // Then play every 5 seconds
      alertInterval = setInterval(() => {
        playAlert()
      }, 5000)
    } else {
      // Stop playing when non-defective
      if (alertInterval) {
        clearInterval(alertInterval)
      }
    }
    
    // Cleanup on unmount or when status changes
    return () => {
      if (alertInterval) {
        clearInterval(alertInterval)
      }
    }
  }, [currentBottle?.Status])

  if (!currentBottle) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-pulse bg-slate-700 rounded-full w-16 h-16 mx-auto mb-4"></div>
          <p className="text-slate-400 text-lg">Waiting for bottle detection...</p>
        </div>
      </div>
    )
  }

  const isDefective = currentBottle.Status === 'Defective'

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-12rem)]">
      {/* Camera Feed - Takes 1 column (1/3 width, full height) */}
      <div className="lg:col-span-1 bg-slate-800/50 rounded-2xl p-4 shadow-2xl border border-slate-700 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-white flex items-center">
            {cameraStatus === 'active' ? (
              <Video className="w-5 h-5 mr-2 text-green-400" />
            ) : (
              <VideoOff className="w-5 h-5 mr-2 text-red-400" />
            )}
            Live Camera Feed
          </h2>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
            cameraStatus === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              cameraStatus === 'active' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`}></div>
            <span className="text-sm font-medium">
              {cameraStatus === 'active' ? 'Live' : cameraStatus === 'loading' ? 'Loading...' : 'Offline'}
            </span>
          </div>
        </div>
        
        <div className="relative bg-black rounded-lg overflow-hidden flex-1">
          {cameraStatus === 'active' ? (
            <img
              src="/api/video-feed"
              alt="Live camera feed"
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <VideoOff className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Camera feed unavailable</p>
                <p className="text-slate-500 text-sm mt-2">Make sure the backend server is running</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status Panel - Takes 2 columns */}
      <div className="lg:col-span-2 flex flex-col gap-4 overflow-y-auto">
      {/* Current Status Card */}
      <div className={`rounded-xl p-6 shadow-2xl border-2 ${
        isDefective 
          ? 'bg-gradient-to-br from-red-900/40 to-red-800/20 border-red-500/50' 
          : 'bg-gradient-to-br from-green-900/40 to-green-800/20 border-green-500/50'
      }`}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white">Current Status</h3>
          {isDefective ? (
            <XCircle className="w-12 h-12 text-red-400" />
          ) : (
            <CheckCircle2 className="w-12 h-12 text-green-400" />
          )}
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4">
          <div className={`inline-flex items-center px-6 py-3 rounded-full font-bold text-2xl ${
            isDefective 
              ? 'bg-red-500/20 text-red-400 border-2 border-red-500/50' 
              : 'bg-green-500/20 text-green-400 border-2 border-green-500/50'
          }`}>
            {currentBottle.Status}
          </div>
        </div>
      </div>

      {/* Component Checks Card */}
      <div className="bg-slate-800/50 rounded-xl p-6 shadow-2xl border border-slate-700">
        <h3 className="text-2xl font-bold text-white mb-6">Component Checks</h3>

        <div className="space-y-4">
          {/* Cap Check */}
          <div className="bg-slate-700/30 rounded-lg p-5 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                currentBottle.Cap === 'Detected' 
                  ? 'bg-green-500/20' 
                  : currentBottle.Cap === 'Missing'
                  ? 'bg-red-500/20'
                  : 'bg-yellow-500/20'
              }`}>
                {currentBottle.Cap === 'Detected' ? (
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                ) : currentBottle.Cap === 'Missing' ? (
                  <XCircle className="w-6 h-6 text-red-400" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-yellow-400" />
                )}
              </div>
              <div>
                <p className="text-white font-semibold text-lg">Cap</p>
                <p className="text-sm text-slate-400">Bottle cap inspection</p>
              </div>
            </div>
            <span className={`font-bold text-lg ${
              currentBottle.Cap === 'Detected' 
                ? 'text-green-400' 
                : currentBottle.Cap === 'Missing'
                ? 'text-red-400'
                : 'text-yellow-400'
            }`}>
              {currentBottle.Cap}
            </span>
          </div>

          {/* Label Check */}
          <div className="bg-slate-700/30 rounded-lg p-5 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                currentBottle.Label === 'Detected' 
                  ? 'bg-green-500/20' 
                  : currentBottle.Label === 'Missing'
                  ? 'bg-red-500/20'
                  : 'bg-yellow-500/20'
              }`}>
                {currentBottle.Label === 'Detected' ? (
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                ) : currentBottle.Label === 'Missing' ? (
                  <XCircle className="w-6 h-6 text-red-400" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-yellow-400" />
                )}
              </div>
              <div>
                <p className="text-white font-semibold text-lg">Label</p>
                <p className="text-sm text-slate-400">Label presence check</p>
              </div>
            </div>
            <span className={`font-bold text-lg ${
              currentBottle.Label === 'Detected' 
                ? 'text-green-400' 
                : currentBottle.Label === 'Missing'
                ? 'text-red-400'
                : 'text-yellow-400'
            }`}>
              {currentBottle.Label}
            </span>
          </div>

          {/* Plastic Check */}
          <div className="bg-slate-700/30 rounded-lg p-5 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                currentBottle.Plastic === 'Good' 
                  ? 'bg-green-500/20' 
                  : 'bg-red-500/20'
              }`}>
                {currentBottle.Plastic === 'Good' ? (
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-400" />
                )}
              </div>
              <div>
                <p className="text-white font-semibold text-lg">Plastic Quality</p>
                <p className="text-sm text-slate-400">Damage detection</p>
              </div>
            </div>
            <span className={`font-bold text-lg ${
              currentBottle.Plastic === 'Good' ? 'text-green-400' : 'text-red-400'
            }`}>
              {currentBottle.Plastic}
            </span>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}
