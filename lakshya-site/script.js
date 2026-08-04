const body = document.body;
const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector(".menu-toggle");
const primaryNav = document.querySelector(".primary-nav");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
body.classList.add("motion-ready");

function closeMenu({ restoreFocus = false } = {}) {
  if (!menuToggle || !primaryNav) return;
  const wasOpen = primaryNav.classList.contains("is-open");
  primaryNav.classList.remove("is-open");
  menuToggle.setAttribute("aria-expanded", "false");
  menuToggle.querySelector("span").textContent = "Open navigation";
  body.classList.remove("nav-open");
  if (wasOpen && restoreFocus) menuToggle.focus();
}

if (menuToggle && primaryNav) {
  menuToggle.addEventListener("click", () => {
    const open = primaryNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.querySelector("span").textContent = open ? "Close navigation" : "Open navigation";
    body.classList.toggle("nav-open", open);
    if (open) primaryNav.querySelector("a")?.focus();
  });

  primaryNav.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && primaryNav.classList.contains("is-open")) closeMenu({ restoreFocus: true });
  });
}

const progressBar = document.querySelector(".scroll-progress span");
let scrollTicking = false;

function updateScrollState() {
  const scrolled = window.scrollY > 24;
  header?.classList.toggle("is-scrolled", scrolled);

  if (progressBar) {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const progress = maxScroll > 0 ? Math.min(1, window.scrollY / maxScroll) : 0;
    progressBar.style.width = `${(progress * 100).toFixed(2)}%`;
  }
  scrollTicking = false;
}

window.addEventListener("scroll", () => {
  if (!scrollTicking) {
    requestAnimationFrame(updateScrollState);
    scrollTicking = true;
  }
}, { passive: true });
updateScrollState();

const revealNodes = document.querySelectorAll(".reveal");
if (reduceMotion || !("IntersectionObserver" in window)) {
  revealNodes.forEach((node) => node.classList.add("is-visible"));
} else {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -6%" });

  revealNodes.forEach((node, index) => {
    node.style.transitionDelay = `${Math.min(index % 4, 3) * 60}ms`;
    revealObserver.observe(node);
  });
}

function formatCount(value) {
  return new Intl.NumberFormat("en-IN").format(value);
}

const countNodes = document.querySelectorAll("[data-count]");
if (countNodes.length) {
  const runCounter = (node) => {
    const target = Number(node.dataset.count || 0);
    const suffix = node.dataset.suffix || "";
    if (reduceMotion) {
      node.textContent = `${formatCount(target)}${suffix}`;
      return;
    }

    const duration = target > 1000 ? 1500 : 1100;
    const startedAt = performance.now();
    const step = (now) => {
      const progress = Math.min(1, (now - startedAt) / duration);
      const eased = 1 - Math.pow(1 - progress, 4);
      node.textContent = `${formatCount(Math.round(target * eased))}${suffix}`;
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const countObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      runCounter(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.45 });
  countNodes.forEach((node) => countObserver.observe(node));
}

const systemContent = {
  teach: {
    kicker: "Foundation first",
    title: "Concepts become clear before speed becomes important.",
    copy: "Expert classroom instruction builds subject depth, connects topics and gives every chapter a deliberate place in the exam journey.",
    progress: "25%",
  },
  test: {
    kicker: "Measure precisely",
    title: "Regular testing turns preparation into visible evidence.",
    copy: "Weekly and monthly assessments track retention, speed and accuracy under exam-relevant conditions—not just classroom familiarity.",
    progress: "50%",
  },
  analyse: {
    kicker: "See the real gap",
    title: "Performance data identifies the next academic priority.",
    copy: "Teachers review patterns by topic and student, giving families a clearer picture of progress and helping intervention happen earlier.",
    progress: "75%",
  },
  reinforce: {
    kicker: "Close the loop",
    title: "Doubt support and extra guidance turn weak areas into progress.",
    copy: "Dedicated sessions, one-to-one guidance and structured digital resources help students revisit difficult concepts until confidence returns.",
    progress: "100%",
  },
};

document.querySelectorAll("[data-system-explorer]").forEach((explorer) => {
  const buttons = [...explorer.querySelectorAll("[data-system-tab]")];
  const kicker = explorer.querySelector("[data-system-kicker]");
  const title = explorer.querySelector("[data-system-title]");
  const copy = explorer.querySelector("[data-system-copy]");
  const progress = explorer.querySelector(".system-progress i");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const data = systemContent[button.dataset.systemTab];
      if (!data) return;
      buttons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-selected", String(active));
      });
      if (kicker) kicker.textContent = data.kicker;
      if (title) title.textContent = data.title;
      if (copy) copy.textContent = data.copy;
      if (progress) progress.style.width = data.progress;
    });
  });
});

document.querySelectorAll(".site-form").forEach((form) => {
  form.addEventListener("submit", () => {
    const submit = form.querySelector("button[type='submit']");
    if (!submit) return;
    submit.disabled = true;
    submit.textContent = "Sending enquiry…";
  });
});
