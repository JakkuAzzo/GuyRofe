(function (Site) {
  if (!Site) return;

  class Slider {
    constructor(root, { interval = 7000 } = {}) {
      this.root = root;
      this.slides = Array.from(root.querySelectorAll(".hero-slide"));
      this.interval = interval;
      this.current = 0;
      this.dots = null;
      this.timer = null;
      this.prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      this.setupDots();
      this.show(0);
      if (!this.prefersReducedMotion) {
        this.start();
      }
    }

    setupDots() {
      const dotsContainer = document.createElement("div");
      dotsContainer.className = "hero-slider__dots";
      this.slides.forEach((_, index) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.addEventListener("click", () => this.show(index));
        dotsContainer.appendChild(dot);
      });
      this.root.appendChild(dotsContainer);
      this.dots = Array.from(dotsContainer.children);
    }

    show(index) {
      if (!this.slides.length) return;
      this.slides[this.current]?.classList.remove("is-active");
      this.slides[index].classList.add("is-active");
      this.dots?.forEach((dot, dotIndex) => {
        dot.setAttribute("aria-current", String(dotIndex === index));
      });
      this.current = index;
      if (!this.prefersReducedMotion) {
        this.restart();
      }
    }

    next() {
      const nextIndex = (this.current + 1) % this.slides.length;
      this.show(nextIndex);
    }

    start() {
      this.timer = window.setInterval(() => this.next(), this.interval);
    }

    restart() {
      this.stop();
      this.start();
    }

    stop() {
      if (this.timer) {
        window.clearInterval(this.timer);
      }
    }
  }

  Site.Slider = Slider;
})(window.Site || (window.Site = {}));
