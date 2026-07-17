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

  /* Contact form → opens the visitor's email client with a prefilled enquiry */
  var form = document.getElementById("enquiry-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var get = function (id) {
        var el = document.getElementById(id);
        return el ? el.value.trim() : "";
      };
      var subject = "Enquiry from " + (get("f-name") || "Website") +
        (get("f-company") ? " (" + get("f-company") + ")" : "");
      var body =
        "Name: " + get("f-name") + "\n" +
        "Company: " + get("f-company") + "\n" +
        "Phone: " + get("f-phone") + "\n" +
        "Email: " + get("f-email") + "\n" +
        "Interested in: " + get("f-topic") + "\n\n" +
        get("f-message");
      location.href =
        "mailto:enquiry@aptcontrols.net" +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
    });
  }

  /* Footer year */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
