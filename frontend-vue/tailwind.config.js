/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#0284c7',
        'primary-hover': '#0369a1',
        'text-dark': '#0f172a',
        'text-muted': '#64748b',
        'border-color': '#e2e8f0',
        'bg-page': '#f8fafc',
        'color-libre': '#10b981',
        'color-ocupado': '#ef4444',
        'color-reservado': '#f59e0b',
        'bg-dark': '#0b0f19',
        'glass-bg': 'rgba(30,41,59,0.65)',
        'glass-border': 'rgba(255,255,255,0.1)'
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
