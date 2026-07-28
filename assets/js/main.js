/* Apt Controls — site interactions */
(function () {
  "use strict";

  /* Mobile navigation toggle */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") nav.classList.remove("open");
    });
  }

  /* Highlight current page in navigation */
  var page = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".main-nav a").forEach(function (link) {
    var href = link.getAttribute("href");
    if (href === page || (page === "" && href === "index.html")) {
      link.classList.add("active");
    }
  });

  /* Reveal-on-scroll animation */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach(function (el) { observer.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("visible"); });
  }

  /* Hero banner carousel */
  var carousel = document.querySelector(".hero-carousel");
  if (carousel) {
    var slides = carousel.querySelector(".slides");
    var count = slides.children.length;
    var dotsWrap = carousel.querySelector(".dots");
    var current = 0;
    var timer = null;

    var goTo = function (i) {
      current = (i + count) % count;
      slides.style.transform = "translateX(-" + current * 100 + "%)";
      dotsWrap.querySelectorAll(".dot").forEach(function (d, j) {
        d.classList.toggle("active", j === current);
      });
    };
    var restart = function () {
      if (timer) clearInterval(timer);
      timer = setInterval(function () { goTo(current + 1); }, 4500);
    };

    for (var i = 0; i < count; i++) {
      var dot = document.createElement("button");
      dot.className = "dot" + (i === 0 ? " active" : "");
      dot.setAttribute("aria-label", "Go to slide " + (i + 1));
      dot.addEventListener("click", (function (idx) {
        return function () { goTo(idx); restart(); };
      })(i));
      dotsWrap.appendChild(dot);
    }
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      restart();
    }
  }

  /* Contact form — posts to FormSubmit (email) or opens WhatsApp with the enquiry prefilled */
  var form = document.getElementById("enquiry-form");
  if (form) {
    // Point the post-submit redirect at this site's own thank-you page,
    // so it works on any host (production domain, GitHub Pages, local preview).
    var nextField = document.getElementById("f-next");
    if (nextField && location.protocol.indexOf("http") === 0) {
      nextField.value =
        location.origin + location.pathname.replace(/[^/]*$/, "") + "thank-you.html";
    }

    var getField = function (id) {
      var el = document.getElementById(id);
      return el ? el.value.trim() : "";
    };

    var waButton = document.getElementById("whatsapp-send");
    if (waButton) {
      waButton.addEventListener("click", function () {
        if (!form.reportValidity()) return;
        var message =
          "New enquiry via aptcontrols.net\n" +
          "-----------------------------\n" +
          "Name: " + getField("f-name") + "\n" +
          "Company: " + (getField("f-company") || "-") + "\n" +
          "Phone: " + getField("f-phone") + "\n" +
          "Email: " + getField("f-email") + "\n" +
          "Interested in: " + getField("f-topic") + "\n\n" +
          "Requirement:\n" + getField("f-message");
        window.open(
          "https://wa.me/918878114492?text=" + encodeURIComponent(message),
          "_blank",
          "noopener"
        );
      });
    }
  }

  /* Footer year */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ------------------------------------------------------------------
     Phase-2 features — each one is controlled by a flag in config.js
     ------------------------------------------------------------------ */
  var cfg = window.APT_CONFIG || {};
  var waNumber = cfg.whatsappNumber || "918878114492";

  /* Floating WhatsApp button (cfg.whatsappFloat) */
  if (cfg.whatsappFloat) {
    var fab = document.createElement("a");
    fab.className = "wa-float";
    fab.href = "https://wa.me/" + waNumber +
      "?text=" + encodeURIComponent("Hello Apt Controls, I have an enquiry.");
    fab.target = "_blank";
    fab.rel = "noopener";
    fab.setAttribute("aria-label", "Chat with Apt Controls on WhatsApp");
    fab.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>' +
      '<span>WhatsApp</span>';
    document.body.appendChild(fab);
  }

  /* Google Analytics 4 (cfg.gaMeasurementId) */
  if (cfg.gaMeasurementId) {
    var gaScript = document.createElement("script");
    gaScript.async = true;
    gaScript.src = "https://www.googletagmanager.com/gtag/js?id=" + cfg.gaMeasurementId;
    document.head.appendChild(gaScript);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", cfg.gaMeasurementId);

    /* Conversion events */
    if (form) {
      form.addEventListener("submit", function () {
        window.gtag("event", "generate_lead", { method: "enquiry_form" });
      });
    }
    document.addEventListener("click", function (e) {
      var link = e.target.closest && e.target.closest("a");
      if (!link) return;
      var href = link.getAttribute("href") || "";
      if (href.indexOf("wa.me") !== -1) {
        window.gtag("event", "contact_whatsapp", { link_url: href });
      } else if (href.indexOf("tel:") === 0) {
        window.gtag("event", "contact_phone", { link_url: href });
      }
    });
  }
})();
