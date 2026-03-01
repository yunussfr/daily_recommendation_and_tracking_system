/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class', // Karanlık/aydınlık tema geçişi için eklendi
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                dark: "#0F172A",
                darker: "#0B1120", // Arka plan için daha koyu bir ton
                primary: "#8B5CF6", // Gelişim sitesindeki mor tonu
                primaryHover: "#7C3AED",
            },
            animation: {
                'bounce-soft': 'bounceSoft 2s infinite',
            },
            keyframes: {
                bounceSoft: {
                    '0%, 100%': { transform: 'translateY(-5%)' },
                    '50%': { transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
