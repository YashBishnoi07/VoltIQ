/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: "#00F0FF",
          lime: "#39FF14",
          violet: "#9D00FF",
          blue: "#0070F3",
        },
        bg: {
          dark: "#080B10",
          card: "#0E131F",
          border: "#1E293B",
        },
      },
      fontFamily: {
        orbitron: ["Orbitron", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
