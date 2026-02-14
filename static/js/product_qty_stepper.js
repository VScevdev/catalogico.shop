document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".product-add-to-cart");
  if (!form) return;

  const input = form.querySelector(".product-qty-input");
  const plusBtn = form.querySelector(".qty-plus");
  const minusBtn = form.querySelector(".qty-minus");
  if (!input || !plusBtn || !minusBtn) return;

  const min = parseInt(input.min, 10) || 1;
  const max = parseInt(input.max, 10) || 999;

  function updateValue(val) {
    const n = Math.max(min, Math.min(max, val));
    input.value = n;
  }

  plusBtn.addEventListener("click", () => {
    updateValue(parseInt(input.value, 10) + 1);
  });

  minusBtn.addEventListener("click", () => {
    updateValue(parseInt(input.value, 10) - 1);
  });
});
