import { BOOK } from "../book.js";

/**
 * Interactive explainers published under /explainers/, opened from a tab in the
 * page margin (book.json "embeds").
 *
 *   "embeds": [
 *     { "page": 3, "at": [1.5, 410.75], "title": "…", "sub": "q3 / q5",
 *       "src": "explainers/moment-balance/moment-balance.html" }
 *   ]
 *
 * `at` is the tab's top-left corner in page points and must sit on measured blank
 * margin: the tab is 20 x 22 pt. `src` is relative to the site root (reader.html),
 * so the same path works from books/<id>/ and from a local QA server.
 *
 * The explainers are complete pages of their own — a slider, a canvas, its own
 * layout — so they open in a full-screen panel with an iframe rather than being
 * rebuilt inside the reader. The iframe keeps their own CSS, their own p5 sketch
 * and their own no-scroll layout, and closing it drops the iframe so the sketch
 * stops running.
 */
const EMBEDS = BOOK.embeds || [];

const ICON = `<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 6.4h14M3 13.6h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none"/><circle cx="7.2" cy="6.4" r="2.3" fill="currentColor"/><circle cx="12.8" cy="13.6" r="2.3" fill="currentColor"/></svg>`;

/** One tab per embed on this page; the tab lives in the overlay, so it scales with the sheet. */
export function addEmbeds(page, overlay) {
  EMBEDS.forEach((item, i) => {
    if (item.page !== page.page) return;
    const [x, y] = item.at || [];
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "emb-btn";
    btn.dataset.embed = String(i);
    const what = item.sub ? `${item.title}（${item.sub}）— 互動示範` : `${item.title} — 互動示範`;
    btn.title = what;
    btn.setAttribute("aria-label", what);
    btn.innerHTML = ICON;
    Object.assign(btn.style, { left: `${x}px`, top: `${y}px` });
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      openEmbed(i);
    });
    overlay.append(btn);
  });
}

let modal = null;
let frame = null;
let title = null;
let sub = null;

/** True when the question's own graphic button should open an explainer. */
export function hasEmbed(id) {
  return EMBEDS.some((item) => item.q === id);
}

/** Opens the explainer that belongs to question `id` (its own widget button). */
export function openEmbedForQ(id) {
  const i = EMBEDS.findIndex((item) => item.q === id);
  if (i >= 0) openEmbed(i);
}

function build() {
  modal = document.createElement("div");
  modal.className = "embed-modal";
  modal.setAttribute("aria-hidden", "true");
  const card = document.createElement("div");
  card.className = "embed-card";
  card.setAttribute("role", "dialog");
  card.setAttribute("aria-modal", "true");
  const head = document.createElement("header");
  title = document.createElement("strong");
  sub = document.createElement("span");
  sub.className = "embed-sub";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "embed-close";
  close.textContent = "關閉 ✕";
  close.title = "Close (Esc)";
  close.addEventListener("click", () => closeEmbed());
  head.append(title, sub, close);
  frame = document.createElement("div");
  frame.className = "embed-frame";
  card.append(head, frame);
  modal.append(card);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeEmbed();
  });
  document.body.append(modal);
  modal.querySelector("header").setAttribute("id", "embed-head");
  card.setAttribute("aria-labelledby", "embed-head");
  return modal;
}

export function openEmbed(i) {
  const item = EMBEDS[i];
  if (!item) return;
  if (!modal) build();
  title.textContent = item.title || "互動示範";
  sub.textContent = item.sub || "";
  sub.hidden = !item.sub;
  // A fresh iframe every time: the sketch starts from its preset instead of
  // resuming whatever the last reader left on screen.
  const iframe = document.createElement("iframe");
  iframe.title = item.title || "Interactive explainer";
  iframe.setAttribute("allow", "fullscreen");
  iframe.src = new URL(item.src, document.baseURI).href;
  // The first open fetches p5 (~1 MB) on a cold cache; until then the frame is
  // white. Say so instead of showing an empty box.
  const loading = document.createElement("div");
  loading.className = "embed-loading";
  loading.textContent = "載入互動示範…";
  iframe.addEventListener("load", () => loading.remove());
  frame.replaceChildren(iframe, loading);
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  document.body.classList.add("embed-open");
}

export function closeEmbed() {
  if (!modal || !modal.classList.contains("open")) return;
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("embed-open");
  frame.replaceChildren();
}

export function embedOpen() {
  return Boolean(modal && modal.classList.contains("open"));
}

document.addEventListener(
  "keydown",
  (event) => {
    if (!embedOpen()) return;
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      closeEmbed();
    }
  },
  true
);
