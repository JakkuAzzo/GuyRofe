(function (Site) {
  if (!Site) return;

  Site.ready(() => {
    const sliderRoot = document.querySelector("[data-hero-slider]");
    if (sliderRoot && Site.Slider) {
      new Site.Slider(sliderRoot, { interval: 6000 });
    }

    Site.enhanceGallery?.('[data-gallery="home-editorials"]');
  });
})(window.Site || (window.Site = {}));
