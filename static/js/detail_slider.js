document.addEventListener("DOMContentLoaded", () => {
  const viewer = document.getElementById("galleryViewer");
  if (!viewer) return;

  const track = viewer.querySelector(".slides-track");
  const slides = Array.from(track.children);
  const thumbs = Array.from(document.querySelectorAll(".thumb"));
  const dots = Array.from(viewer.querySelectorAll(".dot"));
  const prevBtn = viewer.querySelector(".nav-arrow.prev");
  const nextBtn = viewer.querySelector(".nav-arrow.next");

  let current = 0;
  let startX = 0;
  let currentTranslate = 0;
  let isDragging = false;

  function updateUI(index) {
    current = Math.max(0, Math.min(index, slides.length - 1));
    currentTranslate = -current * viewer.clientWidth;
    track.style.transform = `translateX(${currentTranslate}px)`;

    thumbs.forEach(t => t.classList.remove("active"));
    dots.forEach(d => d.classList.remove("active"));

    thumbs[current]?.classList.add("active");
    dots[current]?.classList.add("active");
  }

  /* Thumbs click */
  thumbs.forEach(t => {
    t.addEventListener("click", () => {
      updateUI(parseInt(t.dataset.index));
    });
  });

  /* Arrows */
  prevBtn?.addEventListener("click", () => updateUI(current - 1));
  nextBtn?.addEventListener("click", () => updateUI(current + 1));

  /* Swipe */
  viewer.addEventListener("touchstart", e => {
    startX = e.touches[0].clientX;
    isDragging = true;
    track.style.transition = "none";
  });

  viewer.addEventListener("touchmove", e => {
    if (!isDragging) return;
    const diff = e.touches[0].clientX - startX;
    track.style.transform = `translateX(${currentTranslate + diff}px)`;
  });

  viewer.addEventListener("touchend", e => {
    isDragging = false;
    track.style.transition = "transform 0.35s ease";

    const diff = e.changedTouches[0].clientX - startX;
    if (Math.abs(diff) > 60) {
      updateUI(diff < 0 ? current + 1 : current - 1);
    } else {
      updateUI(current);
    }
  });

  /* Init */
  updateUI(0);
});