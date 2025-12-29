import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Header() {
  const location = useLocation()
  const [scrolled, setScrolled] = useState(false)
  const isLandingPage = location.pathname === '/'

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // Check initial state

    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const isActive = (path: string) => {
    if (path === '/docs') {
      return location.pathname.startsWith('/docs')
    }
    if (path === '/dashboard') {
      return location.pathname.startsWith('/dashboard') || location.pathname.startsWith('/runs')
    }
    return location.pathname === path
  }

  // On landing page: transparent at top, black when scrolled
  // On other pages: always black/80 with blur
  const headerBg = isLandingPage
    ? scrolled
      ? 'bg-black border-white/10'
      : 'bg-transparent border-transparent'
    : 'bg-black/80 backdrop-blur-xl border-white/10'

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 border-b transition-all duration-300 ${headerBg}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center transition-transform group-hover:scale-105">
              <span className="text-white font-bold text-sm">CE</span>
            </div>
            <span className="font-semibold text-lg text-white">Company Eval</span>
          </Link>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Link
              to="/docs"
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                isActive('/docs')
                  ? 'text-white bg-white/10'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              Docs
            </Link>
            <Link
              to="/dashboard"
              className={`btn ${
                isActive('/dashboard') ? 'btn-primary' : 'btn-secondary'
              }`}
            >
              {isActive('/dashboard') ? 'Dashboard' : 'Sign In'}
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
