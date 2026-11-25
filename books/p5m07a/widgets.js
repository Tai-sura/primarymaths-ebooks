/**
 * Interactive graphics for P5 Maths 07 Circles (A), opened from a question's
 * graphic button. House rules: docs/03-authoring-style.md §5.
 *
 * Five pictures, each attached to the questions that ask the same thing:
 *   circleParts      q1  q2          Centre / Circumference / Radius / Diameter,
 *                                    named the way the concept page names them
 *   radiusDiameter   q10 q11 q13     d = 2r, r = d ÷ 2 (and q18–q23, the table)
 *   lineOrDiameter   q12 q34         a line through the centre is a diameter;
 *                                    any other line across the circle is just a line segment
 *   circlesInRow     q36 hw12        n equal circles in a row: AB spans (n − 1) diameters
 *   overlapCircles   q40             two circles through each other's centres: PQ = 3r
 *
 * There is no "chord" anywhere: the course calls every straight line across a circle a line
 * segment, and only the one through the centre a diameter.
 *
 * The printed page is never touched: the engine only draws a small graphic
 * button beside a question whose id is registered here.
 */

import { C, S, T, scene, clear, slider, readout, question, buttonRow } from "../../engine/widgets/kit.js";

const CM_R = 5;          // the radius our pictures show, in centimetres
const DEG = Math.PI / 180;

/** A circle with O at (cx, cy) and the given radius in scene units. */
function circle(svg, cx, cy, R, tint = C.blueSoft) {
  S("circle", { cx, cy, r: R, fill: tint, stroke: C.ink, "stroke-width": 2 }, svg);
}

function dot(svg, x, y, color = C.ink) {
  S("circle", { cx: x, cy: y, r: 4, fill: color, stroke: "#fff", "stroke-width": 1.5 }, svg);
}

/** A label on the picture: 15 px, bold, in the colour of the part it names. */
function lab(svg, x, y, text, color = C.ink) {
  T(svg, x, y, text, { class: "g-lab", "font-size": 15, "font-weight": 700, fill: color });
}

function seg(svg, x1, y1, x2, y2, color, { dash = "", width = 2.5, arrow = false } = {}) {
  S("line", {
    x1, y1, x2, y2,
    stroke: color,
    "stroke-width": width,
    "stroke-dasharray": dash,
    "marker-end": arrow ? `url(#arr${color === C.green ? "Green" : color === C.red ? "Red" : color === C.amber ? "Amber" : "Ink"}-${svg.dataset.uid})` : "",
  }, svg);
}

/** q1, q2: the four parts of a circle, named the way the concept page names them. */
function circleParts(root, card) {
  root.append(question(card));
  const svg = scene(560, 340);
  root.append(svg);

  const cx = 280, cy = 178, R = 118;
  const again = () => {
    clear(svg);
    circle(svg, cx, cy, R);

    // the circumference: a bold arc along the rim, so the name has something to point at
    const a0 = 196 * DEG, a1 = 232 * DEG;
    S("path", {
      d: `M ${cx + R * Math.cos(a0)} ${cy + R * Math.sin(a0)} A ${R} ${R} 0 0 1 ${cx + R * Math.cos(a1)} ${cy + R * Math.sin(a1)}`,
      fill: "none", stroke: C.amber, "stroke-width": 5, "stroke-linecap": "round",
    }, svg);

    const a = angle.get() * DEG;
    const ux = Math.cos(a), uy = Math.sin(a);
    const x2 = cx + R * ux, y2 = cy + R * uy;        // where the radius meets the rim
    const x1 = cx - R * ux, y1 = cy - R * uy;        // the diameter's far end
    seg(svg, x1, y1, x2, y2, C.green, { dash: "7 5", width: 2.5 });
    seg(svg, cx, cy, x2, y2, C.blue, { width: 3, arrow: true });
    dot(svg, cx, cy);
    dot(svg, x2, y2, C.blue);
    dot(svg, x1, y1, C.green);

    /* Radius and diameter are collinear, so the only direction clear of both is the normal to
     * that line. The length labels ride that normal, the centre's name rides the opposite side,
     * and each grows away from the line (anchor by the normal's x), which keeps every label off
     * the drawn lines and off the other labels for all 360 degrees. */
    let nx = -uy, ny = ux;
    if (ny > 0) { nx = -nx; ny = -ny; }
    const size = { class: "g-lab", "font-size": 14, "font-weight": 700 };
    const anchorFor = (v) => (v > 0.2 ? "start" : v < -0.2 ? "end" : "middle");
    T(svg, cx + ux * R * 0.5 + nx * 22, cy + uy * R * 0.5 + ny * 22 + 5, "半徑 Radius",
      { ...size, fill: C.blue, "text-anchor": anchorFor(nx) });
    T(svg, cx - ux * R * 0.5 + nx * 22, cy - uy * R * 0.5 + ny * 22 + 5, "直徑 Diameter",
      { ...size, fill: C.green, "text-anchor": anchorFor(nx) });
    T(svg, cx - nx * 26, cy - ny * 26 + 5, "圓心 Centre",
      { ...size, fill: C.ink, "text-anchor": anchorFor(-nx) });

    // the circumference's name sits above the arc, clear of the rim (the arc is always up-left)
    T(svg, 200, 48, "圓周 Circumference",
      { ...size, fill: C.amber, "text-anchor": "middle" });

    out.set(
      `r = ${CM_R}\\text{ cm},\\quad d = 2r = ${2 * CM_R}\\text{ cm}`,
      true,
      `所有半徑都一樣長（r = ${CM_R} cm）；直徑穿過圓心，是圓內最長的直線（${2 * CM_R} cm）。圓周就是圍住整個圓的那條曲線。`,
      { yes: "d = 2r" },
    );
  };

  const angle = slider({ label: "半徑的方向", min: 0, max: 360, step: 5, value: 60, fmt: (v) => `${v}°` });
  angle.on(again);
  const out = readout();
  root.append(angle.el, out.el);
  again();
}

/** q10, q11, q13 and the q18–q23 table: one radius, both lengths. */
function radiusDiameter(root, card, start = 9) {
  root.append(question(card));
  const svg = scene(560, 300);
  root.append(svg);
  const cx = 280, cy = 150;

  const again = () => {
    const r = rSlider.get();
    // A floor on the drawn radius: at r = 1 the old 24 px circle was smaller than its own labels.
    const R = 44 + r * 7;
    clear(svg);
    circle(svg, cx, cy, R, C.blueSoft);
    seg(svg, cx - R, cy, cx + R, cy, C.green, { dash: "7 5" });
    seg(svg, cx, cy, cx + R, cy, C.blue, { width: 3, arrow: true });
    dot(svg, cx, cy);
    dot(svg, cx + R, cy, C.blue);
    dot(svg, cx - R, cy, C.green);
    // "d" names the far half of the green line, "r" the blue half, both inside the circle
    T(svg, cx - 6, cy + 26, "O", { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.ink });
    T(svg, cx + R / 2, cy - 14, "r",
      { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.blue, "text-anchor": "middle" });
    T(svg, cx - R * 0.55, cy - 14, "d",
      { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.green, "text-anchor": "middle" });
    out.set(
      `d = 2 \\times ${r}\\text{ cm} = ${2 * r}\\text{ cm}`,
      true,
      `半徑是圓心到圓周（${r} cm）；直徑由兩條半徑接成，所以一定是半徑的 2 倍。`,
      { yes: "d = 2r" },
    );
  };

  const rSlider = slider({ label: "半徑 r（cm）", min: 1, max: 12, step: 0.5, value: start });
  rSlider.on(again);
  const out = readout();
  const quick = buttonRow([
    ["r = 4.5", () => { rSlider.set(4.5); again(); }],
    ["r = 6", () => { rSlider.set(6); again(); }],
    ["r = 9", () => { rSlider.set(9); again(); }],
    ["r = 12", () => { rSlider.set(12); again(); }],
  ]);
  root.append(rSlider.el, quick, out.el);
  again();
}

/** q12, q34: only a line through the centre is a diameter; any other is just a line segment. */
function lineOrDiameter(root, card) {
  root.append(question(card));
  const svg = scene(560, 320);
  root.append(svg);
  const cx = 280, cy = 160, R = 120;

  const again = () => {
    const d = offSlider.get();               // distance from the centre, cm
    const y = cy - (d / CM_R) * R;
    const half = Math.sqrt(Math.max(0, CM_R * CM_R - d * d));
    clear(svg);
    circle(svg, cx, cy, R, C.blueSoft);
    const through = d < 0.01;
    const hw = R * Math.sqrt(Math.max(0, 1 - (d / CM_R) ** 2));
    seg(svg, cx - hw, y, cx + hw, y, through ? C.green : C.amber, { width: 3 });
    dot(svg, cx, cy);
    T(svg, cx - 16, cy - 8, "O", { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.ink });
    // The label is a callout at the right end of the line, just outside the rim: the line always
    // ends on the rim, so this stays outside the circle at every distance and never crosses the
    // dotted distance line (whose reading sits on its other side).
    if (through) {
      T(svg, cx + R + 12, cy + 5, "直徑",
        { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.green });
    } else {
      T(svg, cx + hw + 12, y + 5, "線段 line segment",
        { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.amber });
    }
    if (!through) {
      seg(svg, cx, cy, cx, y, C.grey, { dash: "3 3", width: 1.5 });
      T(svg, cx - 8, (cy + y) / 2 - 1, `${d} cm`,
        { class: "g-lab", "font-size": 15, "font-weight": 700, fill: C.grey, "text-anchor": "end" });
    }
    if (through) {
      out.set(`\\text{直徑} = 2r = ${2 * CM_R}\\text{ cm}`, true,
        "線經過圓心，所以是直徑；所有直徑都一樣長，是圓內最長的直線。", { yes: "直徑" });
    } else {
      out.set(`\\text{線段} = 2\\sqrt{r^2 - d^2} = ${(2 * half).toFixed(1)}\\text{ cm}`, null,
        `這條線離開圓心 ${d} cm，不經過圓心，所以只是一條線段（line segment）；離圓心越遠越短，最長的是直徑 ${2 * CM_R} cm。`,
        { yes: "線段" });
    }
  };

  const offSlider = slider({ label: "線與圓心的距離（cm）", min: 0, max: 4.5, step: 0.5, value: 2 });
  offSlider.on(again);
  const out = readout();
  const quick = buttonRow([
    ["經過圓心（直徑）", () => { offSlider.set(0); again(); }],
    ["距離 2 cm", () => { offSlider.set(2); again(); }],
    ["距離 4.5 cm", () => { offSlider.set(4.5); again(); }],
  ]);
  root.append(offSlider.el, quick, out.el);
  again();
}

/* ------------------------------------------------------------------ *
 * The questions that ask "how far is it across several circles".
 * q36 (four circles), hw12 (five circles): AB joins the first centre
 * to the last, so it spans (n − 1) diameters.                         *
 * ------------------------------------------------------------------ */
function circlesInRow(root, card, { count = 4, start = 24 } = {}) {
  root.append(question(card));
  const svg = scene(560, 260);
  root.append(svg);
  const y = 130;

  const again = () => {
    const r = rSlider.get();
    // The row grows with r (55 % of the width at r = 2, the full width at r = 40),
    // so pulling the slider changes the picture, not just the reading.
    const k = 0.55 + (0.45 * (r - MIN_R)) / (MAX_R - MIN_R);
    const R = ((500 / (2 * count)) * k);
    clear(svg);
    const x0 = 280 - (count * R);
    for (let i = 0; i < count; i++) {
      const cx = x0 + R + i * 2 * R;
      S("circle", { cx, cy: y, r: R, fill: C.blueSoft, stroke: C.ink, "stroke-width": 2 }, svg);
      dot(svg, cx, y);
      if (i < count - 1) {
        const nx = cx + 2 * R;
        seg(svg, cx, y, nx, y, C.green, { dash: "6 4", width: 2 });
      }
    }
    const xa = x0 + R, xb = x0 + R + (count - 1) * 2 * R;
    seg(svg, xa, y + R + 26, xb, y + R + 26, C.ink, { width: 2 });
    for (const x of [xa, xb]) seg(svg, x, y + R + 21, x, y + R + 31, C.ink, { width: 2 });
    T(svg, (xa + xb) / 2 - 22, y + R + 20, "AB", { class: "g-lab", "font-size": 16, "font-weight": 700, fill: C.ink });
    lab(svg, xa + 6, y - R - 10, `2r = ${2 * r} cm`, C.green);
    out.set(
      `\\text{AB} = ${count - 1} \\times ${2 * r} = ${(count - 1) * 2 * r}\\text{ cm}`,
      true,
      `${count} 個圓排成一行，圓心同圓心之間有 ${count - 1} 個直徑；每個直徑 ${2 * r} cm。`,
      { yes: "AB" },
    );
  };

  const MIN_R = 2, MAX_R = 40;
  const rSlider = slider({ label: "半徑 r（cm）", min: MIN_R, max: MAX_R, step: 1, value: start });
  rSlider.on(again);
  const out = readout();
  root.append(rSlider.el, out.el);
  again();
}

/* q40: two circles, each through the other's centre. */
function overlapCircles(root, card) {
  root.append(question(card));
  const svg = scene(560, 340);
  root.append(svg);
  const cy = 130;

  const again = () => {
    const r = rSlider.get();
    const R = r * 6;
    const ax = 280 - R / 2, bx = 280 + R / 2;
    const h = (R * Math.sqrt(3)) / 2;
    const top = { x: 280, y: cy - h };
    const bot = { x: 280, y: cy + h };
    clear(svg);
    // The fills go down first: the rhombus ATBR must be drawn on top of them,
    // otherwise the two circles paint over its edges.
    circle(svg, ax, cy, R, C.blueSoft);
    circle(svg, bx, cy, R, C.amberSoft);
    for (const [x1, y1, x2, y2] of [[ax, cy, top.x, top.y], [top.x, top.y, bx, cy], [bx, cy, bot.x, bot.y], [bot.x, bot.y, ax, cy]]) {
      seg(svg, x1, y1, x2, y2, C.amber, { width: 2.5 });
    }
    // AB is one radius: A and B are each R from the other's centre
    seg(svg, ax, cy, bx, cy, C.green, { width: 3, arrow: true });
    dot(svg, ax, cy); dot(svg, bx, cy);
    lab(svg, ax - 20, cy - 8, "A");
    lab(svg, bx + 8, cy - 8, "B");
    lab(svg, 280 - 5, top.y - 12, "T");
    lab(svg, 280 - 5, bot.y + 20, "R");
    lab(svg, 280 - 9, cy - 10, "r", C.green);
    // PQ runs from the left rim of one circle to the right rim of the other
    const px = ax - R, qx = bx + R, dimY = cy + R + 30;
    seg(svg, px, dimY, qx, dimY, C.ink, { width: 2 });
    for (const x of [px, qx]) seg(svg, x, dimY - 5, x, dimY + 5, C.ink, { width: 2 });
    lab(svg, px + 8, dimY - 9, "PQ", C.ink);
    out.set(
      `\\text{PQ} = 3r = ${3 * r}\\text{ cm},\\quad \\text{perimeter} = 4r = ${4 * r}\\text{ cm}`,
      true,
      `兩個圓互相穿過對方的圓心，AB = r，所以 PQ = r + r + r = 3r；ATBR 四邊都是 r。`,
      { yes: "PQ = 3r" },
    );
  };

  const rSlider = slider({ label: "半徑 r（cm）", min: 8, max: 20, step: 1, value: 16 });
  rSlider.on(again);
  const out = readout();
  root.append(rSlider.el, out.el);
  again();
}

/* ------------------------------------------------------------------ *
 * What each question opens. One picture, several questions: the card
 * asks that question, the picture is the same idea.                  *
 * ------------------------------------------------------------------ */

const REGISTRY = {
  q1: (root) => circleParts(root, "每一條直徑都穿過圓內同一個點。這個點叫做什麼？"),
  q2: (root) => circleParts(root, "由圓心畫到圓周的線段，叫做什麼？"),

  q10: (root) => radiusDiameter(root, "直徑的長度是半徑的多少倍？"),
  q11: (root) => radiusDiameter(root, "一個圓的半徑是 9 cm，它的直徑是多少？"),
  q13: (root) => radiusDiameter(root, "半徑是直徑的一半，還是兩倍？", 6),
  q18: (root) => radiusDiameter(root, "直徑是半徑的 2 倍：把 r 拉動，看 d 怎樣變。"),
  q19: (root) => radiusDiameter(root, "直徑是半徑的 2 倍：把 r 拉動，看 d 怎樣變。"),
  q20: (root) => radiusDiameter(root, "直徑是半徑的 2 倍：把 r 拉動，看 d 怎樣變。"),
  q21: (root) => radiusDiameter(root, "已知直徑，半徑就是直徑的一半。", 3),
  q22: (root) => radiusDiameter(root, "已知直徑，半徑就是直徑的一半。", 3),
  q23: (root) => radiusDiameter(root, "已知直徑，半徑就是直徑的一半。", 6),

  q12: (root) => lineOrDiameter(root, "AD 穿過圓心，OC 只是半徑，BE 是不是直徑？"),
  q34: (root) => lineOrDiameter(root, "AY 不穿過圓心。它還算不算直徑？"),

  q36: (root) => circlesInRow(root, "四個圓排成一行，相鄰圓心相距 24 cm。AB 有多長？", { count: 4, start: 12 }),
  hw12: (root) => circlesInRow(root, "五個等圓，每個半徑 12 cm。AB 有多長？", { count: 5, start: 12 }),

  q40: (root) => overlapCircles(root, "兩個圓互相穿過對方的圓心，PQ = 48 cm。求半徑與菱形周界。"),
};

export function hasGraphic(id) {
  return Boolean(REGISTRY[id]);
}

export function mountGraphic(id, root) {
  REGISTRY[id]?.(root);
}
