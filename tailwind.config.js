module.exports = {
    content: ["./templates/**/*.html", "./static/**/*.js"],
    darkMode: "class",
    theme: {
        container: {
            center: true,
            padding: "1rem",
        },
        extend: {
            fontFamily: {
                inter: ["Inter", "sans-serif"],
            },
            colors: {
                transparent: "transparent",
                current: "currentColor",
                white: "#ffffff",
                primary: "#267DFF",
                purple: "#7B6AFE",
                pink: "#FF51A4",
                orange: "#FF7C51",
                success: "#00D085",
                warning: "#FFC41F",
                danger: "#FF3232",
                dark: "#050C17",
                gray: "#7780A1",
                lightgray: "#5A6383",
            },
        },
    },
    plugins: [
        require("@tailwindcss/forms")({
            strategy: "base",
        }),
        require("tailwind-scrollbar"),
    ],
};
