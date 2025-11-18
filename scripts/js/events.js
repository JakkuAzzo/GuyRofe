(function (Site) {
  if (!Site) return;

  Site.ready(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          entry.target.classList.toggle("is-visible", entry.isIntersecting);
        });
      },
      { threshold: 0.25 }
    );

    document.querySelectorAll(".timeline__item").forEach((item) => observer.observe(item));

    Site.enhanceGallery?.('[data-gallery="events"]');
  });
})(window.Site || (window.Site = {}));
