/**
 * Vista previa en tiempo real de colores y logo de tienda.
 * Actualiza dos paneles (modo claro y modo oscuro) al cambiar inputs.
 */
(function () {
  const VAR_MAP_LIGHT = {
    color_bg: "--color-bg",
    color_surface: "--color-surface",
    color_surface_secondary: "--color-surface-secondary",
    color_text: "--color-text",
    color_primary: "--color-primary",
    color_primary_hover: "--color-primary-hover",
    color_border: "--color-border",
    color_muted: "--color-muted",
  };

  const DEFAULT_COLORS = {
    color_bg: "#ffffff",
    color_surface: "#f8f8f8",
    color_surface_secondary: "#f0f0f0",
    color_text: "#111111",
    color_primary: "#3483fa",
    color_primary_hover: "#468cf6",
    color_border: "#e0e0e0",
    color_muted: "#6b6b6b",
    color_bg_dark: "#121212",
    color_surface_dark: "#1e1e1e",
    color_surface_secondary_dark: "#2a2a2a",
    color_text_dark: "#f5f5f5",
    color_primary_dark: "#3483fa",
    color_primary_hover_dark: "#468cf6",
    color_border_dark: "#333333",
    color_muted_dark: "#aaaaaa",
  };

  const VAR_MAP_DARK = {
    color_bg_dark: "--color-bg",
    color_surface_dark: "--color-surface",
    color_surface_secondary_dark: "--color-surface-secondary",
    color_text_dark: "--color-text",
    color_primary_dark: "--color-primary",
    color_primary_hover_dark: "--color-primary-hover",
    color_border_dark: "--color-border",
    color_muted_dark: "--color-muted",
  };

  function applyVarsToElement(element, varMap) {
    if (!element) return;
    const mockup = element.querySelector(".store-preview-mockup");
    if (!mockup) return;

    for (const [fieldName, cssVar] of Object.entries(varMap)) {
      const input = document.getElementById("id_" + fieldName);
      if (input && input.value) {
        mockup.style.setProperty(cssVar, input.value);
      }
    }
  }

  function updatePreviews() {
    const panelLight = document.getElementById("store-preview-light");
    const panelDark = document.getElementById("store-preview-dark");
    applyVarsToElement(panelLight, VAR_MAP_LIGHT);
    applyVarsToElement(panelDark, VAR_MAP_DARK);
  }

  function setLogoInPlaceholder(placeholder, src) {
    if (!placeholder) return;
    if (src) {
      let img = placeholder.querySelector("img");
      if (!img) {
        img = document.createElement("img");
        img.alt = "Logo";
        placeholder.appendChild(img);
      }
      img.src = src;
    } else {
      const img = placeholder.querySelector("img");
      if (img) img.remove();
    }
  }

  function updatePreviewLogo() {
    const logoInput = document.getElementById("id_logo");
    const mainPreview = document.getElementById("preview-logo");
    const lightPreview = document.querySelector('[data-preview-logo="light"]');
    const darkPreview = document.querySelector('[data-preview-logo="dark"]');

    const file = logoInput && logoInput.files && logoInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const url = e.target.result;
        setLogoInPlaceholder(mainPreview, url);
        setLogoInPlaceholder(lightPreview, url);
        setLogoInPlaceholder(darkPreview, url);
      };
      reader.readAsDataURL(file);
    } else {
      const initialUrl =
        typeof window.STORE_CONFIG_LOGO_URL !== "undefined" && window.STORE_CONFIG_LOGO_URL
          ? window.STORE_CONFIG_LOGO_URL
          : null;
      setLogoInPlaceholder(mainPreview, initialUrl);
      setLogoInPlaceholder(lightPreview, initialUrl);
      setLogoInPlaceholder(darkPreview, initialUrl);
    }
  }

  function init() {
    const form = document.querySelector(".store-config-form");
    if (!form) return;

    form.querySelectorAll('input[type="color"]').forEach(function (input) {
      input.addEventListener("input", updatePreviews);
      input.addEventListener("change", updatePreviews);
    });

    const logoInput = document.getElementById("id_logo");
    if (logoInput) {
      logoInput.addEventListener("change", updatePreviewLogo);
    }

    const restoreBtn = document.getElementById("store-config-restore-colors");
    if (restoreBtn) {
      restoreBtn.addEventListener("click", function () {
        for (const [fieldName, value] of Object.entries(DEFAULT_COLORS)) {
          const input = document.getElementById("id_" + fieldName);
          if (input && input.type === "color") {
            input.value = value;
          }
        }
        updatePreviews();
      });
    }

    updatePreviews();
    updatePreviewLogo();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
