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
})();
