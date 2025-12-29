/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      colors: {
        // Unkey-inspired color palette
        background: '#000000',
        foreground: '#ffffff',
        muted: {
          DEFAULT: '#18181b',
          foreground: '#a1a1aa',
        },
        accent: {
          DEFAULT: '#3b82f6',
          foreground: '#ffffff',
        },
        border: 'rgba(255, 255, 255, 0.1)',
        card: {
          DEFAULT: 'rgba(255, 255, 255, 0.02)',
          hover: 'rgba(255, 255, 255, 0.05)',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-glow': 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.3), transparent)',
        'grid-pattern': 'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid': '64px 64px',
      },
      animation: {
        'glow': 'glow 4s ease-in-out infinite alternate',
        'glow-slow': 'glowSlow 8s ease-in-out infinite',
        'glow-pulse': 'glowPulse 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { opacity: 0.5 },
          '100%': { opacity: 1 },
        },
        glowSlow: {
          '0%, 100%': { opacity: 0.4, transform: 'scale(1)' },
          '50%': { opacity: 0.7, transform: 'scale(1.05)' },
        },
        glowPulse: {
          '0%, 100%': { opacity: 0.3 },
          '50%': { opacity: 0.6 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        slideUp: {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
