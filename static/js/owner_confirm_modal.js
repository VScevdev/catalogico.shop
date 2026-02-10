(function () {
  function createModal() {
    var existing = document.getElementById("owner-confirm-overlay");
    if (existing) return existing;

    var overlay = document.createElement("div");
    overlay.id = "owner-confirm-overlay";
    overlay.style.position = "fixed";
    overlay.style.inset = "0";
    overlay.style.background = "rgba(0,0,0,0.45)";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = "1000";
    overlay.style.visibility = "hidden";
    overlay.style.opacity = "0";
    overlay.style.transition = "opacity 0.15s ease, visibility 0.15s ease";

    var dialog = document.createElement("div");
    dialog.style.maxWidth = "420px";
    dialog.style.width = "90%";
    dialog.style.background = "var(--color-surface, #fff)";
    dialog.style.color = "var(--color-text, #111)";
    dialog.style.borderRadius = "12px";
    dialog.style.border = "1px solid var(--color-border, #e0e0e0)";
    dialog.style.boxShadow = "0 8px 24px rgba(0,0,0,0.15)";
    dialog.style.padding = "16px 20px 20px 20px";
    dialog.style.display = "flex";
    dialog.style.flexDirection = "column";
    dialog.style.gap = "12px";

    var title = document.createElement("h2");
    title.textContent = "¿Qué querés hacer con este borrador?";
    title.style.margin = "0";
    title.style.fontSize = "16px";

    var text = document.createElement("p");
    text.textContent = "Podés guardar los cambios como borrador o cancelar y descartar este contenido.";
    text.style.margin = "0";
    text.style.fontSize = "14px";

    var actions = document.createElement("div");
    actions.style.display = "flex";
    actions.style.justifyContent = "flex-end";
    actions.style.gap = "8px";
    actions.style.marginTop = "12px";

    var cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.textContent = "Eliminar borrador";
    cancelBtn.style.padding = "8px 14px";
    cancelBtn.style.borderRadius = "999px";
    cancelBtn.style.border = "1px solid var(--color-border, #e0e0e0)";
    cancelBtn.style.background = "var(--color-surface, #fff)";
    cancelBtn.style.color = "var(--color-text, #111)";
    cancelBtn.style.cursor = "pointer";

    // Botón "Seguir editando"
    var continueBtn = document.createElement("button");
    continueBtn.type = "button";
    continueBtn.textContent = "Seguir editando";
    continueBtn.style.padding = "6px 12px";
    continueBtn.style.borderRadius = "999px";
    continueBtn.style.border = "none";
    continueBtn.style.background = "transparent";
    continueBtn.style.color = "var(--color-muted, #888)";
    continueBtn.style.fontSize = "13px";
    continueBtn.style.cursor = "pointer";
    continueBtn.style.alignSelf = "flex-start";
    continueBtn.style.marginRight = "auto";

    actions.appendChild(continueBtn);


    var saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.textContent = "Guardar borrador";
    saveBtn.style.padding = "8px 14px";
    saveBtn.style.borderRadius = "999px";
    saveBtn.style.border = "none";
    saveBtn.style.background = "var(--color-primary, #3483fa)";
    saveBtn.style.color = "#fff";
    saveBtn.style.cursor = "pointer";

    actions.appendChild(cancelBtn);
    actions.appendChild(saveBtn);
    dialog.appendChild(title);
    dialog.appendChild(text);
    dialog.appendChild(actions);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    return overlay;
  }

  function showModal(handler) {
    var overlay = createModal();
    var cancelBtn = overlay.querySelector("button:nth-child(1)");
    var saveBtn = overlay.querySelector("button:nth-child(2)");

    function hide() {
      overlay.style.opacity = "0";
      overlay.style.visibility = "hidden";
      overlay.removeEventListener("click", onOverlayClick);
      document.removeEventListener("keydown", onKeyDown);
      cancelBtn.onclick = null;
      saveBtn.onclick = null;
    }

    function onOverlayClick(e) {
      if (e.target === overlay) hide();
    }
    function onKeyDown(e) {
      if (e.key === "Escape") hide();
    }

    cancelBtn.onclick = function () {
      hide();
      if (handler && typeof handler.onCancel === "function") {
        handler.onCancel();
      }
    };
    saveBtn.onclick = function () {
      hide();
      if (handler && typeof handler.onSave === "function") {
        handler.onSave();
      }
    };

    overlay.addEventListener("click", onOverlayClick);
    document.addEventListener("keydown", onKeyDown);
    overlay.style.visibility = "visible";
    overlay.style.opacity = "1";
  }

  function setupProduct() {
    var form = document.getElementById("product-form");
    if (!form) return;

    var backLink = document.getElementById("product-back-link");
    var cancelBtn = document.getElementById("product-cancel-btn");
    var mediaManager = document.getElementById("media-manager");
    var cancelUrl = mediaManager && mediaManager.dataset.cancelUrl;
    var csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
    var backHref = backLink ? backLink.getAttribute("href") : null;

    function postCancel() {
      if (!cancelUrl) {
        if (backHref) {
          window.location.href = backHref;
        }
        return;
      }
      var f = document.createElement("form");
      f.method = "post";
      f.action = cancelUrl;
      if (csrfInput) {
        var token = document.createElement("input");
        token.type = "hidden";
        token.name = csrfInput.name;
        token.value = csrfInput.value;
        f.appendChild(token);
      }
      document.body.appendChild(f);
      f.submit();
    }

    function attach(el) {
      if (!el) return;
      el.addEventListener("click", function (e) {
        // Solo mostrar modal si hay cancelUrl (borrador nuevo)
        if (!cancelUrl) return;
        e.preventDefault();
        showModal({
          onSave: function () {
            form.submit();
          },
          onCancel: function () {
            postCancel();
          },
        });
      });
    }

    attach(backLink);
    attach(cancelBtn);
  }

  function setupCategory() {
    var form = document.getElementById("category-form");
    if (!form) return;

    var backLink = document.getElementById("category-back-link");
    var cancelLink = document.getElementById("category-cancel-link");
    var backHref = backLink ? backLink.getAttribute("href") : null;

    function attach(el) {
      if (!el) return;
      el.addEventListener("click", function (e) {
        e.preventDefault();
        showModal({
          onSave: function () {
            form.submit();
          },
          onCancel: function () {
            if (backHref) {
              window.location.href = backHref;
            }
          },
        });
      });
    }

    attach(backLink);
    attach(cancelLink);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      setupProduct();
      setupCategory();
    });
  } else {
    setupProduct();
    setupCategory();
  }
})();

