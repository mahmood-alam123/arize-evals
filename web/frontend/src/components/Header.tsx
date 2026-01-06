import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import NttDataLogo from '/workspaces/arize-evals/web/frontend/src/images/GlobalLogo_NTTDATA_FutureBlue_RGB.png'


interface HeaderProps {
  variant?: 'dark' | 'light'
}

export default function Header({ variant = 'dark' }: HeaderProps) {
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
      return location.pathname.startsWith('/dashboard') || location.pathname.startsWith('/runs') || location.pathname.startsWith('/traces')
    }
    return location.pathname === path
  }

  // Light variant: white background with gray border
  if (variant === 'light') {
    return (
      <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 group">
              <img
                src={NttDataLogo}
                alt="NTT DATA"
                className="h-10 w-auto object-contain translate-y-[2px]"
              />
              <span className="font-semibold text-lg text-gray-900 leading-none">
                Company Eval
              </span>
            </Link>


            {/* Actions */}
            <div className="flex items-center gap-3">
              <Link
                to="/docs"
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive('/docs')
                    ? 'text-gray-900 bg-gray-100'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                Docs
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-all duration-200 bg-gray-900 text-white hover:bg-gray-800"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>
    )
  }

  // Dark variant (default): for landing page
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
          <Link to="/" className="flex items-center gap-2 group">
            <img
              src={NttDataLogo}
              alt="NTT DATA"
              className="h-10 w-auto object-contain translate-y-[2px]"
            />
            <span className="font-semibold text-lg text-white leading-none">
              Company Eval
            </span>
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
