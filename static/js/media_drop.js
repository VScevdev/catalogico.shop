(function () {
  const manager = document.getElementById("media-manager");
  if (!manager) return;

  const uploadUrl = manager.dataset.uploadUrl;
  const reorderUrl = manager.dataset.reorderUrl;
  const deleteUrlTemplate = manager.dataset.deleteUrl;
  const csrfToken = manager.dataset.csrfToken;
  const input = document.getElementById("mediaInput");
  const addBtn = document.getElementById("add-media-btn");
  const mediaList = document.getElementById("media-list");

  // Read existing media data from the script tag
  const existingMediaScript = document.getElementById('existingMediaJson');
  let existingMedia = [];
  if (existingMediaScript) {
    try {
      existingMedia = JSON.parse(existingMediaScript.textContent);
    } catch (e) {
      console.error("[media_drop] Failed to parse existing media JSON:", e);
    }
  }

  // Render existing media previews on load
  existingMedia.forEach(media => {
    renderPreview(media, "Existente", "ok");
  });

  if (!uploadUrl) {
    console.error("[media_drop] Missing data-upload-url on #media-manager");
    return;
  }

  if (!csrfToken) {
    console.warn("[media_drop] Missing CSRF token; uploads may fail with 403");
  }

  addBtn.addEventListener("click", () => input.click());

  input.addEventListener("change", (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!input.files.length) return;
    uploadFiles(input.files);
    input.value = "";
  });

  async function uploadFiles(files) {
    const formData = new FormData();
    const previewNodes = [];
    const cancelledIndices = new Set();

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      formData.append("files", file);
      const node = renderPreview(file, "Subiendo...", "uploading", i);
      node._cancelUpload = function () {
        cancelledIndices.add(i);
        node.remove();
      };
      previewNodes.push(node);
    }

    setUploading(true);

    try {
      const response = await fetch(uploadUrl, {
        method: "POST",
        headers: csrfToken ? { "X-CSRFToken": csrfToken } : undefined,
        body: formData,
        credentials: "same-origin",
      });

      if (!response.ok) {
        const text = await response.text().catch(() => "");
        const snippet = text ? `\n\n${text.slice(0, 400)}` : "";
        throw new Error(`HTTP ${response.status} ${response.statusText}${snippet}`);
      }

      const data = await response.json().catch(() => ({}));
      const ids = data.ids || [];

      for (const i of cancelledIndices) {
        if (ids[i] != null) {
          try {
            await fetch(getDeleteUrl(ids[i]), {
              method: "POST",
              headers: { "X-CSRFToken": csrfToken || "" },
              credentials: "same-origin",
            });
          } catch (e) {
            console.warn("[media_drop] Delete cancelled media failed:", e);
          }
        }
      }

      previewNodes.forEach((node) => setPreviewStatus(node, "Subido", "ok"));

      for (let i = 0; i < previewNodes.length; i++) {
        const node = previewNodes[i];
        if (!node.isConnected || cancelledIndices.has(i)) continue;
        const id = ids[i];
        if (id != null) {
          node.dataset.mediaId = String(id);
          node.draggable = true;
          node.classList.add("media-preview--draggable");
          const deleteBtn = node.querySelector(".media-preview-delete");
          if (deleteBtn) {
            deleteBtn._boundMediaId = id;
            deleteBtn.onclick = makeDeleteHandler(node, id);
          }
        }
      }
    } catch (err) {
      console.error("[media_drop] Upload failed:", err);
      previewNodes.forEach((node) => {
        if (node.isConnected) setPreviewStatus(node, "Error", "error");
      });
      alert(
        "Error subiendo archivos.\n\n" +
          "Tip: si es 403 suele ser CSRF_TRUSTED_ORIGINS/CSRF.\n" +
          "Si es 404, revisá que el producto exista y que la URL sea correcta."
      );
    } finally {
      setUploading(false);
    }
  }

  function makeDeleteHandler(item, mediaId) {
    return async function () {
      if (!confirm("¿Eliminar este archivo de la galería?")) return;
      const url = getDeleteUrl(mediaId);
      if (!url) return;
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: { "X-CSRFToken": csrfToken || "" },
          credentials: "same-origin",
        });
        if (res.ok) {
          item.remove();
        } else {
          alert("No se pudo eliminar.");
        }
      } catch (err) {
        console.error(err);
        alert("Error al eliminar.");
      }
    };
  }

  function setUploading(isUploading) {
    addBtn.disabled = isUploading;
    input.disabled = isUploading;
    manager.dataset.uploading = isUploading ? "1" : "0";
  }

  function setPreviewStatus(node, message, variant) {
    node.dataset.status = variant || "";
    const statusEl = node.querySelector(".media-preview-status");
    if (statusEl) statusEl.textContent = message;
  }

  function getDeleteUrl(mediaId) {
    if (!deleteUrlTemplate) return null;
    return deleteUrlTemplate.replace(/\/0\/eliminar\/?$/, "/" + mediaId + "/eliminar/");
  }

  function getOrderedIds() {
    const items = mediaList.querySelectorAll(".media-preview[data-media-id]");
    return Array.from(items).map(el => parseInt(el.dataset.mediaId, 10));
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
    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(text || "Error al reordenar");
    }
  }

  function renderPreview(mediaItem, statusText, statusVariant, uploadIndex) {
    const item = document.createElement("div");
    item.className = "media-preview";
    item.dataset.status = statusVariant || "";

    const isExisting = mediaItem && typeof mediaItem === "object" && "id" in mediaItem;
    const isUploadingFile = mediaItem instanceof File && uploadIndex !== undefined;

    if (isExisting) {
      item.dataset.mediaId = mediaItem.id;
      item.classList.add("media-preview--draggable");
    }
    if (isUploadingFile) {
      item.dataset.uploadIndex = String(uploadIndex);
    }

    const thumbnailContainer = document.createElement("div");
    thumbnailContainer.className = "media-preview-thumbnail";

    let thumbnailElement;
    let fileName = "";
    let mediaType = "";

    if (mediaItem instanceof File) {
      fileName = mediaItem.name;
      if (mediaItem.type.startsWith("image/")) {
        mediaType = "image";
        thumbnailElement = document.createElement("img");
        thumbnailElement.src = URL.createObjectURL(mediaItem);
      } else if (mediaItem.type.startsWith("video/")) {
        mediaType = "video";
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "▶";
      } else {
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "?";
      }
    } else if (mediaItem && typeof mediaItem === "object") {
      fileName = mediaItem.file_name || "";
      mediaType = mediaItem.media_type || "";
      if (mediaItem.media_type === "image") {
        thumbnailElement = document.createElement("img");
        thumbnailElement.src = mediaItem.file_url || "";
      } else if (mediaItem.media_type === "video") {
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "▶";
      } else {
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "?";
      }
    }

    if (thumbnailElement) {
      thumbnailContainer.appendChild(thumbnailElement);
    }

    const infoContainer = document.createElement("div");
    infoContainer.className = "media-preview-info";

    const nameEl = document.createElement("div");
    nameEl.className = "media-preview-name";
    nameEl.textContent = fileName;

    const statusEl = document.createElement("div");
    statusEl.className = "media-preview-status";
    statusEl.textContent = statusText || "";

    infoContainer.appendChild(nameEl);
    infoContainer.appendChild(statusEl);

    if (isExisting) {
      const dragHandle = document.createElement("span");
      dragHandle.className = "media-preview-drag-handle";
      dragHandle.setAttribute("aria-hidden", "true");
      dragHandle.draggable = true;
      dragHandle.title = "Arrastrar para reordenar";
      dragHandle.textContent = "⋮⋮";
      item.appendChild(dragHandle);
    }
    item.appendChild(thumbnailContainer);
    item.appendChild(infoContainer);

    if (isExisting && deleteUrlTemplate) {
      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "media-preview-delete owner-btn owner-btn--danger owner-btn--small";
      deleteBtn.textContent = "Eliminar";
      deleteBtn.setAttribute("aria-label", "Eliminar este archivo");
      deleteBtn.addEventListener("click", makeDeleteHandler(item, mediaItem.id));
      item.appendChild(deleteBtn);
    }

    if (isUploadingFile && deleteUrlTemplate) {
      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "media-preview-delete owner-btn owner-btn--danger owner-btn--small";
      deleteBtn.textContent = "Eliminar";
      deleteBtn.setAttribute("aria-label", "Quitar de la subida");
      deleteBtn.addEventListener("click", () => {
        if (item._cancelUpload) item._cancelUpload();
      });
      item.appendChild(deleteBtn);
    }

    mediaList.appendChild(item);
    return item;
  }

  // ---- Drag and drop reorder ----
  let draggedEl = null;

  mediaList.addEventListener("dragstart", (e) => {
    if (!e.target.closest(".media-preview-drag-handle")) return;
    const item = e.target.closest(".media-preview[data-media-id]");
    if (!item) return;
    draggedEl = item;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", item.dataset.mediaId);
    item.classList.add("media-preview--dragging");
  });

  mediaList.addEventListener("dragend", (e) => {
    if (draggedEl) {
      draggedEl.classList.remove("media-preview--dragging");
      draggedEl = null;
    }
  });

  mediaList.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    const target = e.target.closest(".media-preview[data-media-id]");
    if (target && target !== draggedEl) {
      target.classList.add("media-preview--drag-over");
    }
  });

  mediaList.addEventListener("dragleave", (e) => {
    const target = e.target.closest(".media-preview[data-media-id]");
    if (target) target.classList.remove("media-preview--drag-over");
  });

  mediaList.addEventListener("drop", async (e) => {
    e.preventDefault();
    const target = e.target.closest(".media-preview[data-media-id]");
    mediaList.querySelectorAll(".media-preview--drag-over").forEach(el => el.classList.remove("media-preview--drag-over"));
    if (!draggedEl || !target || draggedEl === target) return;
    const allWithId = Array.from(mediaList.querySelectorAll(".media-preview[data-media-id]"));
    const idxDrag = allWithId.indexOf(draggedEl);
    const idxTarget = allWithId.indexOf(target);
    if (idxDrag === -1 || idxTarget === -1) return;
    if (idxDrag < idxTarget) {
      target.parentNode.insertBefore(draggedEl, target.nextSibling);
    } else {
      target.parentNode.insertBefore(draggedEl, target);
    }
    const orderIds = getOrderedIds();
    try {
      await callReorder(orderIds);
    } catch (err) {
      console.error("[media_drop] Reorder failed:", err);
      alert("Error al reordenar. Recargá la página.");
    }
  });
})();
