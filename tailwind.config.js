/* Config Tailwind per la build di produzione.
   Sostituisce il CDN: stessi token del prototipo (ex brand.js). */
const SERIF = ['"Cormorant Garamond"', '"Iowan Old Style"', '"Palatino Linotype"', 'Georgia', 'serif'];
const SANS = ['"DM Sans"', 'Inter', '"Helvetica Neue"', 'Arial', 'sans-serif'];

module.exports = {
  content: ["./src/**/*.{njk,md,html}", "./src/assets/brand.js"],
  safelist: ["bg-[#A55C41]", "bg-[#B8735A]", "rounded-[50%]", "rotate-180", "flex"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        base: "#FAF8F4", alt: "#F2ECE3", deep: "#E8DED1",
        background: "#FAF8F4", surface: "#FAF8F4", "surface-bright": "#FAF8F4", cream: "#FAF8F4",
        sand: "#E8DED1", "olive-dark": "#4A5A3E", "ocean-deep": "#3D5A5E",
        primary: "#516442", secondary: "#8b4e38", tertiary: "#715b3e",
        terracotta: "#B8735A", earth: "#8B7355", charcoal: "#2A2A28",
        "warm-gray": "#A09A90", blush: "#E8D5C8", "light-border": "#E5E0D8",
        "on-primary": "#ffffff", "on-secondary": "#ffffff", "on-tertiary": "#ffffff",
        "on-surface": "#1b1c1a", "on-background": "#1b1c1a", "on-surface-variant": "#44483f",
        "on-primary-container": "#243518", "on-tertiary-container": "#3e2d14",
        "primary-container": "#8a9e78", "primary-fixed": "#d4e9bf", "primary-fixed-dim": "#b8cda4",
        "surface-container": "#f0edea", "surface-container-low": "#f6f3f0",
        "surface-container-lowest": "#ffffff", "surface-container-high": "#eae8e4",
        "surface-container-highest": "#e5e2df", "surface-variant": "#e5e2df",
        warning: "#D4A574", success: "#7CAA59", info: "#5B8A9A", error: "#C2685C"
      },
      borderRadius: { DEFAULT: "0.125rem", lg: "0.25rem", xl: "0.5rem", full: "0.75rem" },
      spacing: {
        base: "4px", xs: "8px", sm: "16px", md: "24px", lg: "40px", xl: "64px",
        "container-max": "1440px"
      },
      fontFamily: {
        display: SERIF, h1: SERIF, h2: SERIF, h3: SERIF, h4: SERIF, quote: SERIF,
        body: SANS, label: SANS
      },
      fontSize: {
        display: ["52px", { lineHeight: "1.05", letterSpacing: "-0.5px", fontWeight: "400" }],
        h1: ["44px", { lineHeight: "1.15", letterSpacing: "-0.3px", fontWeight: "400" }],
        h2: ["34px", { lineHeight: "1.2", fontWeight: "400" }],
        h3: ["26px", { lineHeight: "1.3", fontWeight: "400" }],
        h4: ["21px", { lineHeight: "1.35", fontWeight: "500" }],
        quote: ["26px", { lineHeight: "1.45", fontWeight: "400" }],
        "body-lg": ["18px", { lineHeight: "1.7", letterSpacing: "0.2px", fontWeight: "300" }],
        body: ["16px", { lineHeight: "1.8", letterSpacing: "0.3px", fontWeight: "300" }],
        "body-sm": ["14px", { lineHeight: "1.6", fontWeight: "400" }],
        caption: ["12px", { lineHeight: "1.5", fontWeight: "400" }],
        label: ["11px", { lineHeight: "1", letterSpacing: "0.16em", fontWeight: "600" }],
        micro: ["9px", { lineHeight: "1", letterSpacing: "0.16em", fontWeight: "600" }]
      }
    }
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/container-queries")]
};
