import { Link, useLocation, Outlet } from 'react-router-dom'
import { useEffect, useState } from 'react'

interface TocItem {
  id: string
  text: string
  level: number
}

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
    title: 'Core Concepts',
    items: [
      { title: 'How It Works', href: '/docs/how-it-works' },
      { title: 'Tracing', href: '/docs/tracing' },
      { title: 'Evaluation Metrics', href: '/docs/metrics' },
      { title: 'Failure Analysis', href: '/docs/failure-analysis' },
    ],
  },
  {
    title: 'Guides',
    items: [
      { title: 'Basic Chat', href: '/docs/use-cases/chat' },
      { title: 'RAG', href: '/docs/use-cases/rag' },
      { title: 'Agent', href: '/docs/use-cases/agents' },
      { title: 'Custom Evaluators', href: '/docs/custom-evaluators' },
    ],
  },
  {
    title: 'Tools & Integration',
    items: [
      { title: 'SDK', href: '/docs/sdk' },
      { title: 'CLI', href: '/docs/cli/ci-run' },
      { title: 'CI/CD', href: '/docs/cicd' },
      { title: 'Quality Dashboard', href: '/docs/dashboard' },
    ],
  },
  {
    title: 'Reference',
    items: [
      { title: 'Configuration', href: '/docs/config' },
      { title: 'API Reference', href: '/docs/api' },
      { title: 'Integrations', href: '/docs/integrations' },
    ],
  },
]

export default function DocsLayout() {
  const location = useLocation()
  const [toc, setToc] = useState<TocItem[]>([])
  const [activeId, setActiveId] = useState<string>('')

  // Extract headings from the page content
  useEffect(() => {
    const timer = setTimeout(() => {
      const article = document.querySelector('.docs-content')
      if (!article) return

      const headings = article.querySelectorAll('h2, h3')
      const items: TocItem[] = []

      headings.forEach((heading) => {
        const text = heading.textContent || ''
        // Create an ID if one doesn't exist
        if (!heading.id) {
          heading.id = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
        }
        items.push({
          id: heading.id,
          text,
          level: heading.tagName === 'H2' ? 2 : 3,
        })
      })

      setToc(items)
    }, 100)

    return () => clearTimeout(timer)
  }, [location.pathname])

  // Track active heading on scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        })
      },
      { rootMargin: '-80px 0px -80% 0px' }
    )

    toc.forEach((item) => {
      const element = document.getElementById(item.id)
      if (element) observer.observe(element)
    })

    return () => observer.disconnect()
  }, [toc])

  const scrollToHeading = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      const top = element.getBoundingClientRect().top + window.scrollY - 100
      window.scrollTo({ top, behavior: 'smooth' })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Light header for docs */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
        <div className="px-4 sm:px-6 lg:px-8">
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
        {/* Left Sidebar - Navigation */}
        <aside className="fixed left-0 top-16 bottom-0 w-56 bg-white border-r border-gray-200 overflow-y-auto p-4">
          <nav className="space-y-6">
            {navigation.map((section) => (
              <div key={section.title}>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
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
        <main className="flex-1 ml-56 mr-56 min-h-[calc(100vh-4rem)]">
          <div className="max-w-3xl mx-auto px-8 py-12">
            <Outlet />
          </div>
        </main>

        {/* Right Sidebar - Table of Contents */}
        <aside className="fixed right-0 top-16 bottom-0 w-56 bg-white border-l border-gray-200 overflow-y-auto p-4 hidden lg:block">
          {toc.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                On this page
              </h4>
              <nav className="space-y-1">
                {toc.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToHeading(item.id)}
                    className={`block w-full text-left text-sm py-1 transition-colors ${
                      item.level === 3 ? 'pl-3' : ''
                    } ${
                      activeId === item.id
                        ? 'text-blue-600 font-medium'
                        : 'text-gray-500 hover:text-gray-900'
                    }`}
                  >
                    {item.text}
                  </button>
                ))}
              </nav>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}
