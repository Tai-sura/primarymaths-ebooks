/**
 * Interactive graphics for P5 Maths 07 Circles (A), opened from a question's
 * graphic button. House rules: docs/03-authoring-style.md §5.
 *
 * Six pictures, each attached to the questions that ask the same thing:
 *   circleParts      q1  q2          Center / Circumference / Radius / Diameter,
 *                                    named the way the concept page names them
 *   radiusDiameter   q10 q11 q13     d = 2r, r = d ÷ 2
 *   sixCircles       q18–q23         the printed six-circle figure (A–F) redrawn to
 *                                    scale; one circle is coloured and dashed per question
 *   lineOrDiameter   q12 q34         a line through the center is a diameter;
 *                                    any other line across the circle is just a line segment
 *   circlesInRow     q36 hw12        n equal circles in a row: AB spans (n − 1) diameters
 *   overlapCircles   q40             two circles through each other's centers: PQ = 3r
 *
 * Every straight line across a circle is a line segment here; only the one through the center
 * is a diameter. (The course does not use the older word for the others.)
 *
 * The printed page is never touched: the engine only draws a small graphic
 * button beside a question whose id is registered here.
 */

import { C, S, T, H, fmt, marker, scene, clear, slider, readout, question, buttonRow } from "../../engine/widgets/kit.js";

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
     * that line. The length labels ride that normal, the center's name rides the opposite side,
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
    T(svg, cx - nx * 26, cy - ny * 26 + 5, "圓心 Center",
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

/** q12, q34: only a line through the center is a diameter; any other is just a line segment. */
function lineOrDiameter(root, card) {
  root.append(question(card));
  const svg = scene(560, 320);
  root.append(svg);
  const cx = 280, cy = 160, R = 120;

  const again = () => {
    const d = offSlider.get();               // distance from the center, cm
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
 * q36: four equal circles, each one through the next circle's center, so
 * the center-to-center distance is r and AB (leftmost point to rightmost
 * point) spans 3r + d = 5r.
 * hw12: five circles just touching, so the center distance is d and AB
 * (first center to last center) spans (n − 1) diameters.               *
 * ------------------------------------------------------------------ */
function circlesInRow(root, card, { count = 4, start = 24, overlap = false } = {}) {
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
    const gap = overlap ? R : 2 * R;
    const width = (count - 1) * gap + 2 * R;
    clear(svg);
    const x0 = 280 - width / 2;
    // Circles first, then every dash and center dot on top of them: with gap = R the next
    // circle's fill covers the whole dash and half of the previous center dot.
    for (let i = 0; i < count; i++) {
      const cx = x0 + R + i * gap;
      S("circle", { cx, cy: y, r: R, fill: C.blueSoft, stroke: C.ink, "stroke-width": 2 }, svg);
    }
    for (let i = 0; i < count; i++) {
      const cx = x0 + R + i * gap;
      if (i < count - 1) {
        seg(svg, cx, y, cx + gap, y, C.green, { dash: "6 4", width: 2 });
      }
      dot(svg, cx, y);
    }
    const xa = overlap ? x0 : x0 + R;
    const xb = overlap ? x0 + width : x0 + R + (count - 1) * gap;
    seg(svg, xa, y + R + 26, xb, y + R + 26, C.ink, { width: 2 });
    for (const x of [xa, xb]) seg(svg, x, y + R + 21, x, y + R + 31, C.ink, { width: 2 });
    T(svg, (xa + xb) / 2 - 22, y + R + 20, "AB", { class: "g-lab", "font-size": 16, "font-weight": 700, fill: C.ink });
    lab(svg, x0 + R + 6, y - R - 10, overlap ? `r = ${r} cm` : `2r = ${2 * r} cm`, C.green);
    out.set(
      overlap
        ? `\\text{AB} = ${count - 1}r + d = ${(count - 1) * r} + ${2 * r} = ${(count - 1) * r + 2 * r}\\text{ cm}`
        : `\\text{AB} = ${count - 1} \\times ${2 * r} = ${(count - 1) * 2 * r}\\text{ cm}`,
      true,
      overlap
        ? `${count} 個圓相同，每個圓經過下一個圓的圓心，所以相鄰圓心相距 ${r} cm（即一個半徑）。AB 由第一個圓最左點到最後一個圓最右點 = ${count - 1}r + d = ${(count - 1) * r} + ${2 * r} = ${(count - 1) * r + 2 * r} cm。`
        : `${count} 個圓排成一行，圓心同圓心之間有 ${count - 1} 個直徑；每個直徑 ${2 * r} cm。`,
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

/* q40: two circles, each through the other's center. */
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
    // AB is one radius: A and B are each R from the other's center
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
 * q18–q23: the printed six-circle figure, redrawn exactly.            *
 * ------------------------------------------------------------------ */

// Geometry measured on books/p5m07a/pages/p04.jpg (3 px per pt): every rim sampled at
// 0.25° and fitted through the ink center (max deviation 1.05 px), badges and elbow
// leaders measured the same way. The print is drawn to scale at 14.223 pt/cm —
// A 3, B 2, C 5, D 1.5, E 3, F 6 cm — and B is concentric with C (centers 0.12 pt apart).
const SIX = [
  { id: "A", r: 42.69, at: [194.39, 553.38], badge: [205.05, 496.08], lead: [[195.0, 497.5], [185.0, 497.5], [185.0, 508.5]], colour: C.blue },
  { id: "B", r: 28.44, at: [127.61, 576.83], badge: [96.50, 537.31], lead: [[106.3, 537.7], [124.5, 537.7], [124.5, 549.7]], colour: C.green },
  { id: "C", r: 71.07, at: [127.60, 576.71], badge: [59.85, 506.19], lead: [[70.7, 506.4], [88.0, 506.4], [88.0, 515.3]], colour: C.amber },
  { id: "D", r: 21.37, at: [221.33, 655.84], badge: [227.09, 611.55], lead: [[217.7, 611.7], [209.5, 611.7], [209.5, 637.7]], colour: C.red },
  { id: "E", r: 42.66, at: [210.33, 674.14], badge: [236.82, 735.38], lead: [[233.0, 735.5], [197.7, 735.5], [197.7, 716.7]], colour: C.pink },
  { id: "F", r: 85.30, at: [186.52, 638.48], badge: [76.65, 659.19], lead: [[86.0, 659.9], [104.0, 659.9]], colour: C.ink },
];
// page points -> scene px
const SIX_MAP = { x: 40, y: 485, s: 1.8 };
const sx = (x) => (x - SIX_MAP.x) * SIX_MAP.s;
const sy = (y) => (y - SIX_MAP.y) * SIX_MAP.s;

// The three lengths the page itself prints: A's radius, B's radius, D's diameter.
const SIX_GIVEN = [
  { from: [195.00, 510.33], to: [195.00, 557.67], text: "3 cm" },
  { from: [98.67, 576.80], to: [130.67, 576.80], text: "2 cm" },
  { from: [200.00, 656.00], to: [242.67, 656.00], text: "3 cm" },
];
// The book's answers, in centimetres.
const SIX_CM = { A: 3, B: 2, C: 5, D: 1.5, E: 3, F: 6 };
// The printed letter badge: 19.9 pt across on the page, at the scene scale.
const BADGE_R = 9.93 * SIX_MAP.s;

// The two dashed lengths sit at one angle each: the diameter at theta, the radius 146 deg
// further round, so they can never lie on top of one another.
const THETA_R = 146;

// Every circle leans its own way by default, so the six pictures do not all start alike.
// The slider opens on the question's own circle's value; picking another circle brings that
// circle's lean with it (the last circle clicked wins), and a circle nobody has clicked keeps
// its own entry here for the moment it is first picked. Q21 shows D's radius alone, so it
// opens on D's 72 and the radius lands at 72 + 146 = 218 deg.
const SIX_ANGLE = { A: 32, B: 252, C: 252, D: 72, E: 190, F: 288 };

// A dashed length whose two ends both land on ink. The segment's own length is made an odd
// number of half dash-periods and the period is stretched to match, so both ends stop in the
// middle of a dash instead of in a gap: with a fixed "13 7" F's 307 px diameter ended about
// 7 px short of its circle.
//
// The half-period count must be ODD-halves, i.e. L/period = k + 0.5. Rounding L/20 straight
// to a half (round(L/20*2)/2) lands on a whole number for B/C/F's diameters and A/E/F's
// radii, and a whole number puts the line's end exactly where a gap begins — the end then
// stops 0.35c (4-7 px) short, the very fault this fixes. So round to the nearest k, then add
// the half. The period moves by up to ~10% on the smallest circles (D's 77 px diameter: 22.0
// against 20), which is the least any end-on-ink pattern can do at that length.
function dashFor(len, on, off) {
  const target = on + off;
  const halfPeriods = Math.max(0.5, Math.round(len / target - 0.5) + 0.5);
  const k = len / halfPeriods / target;
  return `${(on * k).toFixed(2)} ${(off * k).toFixed(2)}`;
}

/**
 * q18–q23: one figure, six circles. A–F are toggles, and one button at the end of the row
 * selects all six or clears them, its label following the state. A single 0–360° slider turns the two dashed lengths on every picked circle: the diameter at
 * theta and the radius at theta + 146°, so the two never sit on top of each other. It opens on
 * SIX_ANGLE for the question's own circle, and each newly picked circle brings its own lean
 * with it (the last one clicked wins) — see SIX_ANGLE above.
 *
 * Drawing order is the reader's rule, topmost last: the printed rims, the picked circles'
 * wash and colour ring, the two dashed lengths, the printed arrows with their haloed readings,
 * the badges with their leaders, and the center marks. So a dashed line may pass under a
 * printed arrow or its "3 cm" but never over it, and every printed length stays whole at any
 * angle. Each dashed length ends on ink at both ends: its dash period is solved from its own
 * length (dashFor), so the last dash meets the rim instead of stopping in a gap.
 * `only` narrows the question's own circle to the one length it asks for (Q21 shows D's
 * radius alone, leaving the printed 3 cm diameter arrow clear); any other picked circle shows
 * both lengths.
 */
function sixCircles(root, card, start = "A", only = "both") {
  root.append(question(card));
  const svg = scene(480, 470);
  // The drawer is one screen high and the panel also carries a slider, the key row and the A–F
  // row, so the figure's box follows the window height and keeps its own 480:500 aspect: the
  // drawing is scaled, never re-measured. The floor keeps the 13 px readings legible; below it
  // the panel scrolls rather than shrinking the figure to unreadable.
  svg.style.height = "clamp(300px, calc(100vh - 470px), 560px)";
  svg.style.width = "auto";
  const keyRow = H("div", {
    style: "display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;margin-top:8px;font-size:14px;font-weight:700;max-height:58px;overflow-y:auto",
  });
  const out = readout();
  const picked = new Set([start]);
  let theta = SIX_ANGLE[start];

  // One slider for every picked circle: the diameter sits at theta, the radius 146 deg on.
  const thetaSlider = slider({
    label: "角度",
    min: 0,
    max: 360,
    step: 1,
    value: theta,
    fmt: (v) => `${v}°`,
    play: false,
  });
  thetaSlider.on((v) => {
    theta = v;
    again();
  });
  root.append(svg, thetaSlider.el, keyRow, out.el);

  // A dash swatch for the legend: the two dashed lengths are named here and not on the
  // figure, because the six circles overlap and a label inside a 1.5 cm circle lands on
  // its neighbours.
  const key = (colour, dash, text) => {
    const row = H("span", { style: `display:inline-flex;align-items:center;gap:8px;color:${colour}` });
    const box = S("svg", { width: 54, height: 12, viewBox: "0 0 54 12" }, row);
    S("line", { x1: 2, y1: 6, x2: 52, y2: 6, stroke: colour, "stroke-width": 2.6, "stroke-dasharray": dash }, box);
    row.append(document.createTextNode(text));
    return row;
  };

  // A printed arrow: two heads, plus its reading, with a white halo so it stays
  // readable where it crosses a rim.
  const printed = ({ from, to, text }) => {
    const a = [sx(from[0]), sy(from[1])], b = [sx(to[0]), sy(to[1])];
    S("line", {
      x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: C.line, "stroke-width": 1.3,
      "marker-start": marker(svg, "arr"), "marker-end": marker(svg, "arr"),
    }, svg);
    const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
    const vertical = Math.abs(a[0] - b[0]) < 0.5;
    T(svg, vertical ? mx + 9 : mx, vertical ? my + 5 : my - 9, text, {
      "font-size": 13, "font-weight": 700, fill: C.line,
      "text-anchor": vertical ? "start" : "middle",
      stroke: "#fff", "stroke-width": 3.5, "stroke-linejoin": "round", "paint-order": "stroke",
    });
  };

  // The badge's leader, exactly as the page draws it: the measured points, in order.
  const lead = (it) => {
    const pts = it.lead.map(([x, y]) => [sx(x), sy(y)]);
    for (let i = 1; i < pts.length; i += 1) {
      seg(svg, pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], C.line, { width: 1.4 });
    }
  };

  // The question's own circle keeps its narrowing; any other picked circle shows both lengths.
  const modeOf = (id) => (id === start ? only : "both");

  // A–F are toggles; 全選 picks all six, 清除 empties the set. Picking a circle also moves the
  // slider to that circle's own opening angle (SIX_ANGLE), so the last circle clicked wins;
  // un-picking leaves the angle alone.
  const btns = new Map();
  const btnRow = H("div", { class: "g-btns" });
  for (const it of SIX) {
    const b = H("button", {
      type: "button",
      onclick: () => {
        if (picked.has(it.id)) picked.delete(it.id);
        else {
          picked.add(it.id);
          thetaSlider.set(SIX_ANGLE[it.id]);
          return;
        }
        again();
      },
    }, [it.id]);
    btns.set(it.id, b);
    btnRow.append(b);
  }
  // One button closes the row: 全選 while some circle is still out, 清除 once all six are in.
  const allBtn = H("button", {
    type: "button",
    onclick: () => {
      if (picked.size === SIX.length) picked.clear();
      else for (const it of SIX) picked.add(it.id);
      again();
    },
  }, ["全選"]);
  btnRow.append(allBtn);

  function again() {
    clear(svg);
    const ids = SIX.filter((it) => picked.has(it.id)).map((it) => it.id);
    const n = ids.length;

    // 1. the picked circles' wash, lowest of all, so it can tint nothing
    for (const it of SIX) {
      if (!picked.has(it.id)) continue;
      if (n > 2) continue;                       // three or more washes would stack into a blot
      const c = [sx(it.at[0]), sy(it.at[1])];
      S("circle", {
        cx: c[0], cy: c[1], r: it.r * SIX_MAP.s, fill: it.colour,
        "fill-opacity": 0.05, stroke: "none",
      }, svg);
    }
    // 3. the two dashed lengths: above the wash so they read, below every printed mark
    for (const it of SIX) {
      if (!picked.has(it.id)) continue;
      const c = [sx(it.at[0]), sy(it.at[1])];
      const R = it.r * SIX_MAP.s;
      const mode = modeOf(it.id);
      if (mode !== "r") {
        const a = theta * DEG;
        seg(svg, c[0] - R * Math.cos(a), c[1] - R * Math.sin(a),
          c[0] + R * Math.cos(a), c[1] + R * Math.sin(a), it.colour,
          { dash: dashFor(2 * R, 13, 7), width: 2.6 });
      }
      if (mode !== "d") {
        const a = (theta + THETA_R) * DEG;
        seg(svg, c[0], c[1], c[0] + R * Math.cos(a), c[1] + R * Math.sin(a), it.colour,
          { dash: dashFor(R, 6, 5), width: 2.4 });
      }
    }
    // 2b. the printed rims, ABOVE the dashes: a dash crossing another circle's rim must not
    //     repaint that rim. With the rims underneath, q18 lost 114 printed-ink pixels to it.
    for (const it of SIX) {
      const c = [sx(it.at[0]), sy(it.at[1])];
      S("circle", {
        cx: c[0], cy: c[1], r: it.r * SIX_MAP.s,
        fill: "none", stroke: C.line, "stroke-width": 1.2,
      }, svg);
    }
    // 3b. the colour ring of each picked circle, over the dashes, so no rim is painted over
    for (const it of SIX) {
      if (!picked.has(it.id)) continue;
      const c = [sx(it.at[0]), sy(it.at[1])];
      S("circle", {
        cx: c[0], cy: c[1], r: it.r * SIX_MAP.s, fill: "none",
        stroke: it.colour, "stroke-width": 2.2,
      }, svg);
    }
    // 4. the printed arrows and their readings, above the dashes so they always read whole
    SIX_GIVEN.forEach(printed);
    // 5. badges and their leaders, on top of every rim
    for (const it of SIX) {
      const b = [sx(it.badge[0]), sy(it.badge[1])];
      const on = picked.has(it.id);
      lead(it);
      S("circle", {
        cx: b[0], cy: b[1], r: BADGE_R, fill: on ? it.colour : "#fff",
        stroke: on ? it.colour : C.line, "stroke-width": 1.6,
      }, svg);
      T(svg, b[0], b[1] + 6, it.id, {
        "font-size": 16, "font-weight": 700, "text-anchor": "middle",
        fill: on ? "#fff" : C.line,
      });
    }
    // 6. the center marks last, so no arrow and no highlight hides one
    for (const it of SIX) {
      const c = [sx(it.at[0]), sy(it.at[1])];
      S("circle", {
        cx: c[0], cy: c[1], r: picked.has(it.id) ? 6 : 5,
        fill: it.colour, stroke: "#fff", "stroke-width": 1.6,
      }, svg);
    }
    // 7. the toggle row's state: picked = the circle's colour and white letter
    for (const it of SIX) {
      const b = btns.get(it.id);
      const on = picked.has(it.id);
      b.style.background = on ? it.colour : "#fff";
      b.style.borderColor = on ? it.colour : C.line;
      b.style.color = on ? "#fff" : C.line;
      b.style.fontWeight = "700";
    }
    allBtn.textContent = picked.size === SIX.length ? "清除" : "全選";
    // 8. legend and reading, all of it outside the figure
    const keys = [key(C.line, "6 5", "短虛線＝半徑 r"), key(C.line, "13 7", "長虛線＝直徑 d")];
    for (const id of ids) {
      const it = SIX.find((x) => x.id === id);
      const cm = SIX_CM[id];
      keys.push(H("span", {
        style: `display:inline-block;padding:2px 10px;border-radius:999px;border:1px solid ${it.colour};color:${it.colour}`,
      }, [`${id}：r ${fmt(cm)} cm、d ${fmt(2 * cm)} cm`]));
    }
    keyRow.replaceChildren(...keys);
    if (n === 0) {
      out.set("\\phantom{x}", null, "未選圓形 — 點下面的字母選擇。");
    } else if (n === 1) {
      const it = SIX.find((x) => x.id === ids[0]);
      const cm = SIX_CM[it.id];
      const mode = modeOf(it.id);
      out.set(
        mode === "r"
          ? `d = ${fmt(2 * cm)}\\text{ cm},\\quad r = d \\div 2 = ${fmt(cm)}\\text{ cm}`
          : `r = ${fmt(cm)}\\text{ cm},\\quad d = 2r = ${fmt(2 * cm)}\\text{ cm}`,
        true,
        `圓 ${it.id}：半徑 ${fmt(cm)} cm，直徑 ${fmt(2 * cm)} cm。拖「角度」轉動兩條虛線；字母可同時選幾個圓，選得少會加一層淡色。`,
        { yes: mode === "r" ? "r = d ÷ 2" : "d = 2r" },
      );
    } else {
      out.set("d = 2r", true, `已選 ${n} 個圓。轉動直徑，長度不變：d 永遠 = 2r。`, { yes: "d = 2r" });
    }
  }

  root.append(btnRow);
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
  q18: (root) => sixCircles(root, "Q18 的圓是 A。在圖中找出它：半徑 3 cm，直徑是多少？", "A"),
  q19: (root) => sixCircles(root, "Q19 的圓是 B。在圖中找出它：半徑 2 cm，直徑是多少？", "B"),
  q20: (root) => sixCircles(root, "Q20 的圓是 C。在圖中找出它：半徑 5 cm，直徑是多少？", "C"),
  q21: (root) => sixCircles(root, "Q21 的圓是 D。圖中寫着直徑 3 cm：它的半徑是多少？", "D", "r"),
  q22: (root) => sixCircles(root, "Q22 的圓是 E。在圖中找出它：半徑 3 cm，直徑是多少？", "E"),
  q23: (root) => sixCircles(root, "Q23 的圓是 F。在圖中找出它：半徑 6 cm，直徑是多少？", "F"),

  q12: (root) => lineOrDiameter(root, "AD 穿過圓心，OC 只是半徑，BE 是不是直徑？"),
  q34: (root) => lineOrDiameter(root, "AY 不穿過圓心。它還算不算直徑？"),

  q36: (root) => circlesInRow(root, "四個相同的圓，直徑 24 cm。圖中每個圓都經過下一個圓的圓心。AB 有多長？", { count: 4, start: 12, overlap: true }),
  hw12: (root) => circlesInRow(root, "五個等圓，每個半徑 12 cm。AB 有多長？", { count: 5, start: 12 }),

  q40: (root) => overlapCircles(root, "兩個圓互相穿過對方的圓心，PQ = 48 cm。求半徑與菱形周界。"),
};

export function hasGraphic(id) {
  return Boolean(REGISTRY[id]);
}

export function mountGraphic(id, root) {
  REGISTRY[id]?.(root);
}

