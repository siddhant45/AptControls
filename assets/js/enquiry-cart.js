/*
 * Apt Controls — "Add to Enquiry" basket (feature flag: APT_CONFIG.enquiryCart).
 *
 * Visitors collect products/brands while browsing; the list is kept in
 * localStorage and lands prefilled in the contact-page enquiry form,
 * from where it goes out by email or WhatsApp as usual.
 */
(function () {
  "use strict";
  var cfg = window.APT_CONFIG || {};
  if (!cfg.enquiryCart) return;

  var KEY = "aptEnquiryItems";

  var load = function () {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; }
    catch (e) { return []; }
  };
  var save = function (items) {
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) { /* private mode */ }
  };
  var clear = function () { save([]); render(); };

  /* ---- UI ---- */
  var fab = document.createElement("button");
  fab.className = "cart-fab";
  fab.type = "button";
  fab.setAttribute("aria-label", "View enquiry list");
  fab.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>' +
    '<span class="cart-badge">0</span>';
  document.body.appendChild(fab);

  var panel = document.createElement("div");
  panel.className = "cart-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Enquiry list");
  document.body.appendChild(panel);

  var render = function () {
    var items = load();
    fab.querySelector(".cart-badge").textContent = items.length;
    fab.classList.toggle("show", items.length > 0);
    if (!items.length) panel.classList.remove("open");
    var rows = items.map(function (name, i) {
      return '<li>' + name.replace(/</g, "&lt;") +
        '<button type="button" class="cart-remove" data-i="' + i + '" aria-label="Remove">&times;</button></li>';
    }).join("");
    panel.innerHTML =
      '<h4>Enquiry List</h4>' +
      '<ul>' + rows + '</ul>' +
      '<div class="cart-actions">' +
      '<a class="btn btn-primary btn-sm" href="contact.html#enquiry-form">Send Enquiry</a>' +
      '<button type="button" class="btn btn-sm cart-clear">Clear</button>' +
      '</div>';
  };

  fab.addEventListener("click", function () { panel.classList.toggle("open"); });

  panel.addEventListener("click", function (e) {
    if (e.target.classList.contains("cart-remove")) {
      var items = load();
      items.splice(Number(e.target.getAttribute("data-i")), 1);
      save(items);
      render();
    } else if (e.target.classList.contains("cart-clear")) {
      clear();
    }
  });

  /* ---- "Add to Enquiry" buttons (any element with data-enquiry) ---- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("[data-enquiry]");
    if (!btn) return;
    e.preventDefault();
    var name = btn.getAttribute("data-enquiry");
    var items = load();
    if (items.indexOf(name) === -1) {
      items.push(name);
      save(items);
    }
    render();
    var label = btn.textContent;
    btn.textContent = "Added ✓";
    btn.disabled = true;
    setTimeout(function () { btn.textContent = label; btn.disabled = false; }, 1400);
  });

  /* ---- Contact page: prefill the message with the list ---- */
  var form = document.getElementById("enquiry-form");
  if (form) {
    var items = load();
    var msg = document.getElementById("f-message");
    if (items.length && msg && !msg.value.trim()) {
      msg.value = "Please quote for the following:\n- " + items.join("\n- ") + "\n\n";
      var hidden = document.createElement("input");
      hidden.type = "hidden";
      hidden.name = "enquiry_items";
      hidden.value = items.join("; ");
      form.appendChild(hidden);
    }
    form.addEventListener("submit", function () { clear(); });
    var waBtn = document.getElementById("whatsapp-send");
    if (waBtn) waBtn.addEventListener("click", function () {
      if (form.checkValidity()) clear();
    });
  }

  render();
})();
