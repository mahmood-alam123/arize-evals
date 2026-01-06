import { Link } from 'react-router-dom'
import Header from '../components/Header'
import NttDataLogo from '/workspaces/arize-evals/web/frontend/src/images/GlobalLogo_NTTDATA_FutureBlue_RGB.png'


function Landing() {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Ambient glow effects - positioned lights */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden z-0">
        {/* Top left glow - blue */}
        <div className="absolute -top-[300px] -left-[200px] w-[900px] h-[900px] bg-gradient-radial from-blue-600/50 via-blue-500/25 to-transparent blur-[100px]" />

        {/* Top right glow - cyan */}
        <div className="absolute -top-[200px] -right-[100px] w-[750px] h-[750px] bg-gradient-radial from-cyan-500/45 via-blue-400/20 to-transparent blur-[80px]" />

        {/* Middle left glow - blue */}
        <div className="absolute top-[35%] -left-[150px] w-[650px] h-[650px] bg-gradient-radial from-blue-500/45 via-cyan-500/20 to-transparent blur-[80px]" />

        {/* Middle right glow - blue */}
        <div className="absolute top-[55%] -right-[100px] w-[550px] h-[550px] bg-gradient-radial from-blue-500/45 via-cyan-500/20 to-transparent blur-[70px]" />

        {/* Bottom center glow - blue */}
        <div className="absolute -bottom-[100px] left-1/2 -translate-x-1/2 w-[1200px] h-[550px] bg-gradient-radial from-blue-600/50 via-blue-500/25 to-transparent blur-[100px]" />
      </div>

      <Header />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 grid-bg opacity-50" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-radial from-blue-500/15 via-transparent to-transparent opacity-60 blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
              <span className="text-white">Ship LLM Features</span>
              <br />
              <span className="bg-gradient-to-r from-blue-400 via-blue-300 to-cyan-300 bg-clip-text text-transparent">
                With Confidence
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-white/60 max-w-2xl mx-auto mb-10">
              Automated quality gates for your AI applications. Catch regressions before your users do with LLM-powered evaluation pipelines.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/docs/quickstart" className="btn btn-primary px-8 py-3 text-lg">
                Get Started
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <Link to="/dashboard" className="btn btn-secondary px-8 py-3 text-lg">
                View Demo
              </Link>
            </div>

            {/* Code preview */}
            <div className="mt-16 relative">
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-10 pointer-events-none" />
              <div className="card p-6 text-left max-w-2xl mx-auto">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  <span className="ml-4 text-xs text-white/40 font-mono">terminal</span>
                </div>
                <pre className="text-sm">
                  <code className="text-white/80">
                    <span className="text-white/40">$</span> pip install company-eval-framework{'\n'}
                    <span className="text-white/40">$</span> company-eval ci-run --config eval.yaml{'\n'}
                    {'\n'}
                    <span className="text-emerald-400">✓</span> user_frustration: 0.08 (threshold: ≤0.30) <span className="text-emerald-400">PASS</span>{'\n'}
                    <span className="text-emerald-400">✓</span> helpfulness:      0.92 (threshold: ≥0.70) <span className="text-emerald-400">PASS</span>{'\n'}
                    <span className="text-emerald-400">✓</span> toxicity:         0.00 (threshold: ≤0.05) <span className="text-emerald-400">PASS</span>{'\n'}
                    {'\n'}
                    <span className="text-emerald-400 font-semibold">FINAL RESULT: PASS</span>
                  </code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-24 relative">
        <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-radial from-purple-600/12 via-transparent to-transparent blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Built for every LLM use case
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              Pre-built evaluation suites tailored to your application type
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Basic Chat */}
            <Link to="/docs/use-cases/chat" className="card card-hover p-8 group">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30 flex items-center justify-center mb-6 group-hover:from-blue-500/30 group-hover:to-cyan-500/30 transition-colors">
                <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Basic Chat</h3>
              <p className="text-white/50 text-sm leading-relaxed mb-4">
                Q&A bots, conversational interfaces, and customer support assistants.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 text-xs rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">Helpfulness</span>
                <span className="px-2 py-1 text-xs rounded-full bg-red-500/10 text-red-400 border border-red-500/20">Toxicity</span>
                <span className="px-2 py-1 text-xs rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">Frustration</span>
              </div>
            </Link>

            {/* RAG */}
            <Link to="/docs/use-cases/rag" className="card card-hover p-8 group">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 flex items-center justify-center mb-6 group-hover:from-emerald-500/30 group-hover:to-teal-500/30 transition-colors">
                <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">RAG</h3>
              <p className="text-white/50 text-sm leading-relaxed mb-4">
                Retrieval-Augmented Generation apps that answer questions from your documents.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 text-xs rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Hallucination</span>
                <span className="px-2 py-1 text-xs rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Relevance</span>
                <span className="px-2 py-1 text-xs rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">Groundedness</span>
              </div>
            </Link>

            {/* Agent / Multi-agent */}
            <Link to="/docs/use-cases/agents" className="card card-hover p-8 group">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 flex items-center justify-center mb-6 group-hover:from-purple-500/30 group-hover:to-pink-500/30 transition-colors">
                <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Agent / Multi-agent</h3>
              <p className="text-white/50 text-sm leading-relaxed mb-4">
                Tool-using agents and coordinated multi-agent systems.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 text-xs rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">Planning</span>
                <span className="px-2 py-1 text-xs rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">Tool Use</span>
                <span className="px-2 py-1 text-xs rounded-full bg-pink-500/10 text-pink-400 border border-pink-500/20">Coordination</span>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Tooling Section */}
      <section className="py-24 border-t border-white/10 relative">
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-radial from-cyan-600/12 via-transparent to-transparent blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Multiple ways to integrate
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              Use the tooling that fits your workflow
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {/* SDK */}
            <Link to="/docs/sdk" className="card card-hover p-6 text-center group">
              <div className="w-14 h-14 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-500/20 transition-colors">
                <svg className="w-7 h-7 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">SDK</h3>
              <p className="text-white/50 text-sm">Python SDK for programmatic evaluation</p>
            </Link>

            {/* CLI */}
            <Link to="/docs/cli/ci-run" className="card card-hover p-6 text-center group">
              <div className="w-14 h-14 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-500/20 transition-colors">
                <svg className="w-7 h-7 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">CLI</h3>
              <p className="text-white/50 text-sm">Command-line interface for running evals</p>
            </Link>

            {/* CI/CD */}
            <Link to="/docs/cicd" className="card card-hover p-6 text-center group">
              <div className="w-14 h-14 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-500/20 transition-colors">
                <svg className="w-7 h-7 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">CI/CD</h3>
              <p className="text-white/50 text-sm">GitHub Actions for automated testing</p>
            </Link>

            {/* MCP Server */}
            <Link to="/docs/mcp" className="card card-hover p-6 text-center group">
              <div className="w-14 h-14 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mx-auto mb-4 group-hover:bg-orange-500/20 transition-colors">
                <svg className="w-7 h-7 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">MCP Server</h3>
              <p className="text-white/50 text-sm">Model Context Protocol for AI assistants</p>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 relative">
        {/* Section ambient glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[700px] bg-gradient-radial from-blue-600/12 via-transparent to-transparent blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything you need for LLM quality
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              A complete evaluation framework that integrates with your development workflow
            </p>
          </div>

          <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
            {/* Feature 1 - Quality Dashboard */}
            <Link to="/docs/dashboard" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-4 group-hover:bg-orange-500/20 transition-colors">
                <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Quality Dashboard</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Track quality over time with a beautiful dashboard. See trends, drill into failures, compare runs.
              </p>
            </Link>

            {/* Feature 2 - CI/CD Quality Gates */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">CI/CD Quality Gates</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Automatically block PRs that don't meet quality thresholds. Define pass/fail criteria for each metric.
              </p>
            </div>

            {/* Feature 3 - Static Datasets */}
            <Link to="/docs/datasets" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4 group-hover:bg-emerald-500/20 transition-colors">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Static Datasets</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Curated test cases for regression testing. Track quality trends with consistent inputs across runs.
              </p>
            </Link>

            {/* Feature 3 - Synthetic Datasets */}
            <Link to="/docs/datasets" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-4 group-hover:bg-violet-500/20 transition-colors">
                <svg className="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Synthetic Datasets</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Auto-generate test cases with LLMs. Broader coverage with fresh inputs tailored to your app.
              </p>
            </Link>

            {/* Feature 4 - Failure Analysis */}
            <Link to="/docs/failure-analysis" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition-colors">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Failure Analysis</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Axial coding categorizes failures by type. See exactly what went wrong with detailed breakdowns.
              </p>
            </Link>

            {/* Feature 5 - Custom Evaluators */}
            <Link to="/docs/custom-evaluators" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-4 group-hover:bg-amber-500/20 transition-colors">
                <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Custom Evaluators</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Define your own LLM-as-judge evaluators with custom prompts and rubrics for domain-specific needs.
              </p>
            </Link>

            {/* Feature 6 - Slack/Teams Notifications */}
            <Link to="/docs/integrations" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-fuchsia-500/10 border border-fuchsia-500/20 flex items-center justify-center mb-4 group-hover:bg-fuchsia-500/20 transition-colors">
                <svg className="w-6 h-6 text-fuchsia-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Slack & Teams Alerts</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Get notified when evals fail. Webhook integrations for Slack and Microsoft Teams.
              </p>
            </Link>

            {/* Feature 8 - Cost Tracking */}
            <Link to="/dashboard" className="card card-hover p-6 group">
              <div className="w-12 h-12 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center mb-4 group-hover:bg-teal-500/20 transition-colors">
                <svg className="w-6 h-6 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Cost Tracking</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Track OpenAI/Azure spend per evaluation run. Know exactly what your quality assurance costs.
              </p>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        {/* Section ambient lights */}
        <div className="absolute top-1/2 -left-[80px] w-[350px] h-[350px] bg-gradient-radial from-indigo-600/18 via-transparent to-transparent blur-[80px] pointer-events-none" />
        <div className="absolute top-1/2 -right-[80px] w-[350px] h-[350px] bg-gradient-radial from-purple-600/18 via-transparent to-transparent blur-[80px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative card p-12 md:p-16 text-center overflow-hidden">
            {/* Card glow effects */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-radial from-blue-500/20 via-transparent to-transparent blur-[80px]" />

            <div className="relative">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Ready to ship with confidence?
              </h2>
              <p className="text-white/50 text-lg max-w-xl mx-auto mb-8">
                Start evaluating your LLM applications in minutes. Open source and free forever.
              </p>
              <Link to="/docs/quickstart" className="btn btn-primary px-8 py-3 text-lg">
                Read the Docs
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <img
                src={NttDataLogo}
                alt="NTT DATA"
                className="h-10 w-auto object-contain translate-y-[2px]"
              />
              <span className="font-semibold text-lg text-white leading-none">
                Company Eval
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-white/50">
              <Link to="/docs" className="hover:text-white transition-colors">Docs</Link>
              <span>Built with Phoenix Evals</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Landing
