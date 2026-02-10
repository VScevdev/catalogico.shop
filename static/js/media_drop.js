(function () {
  const manager = document.getElementById("media-manager");
  if (!manager) return;

  const uploadUrl = manager.dataset.uploadUrl;
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

    for (const file of files) {
      formData.append("files", file);
      previewNodes.push(renderPreview(file, "Subiendo..."));
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

      previewNodes.forEach((node) => setPreviewStatus(node, "Subido", "ok"));
    } catch (err) {
      console.error("[media_drop] Upload failed:", err);
      previewNodes.forEach((node) => setPreviewStatus(node, "Error", "error"));
      alert(
        "Error subiendo archivos.\n\n" +
          "Tip: si es 403 suele ser CSRF_TRUSTED_ORIGINS/CSRF.\n" +
          "Si es 404, revisá que el producto exista y que la URL sea correcta."
      );
    } finally {
      setUploading(false);
    }
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

  function renderPreview(mediaItem, statusText, statusVariant) {
    const item = document.createElement("div");
    item.className = "media-preview";
    item.dataset.status = statusVariant || "";

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
        thumbnailElement.textContent = "▶"; // Placeholder for video
      } else {
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "?"; // Unknown type
      }
    } else { // Existing media object
      fileName = mediaItem.file_name;
      mediaType = mediaItem.media_type;
      if (mediaItem.media_type === "image") {
        thumbnailElement = document.createElement("img");
        thumbnailElement.src = mediaItem.file_url;
      } else if (mediaItem.media_type === "video") {
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "▶"; // Placeholder for video
      } else {
        thumbnailElement = document.createElement("div");
        thumbnailElement.textContent = "?"; // Unknown type
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

    item.appendChild(thumbnailContainer);
    item.appendChild(infoContainer);

    mediaList.appendChild(item);
    return item;
  }
})();