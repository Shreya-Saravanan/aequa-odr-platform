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
          DEFAULT: '#1a3fa0',
          light: '#2454cc',
          50: '#eef2ff',
          100: '#dde8ff',
        },
        gold: {
          DEFAULT: '#c9900a',
          light: '#e8aa20',
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
        navy: '0 4px 14px rgba(26,63,160,0.28)',
        'navy-lg': '0 8px 28px rgba(26,63,160,0.38)',
      },
      backgroundImage: {
        'page-gradient': 'linear-gradient(145deg,#eef2ff 0%,#e8f0ff 55%,#fdf8ee 100%)',
        'landing-gradient': 'linear-gradient(145deg,#dce8ff 0%,#c8d8ff 40%,#faecd0 100%)',
        'navy-gradient': 'linear-gradient(135deg,#1a3fa0 0%,#2454cc 100%)',
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
