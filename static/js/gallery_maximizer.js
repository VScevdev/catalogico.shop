/**
 * Lightbox / maximizer para galería de producto.
 * Click en .thumb o .slide abre overlay con imagen/video en grande, contador y flechas.
 */
(function () {
  const scriptEl = document.getElementById("mediaItemsJson");
  if (!scriptEl) return;

  let mediaItems = [];
  try {
    mediaItems = JSON.parse(scriptEl.textContent || "[]");
  } catch (e) {
    return;
  }

  if (!mediaItems.length) return;

  const viewer = document.getElementById("galleryViewer");
  if (!viewer) return;

  let overlay = null;
  let currentIndex = 0;

  function createOverlay() {
    const wrap = document.createElement("div");
    wrap.id = "gallery-maximizer-overlay";
    wrap.className = "gallery-maximizer-overlay";
    wrap.setAttribute("aria-hidden", "true");

    const backdrop = document.createElement("div");
    backdrop.className = "gallery-maximizer-backdrop";

    const header = document.createElement("div");
    header.className = "gallery-maximizer-header";
    const counter = document.createElement("span");
    counter.className = "gallery-maximizer-counter";
    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "gallery-maximizer-close";
    closeBtn.setAttribute("aria-label", "Cerrar");
    closeBtn.innerHTML = "×";
    header.appendChild(counter);
    header.appendChild(closeBtn);

    const content = document.createElement("div");
    content.className = "gallery-maximizer-content";

    const mediaWrap = document.createElement("div");
    mediaWrap.className = "gallery-maximizer-media";

    const prevBtn = document.createElement("button");
    prevBtn.type = "button";
    prevBtn.className = "gallery-maximizer-arrow gallery-maximizer-prev";
    prevBtn.setAttribute("aria-label", "Anterior");
    prevBtn.textContent = "‹";

    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "gallery-maximizer-arrow gallery-maximizer-next";
    nextBtn.setAttribute("aria-label", "Siguiente");
    nextBtn.textContent = "›";

    const dotsWrap = document.createElement("div");
    dotsWrap.className = "gallery-maximizer-dots";
    for (let i = 0; i < mediaItems.length; i++) {
      const dot = document.createElement("span");
      dot.className = "gallery-maximizer-dot" + (i === 0 ? " active" : "");
      dot.setAttribute("aria-label", "Ir a imagen " + (i + 1));
      dot.dataset.index = String(i);
      dotsWrap.appendChild(dot);
    }

    content.appendChild(prevBtn);
    content.appendChild(mediaWrap);
    content.appendChild(nextBtn);
    wrap.appendChild(backdrop);
    wrap.appendChild(header);
    wrap.appendChild(content);
    wrap.appendChild(dotsWrap);
    document.body.appendChild(wrap);

    function updateMedia() {
      mediaWrap.innerHTML = "";
      const item = mediaItems[currentIndex];
      if (!item) return;
      if (item.media_type === "image") {
        const img = document.createElement("img");
        img.src = item.url;
        img.alt = "";
        img.className = "gallery-maximizer-img";
        mediaWrap.appendChild(img);
      } else {
        const video = document.createElement("video");
        video.src = item.url;
        video.controls = true;
        video.className = "gallery-maximizer-video";
        mediaWrap.appendChild(video);
      }
      counter.textContent = (currentIndex + 1) + " / " + mediaItems.length;
      dotsWrap.querySelectorAll(".gallery-maximizer-dot").forEach((d, i) => {
        d.classList.toggle("active", i === currentIndex);
      });
    }

    dotsWrap.querySelectorAll(".gallery-maximizer-dot").forEach((dot) => {
      dot.addEventListener("click", (e) => {
        e.stopPropagation();
        const idx = parseInt(dot.dataset.index, 10);
        if (!isNaN(idx)) {
          currentIndex = idx;
          updateMedia();
        }
      });
    });

    function show(index) {
      currentIndex = Math.max(0, Math.min(index, mediaItems.length - 1));
      updateMedia();
      wrap.classList.add("gallery-maximizer-open");
      wrap.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }

    function hide() {
      wrap.classList.remove("gallery-maximizer-open");
      wrap.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    backdrop.addEventListener("click", hide);
    closeBtn.addEventListener("click", hide);
    prevBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      currentIndex = (currentIndex - 1 + mediaItems.length) % mediaItems.length;
      updateMedia();
    });
    nextBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      currentIndex = (currentIndex + 1) % mediaItems.length;
      updateMedia();
    });

    content.addEventListener("click", (e) => e.stopPropagation());

    document.addEventListener("keydown", (e) => {
      if (!wrap.classList.contains("gallery-maximizer-open")) return;
      if (e.key === "Escape") hide();
      if (e.key === "ArrowLeft") {
        currentIndex = (currentIndex - 1 + mediaItems.length) % mediaItems.length;
        updateMedia();
      }
      if (e.key === "ArrowRight") {
        currentIndex = (currentIndex + 1) % mediaItems.length;
        updateMedia();
      }
    });

    return { el: wrap, show, updateMedia };
  }

  overlay = createOverlay();

  function openAt(index) {
    overlay.show(index);
  }

  const track = viewer.querySelector(".slides-track");
  if (track) {
    track.querySelectorAll(".slide").forEach((slide) => {
      slide.addEventListener("click", (e) => {
        if (e.target.closest("video")) return;
        const idx = parseInt(slide.dataset.index, 10);
        if (!isNaN(idx) && idx >= 0 && idx < mediaItems.length) openAt(idx);
      });
    });
  }
})();
