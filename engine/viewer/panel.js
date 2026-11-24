import { mountGraphic } from "../book.js";

/**
 * The shared graphic drawer, opened from anywhere that can name a widgets.js
 * graphic: a question's own chart button (app.js) or a printed panel's media
 * entry (`book.json` media `"widget"`, media.js).
 */
export function openGraphicPanel(id, title) {
  const drawer = document.getElementById("graphic");
  document.getElementById("graphic-title").textContent = title;
  mountGraphic(id, document.getElementById("graphic-body"));
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  document.body.classList.add("drawer-open");
}
