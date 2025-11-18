(function () {
  const Site = {
    ready(callback) {
      if (document.readyState !== "loading") {
        callback();
      } else {
        document.addEventListener("DOMContentLoaded", callback);
      }
    },
  };

  Site.initNav = function initNav() {
    const toggle = document.querySelector("[data-nav-toggle]");
    const nav = document.querySelector(".site-nav");

    if (!toggle || !nav) return;

    const setState = (open) => {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };

    toggle.addEventListener("click", () => {
      const isOpen = nav.classList.contains("is-open");
      setState(!isOpen);
    });

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setState(false));
    });
  };

  Site.initScrollAccent = function initScrollAccent() {
    const header = document.querySelector(".site-header");
    if (!header) return;

    const update = () => {
      header.classList.toggle("is-floating", window.scrollY > 24);
    };

    update();
    window.addEventListener("scroll", update, { passive: true });
  };

  window.Site = Site;

  Site.ready(() => {
    Site.initNav();
    Site.initScrollAccent();
  });
})();
