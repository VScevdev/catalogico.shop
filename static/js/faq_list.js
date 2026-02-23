(function () {
  const list = document.getElementById("faq-list");
  if (!list) return;

  const reorderUrl = list.dataset.reorderUrl;
  const csrfToken = list.dataset.csrfToken;

  function getOrderedIds() {
    return Array.from(list.querySelectorAll(".help-faq-item[data-faq-id]"))
      .map((el) => parseInt(el.dataset.faqId, 10))
      .filter((n) => !Number.isNaN(n));
  }

  async function callReorder(orderIds) {
    if (!reorderUrl || !orderIds.length) return;
    const response = await fetch(reorderUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({ order: orderIds }),
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error("Reorder failed");
  }

  let draggedEl = null;

  list.addEventListener("dragstart", (e) => {
    if (!e.target.closest(".help-faq-drag-handle")) return;
    const item = e.target.closest(".help-faq-item[data-faq-id]");
    if (!item) return;
    draggedEl = item;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", item.dataset.faqId);
    item.classList.add("help-faq-item--dragging");
  });

  list.addEventListener("dragend", () => {
    if (draggedEl) {
      draggedEl.classList.remove("help-faq-item--dragging");
      draggedEl = null;
    }
  });

  list.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    const target = e.target.closest(".help-faq-item[data-faq-id]");
    if (target && target !== draggedEl) target.classList.add("help-faq-item--drag-over");
  });

  list.addEventListener("dragleave", (e) => {
    const target = e.target.closest(".help-faq-item[data-faq-id]");
    if (target) target.classList.remove("help-faq-item--drag-over");
  });

  list.addEventListener("drop", async (e) => {
    e.preventDefault();
    const target = e.target.closest(".help-faq-item[data-faq-id]");
    list.querySelectorAll(".help-faq-item--drag-over").forEach((el) => el.classList.remove("help-faq-item--drag-over"));
    if (!draggedEl || !target || draggedEl === target) return;
    const items = Array.from(list.querySelectorAll(".help-faq-item[data-faq-id]"));
    const idxDrag = items.indexOf(draggedEl);
    const idxTarget = items.indexOf(target);
    if (idxDrag === -1 || idxTarget === -1) return;
    if (idxDrag < idxTarget) {
      target.parentNode.insertBefore(draggedEl, target.nextSibling);
    } else {
      target.parentNode.insertBefore(draggedEl, target);
    }
    try {
      await callReorder(getOrderedIds());
    } catch (err) {
      console.error("[faq_list] Reorder failed:", err);
      alert("Error al reordenar. Recargá la página.");
    }
  });

  list.addEventListener("submit", (e) => {
    const form = e.target.closest("form.faq-delete-form");
    if (!form) return;
    e.preventDefault();
    if (!confirm("¿Eliminar esta pregunta frecuente?")) return;
    form.submit();
  });
})();
