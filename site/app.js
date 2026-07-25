(function () {
  "use strict";

  const nav = document.querySelector(".nav");
  const menuButton = document.querySelector(".menu-button");
  const navLinks = document.querySelector(".nav-links");
  const analytics = (eventName, parameters) => window.sccAnalytics?.event(eventName, parameters);

  const updateNav = () => nav?.classList.toggle("scrolled", window.scrollY > 12);
  updateNav();
  window.addEventListener("scroll", updateNav, { passive: true });

  if (menuButton && navLinks) {
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!open));
      menuButton.setAttribute("aria-label", open ? "Open navigation" : "Close navigation");
      navLinks.classList.toggle("open", !open);
    });

    navLinks.addEventListener("click", (event) => {
      if (event.target instanceof HTMLAnchorElement) {
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Open navigation");
        navLinks.classList.remove("open");
      }
    });
  }

  const revealItems = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -35px" },
    );
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add("visible"));
  }

  const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
  const panels = Array.from(document.querySelectorAll('[role="tabpanel"]'));

  const selectTab = (tab) => {
    const target = tab.dataset.tab;
    tabs.forEach((candidate) => {
      const active = candidate === tab;
      candidate.setAttribute("aria-selected", String(active));
      candidate.tabIndex = active ? 0 : -1;
    });
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.panel !== target;
    });
    analytics("developer_example_tab", { example: target });
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = tabs.length - 1;
      selectTab(tabs[nextIndex]);
      tabs[nextIndex].focus();
    });
  });

  document.querySelectorAll(".copy-button").forEach((button) => {
    button.addEventListener("click", async () => {
      const source = document.getElementById(button.dataset.copy || "");
      if (!source) return;
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(source.innerText);
        button.textContent = "Copied";
        analytics("code_example_copy", { example: button.dataset.copy || "unknown" });
      } catch (_error) {
        button.textContent = "Select text";
      }
      window.setTimeout(() => {
        button.textContent = original;
      }, 1600);
    });
  });

  const number = (id, fallback) => {
    const element = document.getElementById(id);
    const value = Number(element?.value);
    return Number.isFinite(value) ? value : fallback;
  };

  const compactNumber = (value) =>
    new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);

  const calculate = () => {
    const tasks = Math.max(0, number("tasks", 1000));
    const tokens = Math.max(0, number("tokens", 20000));
    const reduction = Math.min(100, Math.max(0, number("reduction", 50)));
    const price = Math.max(0, number("price", 3));
    const savedTokens = tasks * 30 * tokens * (reduction / 100);
    const savedCost = (savedTokens / 1_000_000) * price;
    const tokenOutput = document.getElementById("saved-tokens");
    const costOutput = document.getElementById("saved-cost");
    if (tokenOutput) tokenOutput.textContent = compactNumber(savedTokens);
    if (costOutput) {
      costOutput.textContent = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: savedCost >= 100 ? 0 : 2,
      }).format(savedCost);
    }
  };

  ["tasks", "tokens", "reduction", "price"].forEach((id) => {
    document.getElementById(id)?.addEventListener("input", calculate);
    document.getElementById(id)?.addEventListener("change", () => {
      analytics("token_calculator_use", { field: id });
    });
  });
  calculate();

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const link = event.target.closest("a");
    if (!(link instanceof HTMLAnchorElement)) return;

    if (link.protocol === "mailto:") {
      analytics("pilot_request_click", { placement: link.closest("nav") ? "navigation" : "page" });
      return;
    }

    if (link.hostname === "github.com") {
      const pathParts = link.pathname.split("/").filter(Boolean);
      const repository = pathParts.length >= 2 ? pathParts.slice(0, 2).join("/") : "github";
      const resourceType =
        link.pathname.includes("/docs/") || link.pathname.includes("/blob/")
          ? "documentation"
          : link.pathname.includes("/deploy/") || link.pathname.includes("/tree/")
            ? "implementation"
            : "repository";
      analytics("github_resource_click", {
        repository,
        resource_type: resourceType,
      });
      return;
    }

    if (link.hash === "#economics") {
      analytics("token_savings_cta_click");
    }
  });

  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
