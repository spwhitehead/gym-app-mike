import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/utils/**/*.{js,ts,jsx,tsx,mdx}", "./src/components/**/*.{js,ts,jsx,tsx,mdx}", "./src/app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "gradient-to-br": "linear-gradient(to bottom right, var(--tw-gradient-stops))",
      },
      textShadow: {
        default: "0 1px 3px rgba(0, 0, 0, 0.9)",
        md: "0 3px 6px rgba(0, 0, 0, 0.5)",
        lg: "0 5px 10px rgba(0, 0, 0, 0.5)",
      },
      colors: {
        teal: {
          500: "#38b2ac",
        },
        green: {
          400: "#48bb78",
        },
        gray: {
          200: "#edf2f7",
        },
      },
    },
  },
  plugins: [
    function ({ addUtilities }: { addUtilities: any }) {
      const newUtilities = {
        ".text-shadow": {
          textShadow: "0 1px 3px rgba(0, 0, 0, 0.9)",
        },
        ".text-shadow-md": {
          textShadow: "0 3px 6px rgba(0, 0, 0, 0.5)",
        },
        ".text-shadow-lg": {
          textShadow: "0 5px 10px rgba(0, 0, 0, 0.5)",
        },
        ".text-shadow-none": {
          textShadow: "none",
        },
      };
      addUtilities(newUtilities);
    },
  ],
};

export default config;
