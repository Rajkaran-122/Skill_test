import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from './components/layout/DashboardLayout'
import Dashboard from './pages/Dashboard'
import LiveFeeds from './pages/LiveFeeds'
import Alerts from './pages/Alerts'
import Stores from './pages/Stores'
import Login from './pages/Login'
import ProtectedRoute from './components/layout/ProtectedRoute'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/store/:storeId" element={<Dashboard />} />
            <Route path="/live" element={<LiveFeeds />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/stores" element={<Stores />} />
          </Route>
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
