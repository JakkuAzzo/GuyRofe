(function (Site) {
  if (!Site) return;

  Site.ready(() => {
    const counter = document.querySelector("[data-gallery-count]");
    const items = document.querySelectorAll("[data-gallery-item]");
    if (counter) {
      counter.textContent = `${items.length} featured frames`;
    }

    Site.enhanceGallery?.('[data-gallery="sports"]');
  });
})(window.Site || (window.Site = {}));
