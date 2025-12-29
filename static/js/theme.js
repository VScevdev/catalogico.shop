document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("theme-toggle");
    const root = document.documentElement;

    const savedTheme = localStorage.getItem("theme");

    if (savedTheme) {
        root.setAttribute("data-theme", savedTheme);
        updateIcon(savedTheme);
    }

    toggleBtn.addEventListener("click", () => {
        const currentTheme = root.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";

        root.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
        updateIcon(newTheme);
    });

    function updateIcon(theme) {
        toggleBtn.textContent = theme === "dark" ? "☀️" : "🌙";
    }
});
