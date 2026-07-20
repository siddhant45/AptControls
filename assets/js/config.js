/*
 * Apt Controls — site configuration.
 *
 * Every phase-2 feature reads its switch from here. To turn a feature off,
 * set its flag to false and redeploy — no other file needs to change.
 */
window.APT_CONFIG = {
  /* WhatsApp number used by the floating button, enquiry form and cart
     (country code + number, digits only). */
  whatsappNumber: "918878114492",

  /* Floating WhatsApp chat button, shown on every page. */
  whatsappFloat: true,

  /* "Add to Enquiry" basket: collect products/brands while browsing and
     send one combined enquiry from the contact page. */
  enquiryCart: true,

  /* Google Analytics 4. Leave "" to keep analytics completely off.
     Paste the property's Measurement ID (looks like "G-XXXXXXXXXX") to
     enable page-view tracking plus conversion events:
       - generate_lead   (enquiry form submitted)
       - contact_whatsapp (any WhatsApp link/button clicked)
       - contact_phone    (any phone number clicked)  */
  gaMeasurementId: ""
};
