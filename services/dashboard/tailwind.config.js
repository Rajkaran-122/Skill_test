/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ["class"],
	content: [
		"./src/**/*.{js,jsx,ts,tsx}",
		"./public/index.html"
	],
	theme: {
		extend: {
			fontFamily: {
				sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
				mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
				display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
			},
			fontSize: {
				'xs': '0.75rem',
				'sm': '0.875rem',
				'base': '1rem',
				'lg': '1.125rem',
				'xl': '1.25rem',
				'2xl': '1.5rem',
				'3xl': '1.875rem',
				'4xl': '2.25rem',
				'5xl': '3rem',
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			colors: {
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))',
					blue: '#3B82F6',
					purple: '#8B5CF6',
					cyan: '#06B6D4',
					green: '#10B981',
					yellow: '#F59E0B',
					red: '#EF4444',
					pink: '#EC4899',
					orange: '#F97316',
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				chart: {
					'1': 'hsl(var(--chart-1))',
					'2': 'hsl(var(--chart-2))',
					'3': 'hsl(var(--chart-3))',
					'4': 'hsl(var(--chart-4))',
					'5': 'hsl(var(--chart-5))'
				},
				// Custom theme colors for $50M Enterprise SaaS
				dark: {
					'bg-primary': '#050816',
					'bg-secondary': '#0B1220',
					'bg-tertiary': '#0F172A',
					'bg-hover': '#1E293B',
					'bg-active': '#334155',
				},
				'border-subtle': '#1E1E2A',
				'border-default': '#2A2A3A',
				'border-strong': '#3A3A4A',
				'text-primary': '#F8FAFC',
				'text-secondary': '#94A3B8',
				'text-tertiary': '#64748B',
			},
			boxShadow: {
				'sm': '0 1px 2px rgba(0, 0, 0, 0.4)',
				'md': '0 4px 12px rgba(0, 0, 0, 0.5)',
				'lg': '0 8px 24px rgba(0, 0, 0, 0.6)',
				'glow': '0 0 40px rgba(59, 130, 246, 0.15)',
				'glow-green': '0 0 40px rgba(16, 185, 129, 0.15)',
				'glow-red': '0 0 40px rgba(239, 68, 68, 0.15)',
			},
			keyframes: {
				'accordion-down': {
					from: { height: '0' },
					to: { height: 'var(--radix-accordion-content-height)' }
				},
				'accordion-up': {
					from: { height: 'var(--radix-accordion-content-height)' },
					to: { height: '0' }
				},
				'shimmer': {
					'0%': { backgroundPosition: '-200% 0' },
					'100%': { backgroundPosition: '200% 0' }
				},
				'pulse-glow': {
					'0%, 100%': { boxShadow: '0 0 0 0 rgba(59, 130, 246, 0.4)' },
					'50%': { boxShadow: '0 0 0 8px rgba(59, 130, 246, 0)' }
				},
				'card-enter': {
					from: { opacity: '0', transform: 'translateY(20px)' },
					to: { opacity: '1', transform: 'translateY(0)' }
				},
				'fade-in': {
					from: { opacity: '0' },
					to: { opacity: '1' }
				},
				'slide-in-right': {
					from: { transform: 'translateX(100%)' },
					to: { transform: 'translateX(0)' }
				},
				'slide-in-left': {
					from: { transform: 'translateX(-100%)' },
					to: { transform: 'translateX(0)' }
				},
				'float': {
					'0%, 100%': { transform: 'translateY(0)' },
					'50%': { transform: 'translateY(-20px)' },
				},
				'data-stream': {
					'0%': { transform: 'translateX(-100%)' },
					'100%': { transform: 'translateX(100%)' },
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'shimmer': 'shimmer 1.5s infinite',
				'pulse-glow': 'pulse-glow 1.5s infinite',
				'card-enter': 'card-enter 0.5s ease-out forwards',
				'fade-in': 'fade-in 0.3s ease-out',
				'slide-in-right': 'slide-in-right 0.3s ease-out',
				'slide-in-left': 'slide-in-left 0.3s ease-out',
				'float': 'float 6s ease-in-out infinite',
				'float-delayed': 'float 6s ease-in-out 3s infinite',
				'data-stream': 'data-stream 2s linear infinite',
			},
			transitionProperty: {
				'height': 'height',
				'spacing': 'margin, padding',
			},
			backdropBlur: {
				'xs': '2px',
			},
		}
	},
	plugins: [require("tailwindcss-animate")],
};
