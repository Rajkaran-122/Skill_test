import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, User, Eye, EyeOff } from 'lucide-react'
import { useAuthStore } from '../hooks/useAuthStore'

export default function Login() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    const success = await login(password, username)
    if (success) {
      navigate('/')
    } else {
      setError('Invalid username or password. Use admin / admin')
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg-primary flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-accent-blue/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-accent-purple/10 blur-[120px] pointer-events-none" />

      <div className="w-full max-w-md">
        <div className="glass-light border border-border-default rounded-3xl p-8 shadow-2xl relative z-10 backdrop-blur-xl">
          
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-accent-blue to-accent-purple mb-2">
              Store Intelligence
            </h1>
            <p className="text-text-secondary text-sm">Sign in to access your dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              {/* Username Input */}
              <div className="relative">
                <label className="block text-xs font-medium text-text-tertiary mb-1.5 uppercase tracking-wider">
                  Username
                </label>
                <div className="relative flex items-center">
                  <User className="absolute left-3 h-5 w-5 text-text-tertiary" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full bg-dark-bg-secondary/50 border border-border-default rounded-xl py-2.5 pl-10 pr-4 text-text-primary placeholder-text-tertiary focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/50 transition-all duration-300"
                    placeholder="Enter username"
                    required
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="relative">
                <label className="block text-xs font-medium text-text-tertiary mb-1.5 uppercase tracking-wider">
                  Password
                </label>
                <div className="relative flex items-center">
                  <Lock className="absolute left-3 h-5 w-5 text-text-tertiary" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-dark-bg-secondary/50 border border-border-default rounded-xl py-2.5 pl-10 pr-12 text-text-primary placeholder-text-tertiary focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/50 transition-all duration-300"
                    placeholder="Enter password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 p-1 text-text-tertiary hover:text-text-primary transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <div className="text-accent-red text-sm bg-accent-red/10 border border-accent-red/20 rounded-lg p-3 text-center animate-fade-in">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-accent-blue to-accent-purple hover:opacity-90 text-white font-medium py-3 rounded-xl transition-all duration-300 shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)] transform hover:-translate-y-0.5"
            >
              Sign In
            </button>
          </form>

          <div className="mt-8 text-center border-t border-border-default pt-6">
            <p className="text-xs text-text-tertiary">
              Demo Credentials:<br/>
              <span className="font-mono text-text-secondary">admin</span> / <span className="font-mono text-text-secondary">admin</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
