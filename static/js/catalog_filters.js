document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".filters-toggle");
  const closeBtn = document.querySelector(".filters-close");
  const sidebar = document.querySelector(".catalog-sidebar");
  const overlay = document.querySelector(".catalog-overlay");

  if (!toggle || !sidebar || !overlay) return;

  function openSidebar() {
    sidebar.classList.add("is-open");
    overlay.classList.add("is-active");
    toggle.setAttribute("aria-expanded", "true");
  }

  function closeSidebar() {
    sidebar.classList.remove("is-open");
    overlay.classList.remove("is-active");
    toggle.setAttribute("aria-expanded", "false");
  }

  toggle.addEventListener("click", openSidebar);
  overlay.addEventListener("click", closeSidebar);

  if (closeBtn) {
    closeBtn.addEventListener("click", closeSidebar);
  }
});