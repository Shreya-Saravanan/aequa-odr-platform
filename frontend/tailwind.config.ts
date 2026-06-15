import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './context/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#1a2b5e',
          light: '#253580',
          50: '#eef0ff',
          100: '#dde0ff',
        },
        gold: {
          DEFAULT: '#c9a227',
          light: '#e6bb3a',
        },
        surface: '#fafafe',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        xl: '12px',
        '2xl': '16px',
        '3xl': '20px',
      },
      boxShadow: {
        card: '0 2px 16px rgba(80,80,200,0.07)',
        'card-hover': '0 6px 24px rgba(80,80,200,0.13)',
        navy: '0 4px 14px rgba(26,43,94,0.28)',
        'navy-lg': '0 8px 28px rgba(26,43,94,0.35)',
      },
      backgroundImage: {
        'page-gradient': 'linear-gradient(145deg,#eef0fa 0%,#f4f0ff 55%,#fef4f8 100%)',
        'landing-gradient': 'linear-gradient(145deg,#e8eaf6 0%,#ede7f6 40%,#fce4ec 100%)',
        'navy-gradient': 'linear-gradient(135deg,#1a2b5e 0%,#253580 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.25s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
export default config
