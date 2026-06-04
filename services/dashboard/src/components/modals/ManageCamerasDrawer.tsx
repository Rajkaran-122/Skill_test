import { useState } from 'react'

interface ManageCamerasDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export default function ManageCamerasDrawer({ isOpen, onClose }: ManageCamerasDrawerProps) {
  const [cameras, setCameras] = useState([
    { id: 'CAM01', name: 'Main Entrance', status: 'online', res: '1080p', active: true },
    { id: 'CAM02', name: 'Skincare Aisle', status: 'online', res: '1080p', active: true },
    { id: 'CAM03', name: 'Electronics', status: 'offline', res: '4K', active: false },
    { id: 'CAM04', name: 'Checkout Zone', status: 'online', res: '1080p', active: true },
    { id: 'CAM05', name: 'Main Exit', status: 'online', res: '1080p', active: true },
  ])

  const toggleCamera = (id: string) => {
    setCameras(cameras.map(c => 
      c.id === id ? { ...c, active: !c.active, status: !c.active ? 'online' : 'offline' } : c
    ))
  }

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 glass-card backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div 
        className={`fixed inset-y-0 right-0 z-50 w-full max-w-md glass-card shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-border-default">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-dark-bg-primary text-text-primary rounded-lg">
              
            </div>
            <div>
              <h2 className="text-xl font-bold text-text-primary">🎥 Manage Cameras</h2>
              <p className="text-sm text-text-secondary">Configure CV pipeline inputs</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-text-secondary hover:text-text-secondary hover:bg-dark-bg-hover rounded-full transition-colors"
          >
            
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Action Bar */}
          <button className="w-full flex items-center justify-center gap-2 py-3 border-2 border-dashed border-white/20 text-text-primary font-medium rounded-xl hover:bg-text-primary text-dark-bg-primary/10 hover:border-white/50 transition-colors">
            
            Add New Camera Stream
          </button>

          {/* Camera List */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">Configured Devices</h3>
            
            {cameras.map((cam) => (
              <div 
                key={cam.id} 
                className={`flex items-center justify-between p-4 rounded-xl border transition-colors ${
                  cam.active ? 'border-white/20 bg-text-primary text-dark-bg-primary/10' : 'border-border-strong glass-card'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className={`p-3 rounded-xl ${cam.active ? 'bg-accent-blue/10 text-accent-blue0/20 text-text-primary' : 'bg-dark-bg-hover text-text-secondary'}`}>
                      
                    </div>
                    <span className={`absolute -top-1 -right-1 h-3.5 w-3.5 border-2 border-white rounded-full ${
                      cam.status === 'online' ? 'bg-emerald-500' : 'bg-rose-500'
                    }`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-text-primary flex items-center gap-2">
                      {cam.id} 
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-dark-bg-tertiary text-text-secondary">{cam.res}</span>
                    </h4>
                    <p className="text-xs font-medium text-text-secondary mt-0.5">{cam.name}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <button className="p-1.5 text-text-secondary hover:text-text-primary transition-colors">
                    
                  </button>
                  <button 
                    onClick={() => toggleCamera(cam.id)}
                    className={`p-2 rounded-lg transition-colors ${
                      cam.active 
                        ? 'bg-rose-500/20 text-rose-400 hover:bg-rose-500/30' 
                        : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                    }`}
                    title={cam.active ? 'Disable Camera' : 'Enable Camera'}
                  >
                    
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Footer */}
        <div className="p-6 border-t border-border-default bg-dark-bg-hover">
          <p className="text-xs text-text-secondary text-center mb-4">
            Changes to camera states will trigger a restart of the associated CV-Pipeline containers.
          </p>
          <button 
            onClick={onClose}
            className="w-full py-3 bg-text-primary text-dark-bg-primary hover:bg-dark-bg-tertiary text-black font-semibold rounded-xl transition-colors shadow-sm shadow-white/10"
          >
            Apply Configurations
          </button>
        </div>
      </div>
    </>
  )
}
