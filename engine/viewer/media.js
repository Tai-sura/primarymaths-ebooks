import { BOOK, BOOK_DIR } from "../book.js";
import { openGraphicPanel } from "./panel.js";

const PAGE_W = 595.32;
/** Half the play button: it straddles the panel's top-right corner. */
const HALF = 12;
/** Clearance between the button and the page edge. */
const EDGE = 4;

/**
 * Animations (book.json "media") laid over the printed summary panels they
 * replace. The poster is the last frame, so a panel that is never played still
 * reads like the printed one.
 */
export function addMedia(pageNo, overlay) {
  for (const [n, item] of (BOOK.media || []).entries()) {
    if (item.page !== pageNo) continue;
    const [x0, y0, x1, y1] = item.region;
    const box = document.createElement("div");
    box.className = "media";
    Object.assign(box.style, { left: `${x0}px`, top: `${y0}px`, width: `${x1 - x0}px`, height: `${y1 - y0}px` });
    const video = document.createElement("video");
    Object.assign(video, { muted: true, playsInline: true, preload: "none", poster: BOOK_DIR + item.poster, src: BOOK_DIR + item.src });
    video.setAttribute("playsinline", "");
    video.setAttribute("muted", "");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "media-play";
    button.dataset.media = String(n);
    // item.ctrl = [dx, dy] (pt) nudges the button off the panel's top-right corner, for a panel whose
    // printed frame line runs through that corner; +dx moves it right, +dy moves it down. Omitted = 0.
    const [dx, dy] = item.ctrl || [0, 0];
    button.style.right = `${-Math.min(HALF, PAGE_W - EDGE - x1) - dx}px`;
    button.style.top = `${-Math.min(HALF, y0 - EDGE) + dy}px`;
    const title = item.title || "Play the animation";
    const label = (text, what) => {
      button.textContent = text;
      button.title = what;
      button.setAttribute("aria-label", what);
    };
    label("▶", title);
    video.addEventListener("play", () => { box.classList.add("playing"); label("❚❚", "Pause the animation"); });
    video.addEventListener("pause", () => {
      box.classList.remove("playing");
      label(video.ended ? "↻" : "▶", video.ended ? "Replay the animation" : "Resume the animation");
    });
    // item.widget = a widgets.js graphic that belongs to this printed panel (e.g. the
    // interactive version of a summary panel). One more round button, left of ▶.
    if (item.widget) {
      const gb = document.createElement("button");
      gb.type = "button";
      gb.className = "media-widget";
      gb.dataset.mediaWidget = String(n);
      const what = item.widgetTitle || "Open the interactive graphic";
      gb.title = what;
      gb.setAttribute("aria-label", what);
      gb.innerHTML =
        '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 16h14M5 13l4-5 3 3 4-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      gb.style.right = `${-Math.min(HALF, PAGE_W - EDGE - x1) - dx + 28}px`;
      gb.style.top = `${-Math.min(HALF, y0 - EDGE) + dy}px`;
      gb.addEventListener("click", () => openGraphicPanel(item.widget, what));
      box.append(gb);
    }
    box.append(video, button);
    overlay.append(box);
  }
}

export function toggleMedia(button) {
  const video = button.closest(".media").querySelector("video");
  if (!video.paused && !video.ended) {
    video.pause();
    return;
  }
  if (video.ended) video.currentTime = 0;
  video.play().catch(() => {});
}
