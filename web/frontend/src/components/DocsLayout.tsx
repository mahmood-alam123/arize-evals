import { Link, useLocation, Outlet } from 'react-router-dom'

const navigation = [
  {
    title: 'Getting Started',
    items: [
      { title: 'Introduction', href: '/docs' },
      { title: 'Quickstart', href: '/docs/quickstart' },
      { title: 'Installation', href: '/docs/installation' },
    ],
  },
  {
    title: 'Configuration',
    items: [
      { title: 'Config File', href: '/docs/config' },
      { title: 'App Types', href: '/docs/app-types' },
      { title: 'Datasets', href: '/docs/datasets' },
      { title: 'Thresholds', href: '/docs/thresholds' },
    ],
  },
  {
    title: 'Evaluation',
    items: [
      { title: 'Eval Suites', href: '/docs/eval-suites' },
      { title: 'Custom Evaluators', href: '/docs/custom-evaluators' },
      { title: 'Failure Analysis', href: '/docs/failure-analysis' },
    ],
  },
  {
    title: 'CLI Reference',
    items: [
      { title: 'ci-run', href: '/docs/cli/ci-run' },
      { title: 'dashboard', href: '/docs/cli/dashboard' },
    ],
  },
  {
    title: 'Dashboard',
    items: [
      { title: 'Overview', href: '/docs/dashboard' },
      { title: 'API Reference', href: '/docs/api' },
    ],
  },
]

export default function DocsLayout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Light header for docs */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center transition-transform group-hover:scale-105">
                <span className="text-white font-bold text-sm">CE</span>
              </div>
              <span className="font-semibold text-lg text-gray-900">Company Eval</span>
            </Link>

            {/* Actions */}
            <div className="flex items-center gap-3">
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

      <div className="flex pt-16">
        {/* Sidebar */}
        <aside className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 overflow-y-auto p-6">
          <nav className="space-y-8">
            {navigation.map((section) => (
              <div key={section.title}>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  {section.title}
                </h3>
                <ul className="space-y-1">
                  {section.items.map((item) => (
                    <li key={item.href}>
                      <Link
                        to={item.href}
                        className={`light-sidebar-link ${
                          location.pathname === item.href ? 'light-sidebar-link-active' : ''
                        }`}
                      >
                        {item.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 ml-64 min-h-[calc(100vh-4rem)]">
          <div className="max-w-4xl mx-auto px-8 py-12">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
