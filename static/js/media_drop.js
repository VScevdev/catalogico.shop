(function () {
  const manager = document.getElementById("media-manager");
  if (!manager) return;

  const uploadUrl = manager.dataset.uploadUrl;
  const csrfToken = manager.dataset.csrfToken;
  const input = document.getElementById("mediaInput");
  const addBtn = document.getElementById("add-media-btn");
  const mediaList = document.getElementById("media-list");

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

  function renderPreview(file, statusText) {
    const item = document.createElement("div");
    item.className = "media-preview";

    const nameEl = document.createElement("div");
    nameEl.className = "media-preview-name";
    nameEl.textContent = file.name;

    const statusEl = document.createElement("div");
    statusEl.className = "media-preview-status";
    statusEl.textContent = statusText || "";

    item.appendChild(nameEl);
    item.appendChild(statusEl);

    mediaList.appendChild(item);
    return item;
  }
})();