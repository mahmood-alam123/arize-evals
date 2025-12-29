import { Link } from 'react-router-dom'
import Header from '../components/Header'

function Landing() {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Ambient glow effects - positioned lights */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        {/* Top left glow - blue/purple */}
        <div className="absolute -top-[350px] -left-[250px] w-[800px] h-[800px] bg-gradient-radial from-blue-600/25 via-purple-600/10 to-transparent blur-[120px] animate-glow-slow" />

        {/* Top right glow - cyan/teal */}
        <div className="absolute -top-[250px] -right-[150px] w-[650px] h-[650px] bg-gradient-radial from-cyan-500/20 via-teal-500/8 to-transparent blur-[100px] animate-glow-pulse" />

        {/* Middle left glow - purple */}
        <div className="absolute top-[40%] -left-[180px] w-[550px] h-[550px] bg-gradient-radial from-purple-600/18 via-indigo-600/8 to-transparent blur-[100px] animate-glow-pulse" style={{ animationDelay: '2s' }} />

        {/* Middle right glow - blue */}
        <div className="absolute top-[60%] -right-[120px] w-[450px] h-[450px] bg-gradient-radial from-blue-500/20 via-cyan-500/8 to-transparent blur-[90px] animate-glow-slow" style={{ animationDelay: '4s' }} />

        {/* Bottom center glow - mixed */}
        <div className="absolute -bottom-[150px] left-1/2 -translate-x-1/2 w-[1000px] h-[450px] bg-gradient-radial from-indigo-600/22 via-purple-600/10 to-transparent blur-[120px] animate-glow-pulse" style={{ animationDelay: '1s' }} />
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

      {/* Stats Section */}
      <section className="py-16 border-y border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-4xl font-bold text-white">4</div>
              <div className="text-white/50 text-sm">App Types</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-white">10+</div>
              <div className="text-white/50 text-sm">Built-in Evaluators</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-white">CI/CD</div>
              <div className="text-white/50 text-sm">Native Integration</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-white">100%</div>
              <div className="text-white/50 text-sm">Open Source</div>
            </div>
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

          <div className="grid md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Quality Gates</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Automatically block PRs that don't meet quality thresholds. Define pass/fail criteria for each metric.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Multiple App Types</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Pre-built evaluation suites for Chat, RAG, Agents, and Multi-Agent systems. Works out of the box.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Failure Analysis</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                When tests fail, get detailed axial coding that categorizes failures and explains what went wrong.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Quality Dashboard</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Track quality over time with a beautiful dashboard. See trends, drill into failures, compare runs.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">CLI-First</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                One command to run evaluations. Integrate into any CI/CD pipeline with exit codes for automation.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="card card-hover p-6">
              <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Phoenix Evals</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Built on Arize Phoenix Evals. Production-grade LLM judges for hallucination, toxicity, and more.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 border-t border-white/10 relative">
        {/* Dual glow effect */}
        <div className="absolute top-0 left-[20%] w-[450px] h-[450px] bg-gradient-radial from-purple-600/15 via-transparent to-transparent blur-[100px] pointer-events-none" />
        <div className="absolute bottom-0 right-[20%] w-[450px] h-[450px] bg-gradient-radial from-cyan-600/15 via-transparent to-transparent blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              How it works
            </h2>
            <p className="text-white/50 text-lg">
              Get started in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 text-white flex items-center justify-center mx-auto mb-6 text-xl font-bold">
                1
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Configure</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Define your evaluation in a simple YAML file. Specify app type, dataset, and quality thresholds.
              </p>
            </div>
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center mx-auto mb-6 text-xl font-bold">
                2
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Evaluate</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Run in CI/CD with <code>company-eval ci-run</code>. LLM judges assess quality automatically.
              </p>
            </div>
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 text-white flex items-center justify-center mx-auto mb-6 text-xl font-bold">
                3
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Monitor</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                View results in the dashboard. Track trends, analyze failures, and ship with confidence.
              </p>
            </div>
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
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center">
                <span className="text-white font-bold text-sm">CE</span>
              </div>
              <span className="font-semibold text-white">Company Eval</span>
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
