(function (Site) {
  if (!Site) return;

  Site.enhanceGallery = function enhanceGallery(selector) {
    const root = document.querySelector(selector);
    if (!root) return;

    const dialog = document.createElement("dialog");
    dialog.className = "lightbox";
    dialog.innerHTML = `
      <button class="lightbox__close" aria-label="Close">×</button>
      <img alt="Expanded gallery item">
      <p class="lightbox__caption"></p>
    `;
    document.body.appendChild(dialog);
    const imageEl = dialog.querySelector("img");
    const captionEl = dialog.querySelector(".lightbox__caption");
    const closeBtn = dialog.querySelector(".lightbox__close");

    const close = () => {
      if (dialog.open) {
        dialog.close();
      }
    };

    closeBtn.addEventListener("click", close);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        close();
      }
    });

    root.querySelectorAll("[data-gallery-item]").forEach((item) => {
      item.addEventListener("click", () => {
        const image = item.querySelector("img");
        if (!image) return;
        imageEl.src = image.src;
        imageEl.alt = image.alt || "Expanded gallery item";
        captionEl.textContent = item.dataset.caption || image.alt || "";
        dialog.showModal();
      });
    });
  };
})(window.Site || (window.Site = {}));
