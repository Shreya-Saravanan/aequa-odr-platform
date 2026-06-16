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
          DEFAULT: '#1e40af',
          light: '#2563eb',
          50: '#eff6ff',
          100: '#dbeafe',
        },
        gold: {
          DEFAULT: '#d97706',
          light: '#f59e0b',
        },
        surface: '#f8faff',
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
        navy: '0 4px 14px rgba(30,64,175,0.3)',
        'navy-lg': '0 8px 28px rgba(30,64,175,0.42)',
      },
      backgroundImage: {
        'page-gradient': 'linear-gradient(145deg,#eff6ff 0%,#dbeafe 40%,#fef9ee 100%)',
        'landing-gradient': 'linear-gradient(145deg,#bfdbfe 0%,#93c5fd 30%,#fde68a 100%)',
        'navy-gradient': 'linear-gradient(135deg,#1e40af 0%,#2563eb 100%)',
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
