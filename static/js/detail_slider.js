const slides = document.querySelectorAll(".slide");
const thumbs = document.querySelectorAll(".thumb");

function showSlide(index) {
  slides.forEach(s => s.classList.remove("active"));
  thumbs.forEach(t => t.classList.remove("active"));

  slides[index].classList.add("active");
  thumbs[index].classList.add("active");
}

thumbs.forEach(t => {
  t.addEventListener("click", () => {
    showSlide(parseInt(t.dataset.index));
  });
});