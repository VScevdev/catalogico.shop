(function () {
  const manager = document.getElementById("media-manager");
  if (!manager) return;

  const uploadUrl = manager.dataset.uploadUrl;
  const csrfToken = manager.dataset.csrfToken;
  const input = document.getElementById("mediaInput");
  const addBtn = document.getElementById("add-media-btn");
  const mediaList = document.getElementById("media-list");

  addBtn.addEventListener("click", () => input.click());

  input.addEventListener("change", (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!input.files.length) return;
    uploadFiles(input.files);
    input.value = "";
  });

  function uploadFiles(files) {
    const formData = new FormData();

    for (const file of files) {
      formData.append("files", file);
      renderPreview(file);
    }

    fetch(uploadUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      body: formData,
    }).catch(() => {
      alert("Error subiendo archivos");
    });
  }

  function renderPreview(file) {
    const item = document.createElement("div");
    item.className = "media-preview";
    item.textContent = file.name;
    mediaList.appendChild(item);
  }
})();