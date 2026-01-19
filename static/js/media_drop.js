const dropzone = document.getElementById("media-dropzone");
const input = document.getElementById("mediaInput");

const uploadUrl = dropzone.dataset.uploadUrl;
const csrfToken = dropzone.dataset.csrfToken;

dropzone.addEventListener("click", () => input.click());

dropzone.addEventListener("dragover", e => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", e => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  handleFiles(e.dataTransfer.files);
});

input.addEventListener("change", () => {
  handleFiles(input.files);
});

function handleFiles(files) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  fetch(uploadUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken
    },
    body: formData
  }).then(() => location.reload());
}