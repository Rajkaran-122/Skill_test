import { useState } from 'react'

interface ExportReportModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function ExportReportModal({ isOpen, onClose }: ExportReportModalProps) {
  const [isExporting, setIsExporting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [format, setFormat] = useState('pdf')

  if (!isOpen) return null

  const handleExport = () => {
    setIsExporting(true)
    // Simulate network delay
    setTimeout(() => {
      setIsExporting(false)
      setIsSuccess(true)
      
      // Reset and close after a short delay
      setTimeout(() => {
        setIsSuccess(false)
        onClose()
      }, 2000)
    }, 2500)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-dark-bg-primary/50 backdrop-blur-sm transition-opacity">
      <div className="glass-card rounded-2xl shadow-xl w-full max-w-md overflow-hidden transform transition-all">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border-default flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-accent-blue/10 text-accent-blue rounded-lg text-text-primary">
              <svg className="w-5 h-5 text-accent-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-text-primary">Export Report</h3>
          </div>
          <button 
            onClick={onClose}
            className="text-text-secondary hover:text-text-secondary transition-colors p-1 rounded-md hover:bg-dark-bg-hover"
            disabled={isExporting}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {!isSuccess ? (
            <>
              {/* Date Range (Simulated) */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-text-primary">Date Range</label>
                <select className="w-full bg-dark-bg-hover border border-border-strong text-text-primary text-sm rounded-lg focus:ring-accent-blue focus:border-indigo-500 block p-2.5 outline-none transition-colors">
                  <option>Today</option>
                  <option>Last 7 Days</option>
                  <option>Last 30 Days</option>
                  <option>This Month</option>
                  <option>Custom Range...</option>
                </select>
              </div>

              {/* Format Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-text-primary">File Format</label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setFormat('pdf')}
                    className={`flex items-center justify-center py-3 border rounded-xl font-medium transition-all ${
                      format === 'pdf' 
                        ? 'border-indigo-600 bg-accent-blue/10 text-accent-blue text-accent-blue' 
                        : 'border-border-strong glass-card text-text-secondary hover:bg-dark-bg-hover'
                    }`}
                  >
                    PDF Document
                  </button>
                  <button
                    onClick={() => setFormat('csv')}
                    className={`flex items-center justify-center py-3 border rounded-xl font-medium transition-all ${
                      format === 'csv' 
                        ? 'border-indigo-600 bg-accent-blue/10 text-accent-blue text-accent-blue' 
                        : 'border-border-strong glass-card text-text-secondary hover:bg-dark-bg-hover'
                    }`}
                  >
                    CSV Spreadsheet
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <div className="h-16 w-16 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 animate-bounce">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-text-primary">Export Complete!</p>
              <p className="text-sm text-text-secondary text-center">Your report has been downloaded successfully.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {!isSuccess && (
          <div className="px-6 py-4 bg-dark-bg-hover border-t border-border-default flex justify-end gap-3">
            <button
              onClick={onClose}
              disabled={isExporting}
              className="px-4 py-2 text-sm font-medium text-text-primary glass-card border border-border-strong rounded-lg hover:bg-dark-bg-hover transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-text-primary glass-card rounded-lg hover:bg-accent-blue btn-shimmer transition-colors disabled:opacity-70 min-w-[140px] justify-center"
            >
              {isExporting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download Report
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
