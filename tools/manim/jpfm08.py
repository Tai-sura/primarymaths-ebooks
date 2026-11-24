"""Manim film for the jpfm08 (Moments) p1 three-cell concept strip.

The strip is one printed figure on page 1: a rod A-O with the force F drawn three
ways (perpendicular to the rod, at angle theta, along the rod), with the moment arm
marked in each and the result printed under each cell:
    Moment about O = Fd   |   Moment about O = Fd sin theta   |   Moment about O = 0
The film holds a copy of the printed region as its base layer and builds the three cells in
the order asked for: each cell's force arrow is drawn again in amber exactly over the printed
one, tail and tip, so the printed arrow reads as growing with the overlay and is untouched
again once the overlay fades; every other mark sits in blank space. It adds no text and no
numbers, and the printed force arrows themselves are never moved or redrawn in place.

Where every coordinate below comes from (page points, 595.32 x 841.92, origin top
left; pages/p01.jpg is 1786 x 2526 px = 3.000 px/pt):

* The three-cell frame, measured from the page image (rows/columns holding a single
  long dark run): left border x 69.7, divider x 226.0, divider x 390.7, right border
  x 547.8; top border y 224.5, divider y 334.3, bottom border y 383.5. REGION is the
  tight frame round that box, (64, 214, 552, 388) = 488 x 174 pt (ratio 2.8046, film
  1464 x 522): row y 208-222 and y 386-392 are clear of ink all the way across, as are
  the columns x 60-68 and x 550-558, so the frame carries the three cells only. The
  printed bullet box above ends at y 205.3-206.0 and stays outside the frame.

* Text boxes come from the PDF text layer (fitz `get_text("words")`) and match the
  brief: "Moment about O" 104.66-186.64 / 263.69-345.69 / 430.27-512.28 with
  y 338.56-351.84, 337.84-351.12, 338.56-351.84; "= Fd" 128.66-151.70,
  "= Fd sin theta" 275.69-324.52 (y 361.12-374.40), "= 0" 454.27-470.02 (y 356.56-
  369.84); "d" 141.50-147.50 and 297.53-303.53, "d sin theta" 327.53-359.34
  (y 296.56-309.84). The words "moment arm", "=" and the digits are bitmap ink; their
  boxes were measured on the page image instead.

* Cell 1: the right-angle bracket is the rod's bottom border (y 257.3) plus a stroke
  at x 103.7-104.0 down to a stroke at y 266.5; the open white square inside it runs
  x 95-103.6, y 257.4-265.2 and is the only fill anywhere (no stroke, inset 0.7 pt:
  x 96.6-103.0, y 258.1-264.5), because a stroked frame of that size would have to
  graze the bracket's own strokes. The moment-arm double arrow runs x 94.7-198.3 at
  y 274.3-277.7 (shaft y 275.9); the amber double arrow is drawn exactly over it.
  The printed force arrow measures tail (93.67, 257.0) to tip (94.67, 294.33), i.e.
  the vertical at x 94.8 from the rod's underside to y 294.3.

* Cell 2: the force line was fitted to the red arrow pixels (least squares, rms
  0.86 pt): through (262.45, 272.75) along (0.525, 0.851), i.e. from A (252.0, 255.9)
  to the tip (271.67, 287.87). The perpendicular was fitted to the grey line from O
  (351.2, 254.8) toward the foot (rms 0.33 pt), along (-0.847, 0.531); the two meet at
  the foot (279.85, 300.93), which is |O-foot| = 84.9 pt = d sin theta for d = 99.2 pt
  and theta = 58.3 deg. The line of action is extended along the printed dashes from
  the tip to the foot, and the right angle is marked at the foot by an amber corner
  5.5 pt on each side, its sides along those two fitted directions.
  The label "moment arm / = d sin theta" ink is x 314.00-378.33 (nine letters of
  "moment arm", measured in the x-height band y 287.4-293.5 so the perpendicular,
  which is above 287 only left of x 312, cannot get into the measurement), y 285.0-
  307.33; "d sin theta" is 313.33-358.67 on the text layer. The amber frame at
  (312.0, 283.0, 381.0, 311.5) keeps 2.0-4.2 pt off that ink and stays 9.7 pt left of
  the cell divider; the fitted perpendicular passes 3.1 pt from the frame's top-left
  corner, so the 1.2 pt stroke does not reach it.

* Cell 3: the rod runs x 409.3-524.7 at y 253.3-259.0, O at (523.5, 256.2), the force
  arrow from A (409.5, 256.2) to its printed tip (449.7, 256.2). "moment arm d = 0"
  ink is x 414.67-522.33, y 286.67-296.00. The two amber parallel marks cross the rod
  at x 466 and 472, each a 4.6 x 6.2 pt stroke, in the blank strip between the printed
  F arrowhead and O.

* The 30 deg swing in cell 1 is an amber ring sector about O (radii 30 and 40 pt,
  printed angle 180 deg to 150 deg). It stays clear of everything printed: its inner
  radius keeps it off the rod, its outer radius stops 0.2 pt above the moment-arm
  arrow (y 274.3), and x >= 159 keeps it 11.5 pt right of the "d" label (x 141.5-147.5).

* Every amber frame round printed words is hollow (no fill) and inset 2.5 pt from the ink
  (>= 2 pt clear), so nothing inside those words changes in any frame; no overlay comes
  within 9 px of the region edge. The frames highlight by drawing their line and then
  breathing their own stroke opacity (1 -> 0.45 -> 1), never by tinting what is inside.

The base layer is drawn at the render's own pixel height with nearest-neighbour
resampling, so the frames that carry no overlay are pixel-identical to the region
crop (max abs difference 0); with Manim's default bicubic resampling they differ by
1 grey level on 2% of pixels.
"""

from pathlib import Path
import os

import numpy as np
from PIL import Image
from manim import (
    PI, RESAMPLING_ALGORITHMS, AnnularSector, Create, DashedLine, DoubleArrow, FadeIn, FadeOut,
    ImageMobject, Line, Polygon, RoundedRectangle, Scene, VGroup, ValueTracker, always_redraw,
    config, smooth, there_and_back,
)

ROOT = Path(__file__).resolve().parents[2]
AMBER = "#e8890c"          # formula / label frames (neutral highlight)
RED = "#e01b1b"            # everything about the force F (the book prints F in red)
RED_GLOW = "#ff3a3a"        # soft halo that makes the growing arrow readable on red ink
BLUE = "#1f6fd0"           # everything about the moment arm d

# ---- printed geometry, all measured (see the module docstring) ----
MARK_BOX = (96.6, 258.1, 103.0, 264.5)        # tint inside the right-angle bracket (fill only)
FD_1 = (125.2, 353.1, 155.2, 373.3)           # frame round "= Fd"
LAB_2 = (311.3, 283.0, 381.0, 311.5)          # frame round "moment arm = d sin theta"
FD_2 = (272.2, 357.6, 327.9, 377.9)           # frame round "= Fd sin theta"
LAB_3 = (411.2, 283.2, 525.8, 299.5)          # frame round "moment arm d = 0"
FD_3 = (450.8, 353.1, 473.5, 373.3)           # frame round "= 0"

# the three printed force arrows, fitted on their red pixels (tail -> tip, page pt)
C1_F = ((94.8, 257.3), (94.8, 294.3))          # cell 1: straight down from the rod at A
C2_F = ((252.0, 255.2), (271.7, 287.9))        # cell 2: down-right at 58.5 deg (dir 0.522, 0.853)
C3_F = ((409.5, 256.2), (449.7, 256.2))        # cell 3: along the rod toward O
C1_D = ((95.0, 275.9), (198.3, 275.9))         # cell 1 moment-arm double arrow (printed)
C1_O = (199.3, 254.5)                          # cell 1 hinge O (printed red dot centre)
C2_O = (351.2, 254.8)                          # cell 2 hinge O
P2_FOOT = (279.85, 300.93)                     # fitted foot of the perpendicular from O
PERP_TRACE = ((351.2, 254.8), (288.4, 296.3))  # O to just before the printed arrowhead
C3_A = (409.5, 256.2)                          # cell 3 rod, A end
C3_O = (523.5, 256.2)                          # cell 3 rod, O end (printed red dot)
C3_SLASH = (466.0, 472.0)                      # x where the two "parallel" marks cross the rod


class PageFilm(Scene):
    """A printed page region as the base layer, with page-point coordinates on top."""

    BOOK = "jpfm08"
    PAGE = 1
    REGION = (64.0, 214.0, 552.0, 388.0)

    def setup(self):
        x0, y0, x1, y1 = self.REGION
        self.k = config.frame_height / (y1 - y0)
        self.c = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.camera.background_color = "#ffffff"
        page = Image.open(ROOT / "books" / self.BOOK / "pages" / f"p{self.PAGE:02d}.jpg").convert("RGB")
        s = page.width / 595.32
        crop = page.crop((round(x0 * s), round(y0 * s), round(x1 * s), round(y1 * s)))
        self.base = ImageMobject(np.asarray(crop), scale_to_resolution=config.pixel_height)
        self.base.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        self.base.stretch_to_fit_width((x1 - x0) * self.k)
        self.base.stretch_to_fit_height((y1 - y0) * self.k)
        self.base.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(0)
        self.add(self.base)

    # ---------- page points ----------

    def P(self, x, y):
        return np.array([(x - self.c[0]) * self.k, (self.c[1] - y) * self.k, 0.0])

    def w(self, pt):
        return pt * self.k * 100

    # ---------- per-frame evidence (only when JM1_SNAP points at a folder) ----------

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        folder = os.environ.get("JM1_SNAP")
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
            self.camera.get_image().save(Path(folder) / f"{self.renderer.time:05.2f}.png")

    # ---------- overlays ----------

    def box(self, x0, y0, x1, y1, stroke=1.2, fill=0.0, radius=1.3, color=AMBER):
        r = RoundedRectangle(
            width=(x1 - x0) * self.k, height=(y1 - y0) * self.k, corner_radius=radius * self.k,
            stroke_color=color, stroke_width=self.w(stroke),
            fill_color=color, fill_opacity=fill,
        )
        r.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(6)
        return r

    # ---------- emphasis ----------

    def pulse_stroke(self, mob, run_time=0.9, opacity=0.45):
        """Breathe a hollow frame: only its own line changes, never anything inside it."""
        self.play(mob.animate(rate_func=there_and_back).set_stroke(opacity=opacity), run_time=run_time)


class MomentConcept(PageFilm):
    """Build each cell in the order asked for on the marked-up page.

    Colour code asked for by the reader: everything about the force F is RED (the colour the
    book prints F in), everything about the moment arm d is BLUE, and the formula frames stay
    amber as neutral highlights.

    Cell 1: the force arrow grows down at A (red), then the moment arm d grows out from O
    (blue), the printed right-angle bracket at A lights (blue), then the door swings about O
    by 30 deg anticlockwise, i.e. the A end down (a blue ring sector sweeping down from the rod, and back), then = Fd.
    Cell 2: the force arrow grows along the printed 58.5 deg (red), the line of action is
    extended along the printed dashes to the foot (red), a blue right-angle square is drawn
    at the foot with two of its sides on the printed lines, then the moment arm O->foot is
    traced (blue) and "moment arm = d sin theta" is framed, then = Fd sin theta. No rotation.
    Cell 3: the force arrow grows along the rod toward O (red), the rod is traced (blue) so
    F and d are visibly one and the same line, with two red parallel marks, then
    "moment arm d = 0" and = 0.

    Every frame that surrounds printed words is HOLLOW: a stroked rounded rectangle with
    no fill, so no pixel inside those words changes at any time. An earlier cut filled the
    frames with amber, which tinted the printed formulae - the poster was still
    pixel-perfect, so measuring the poster alone hid it; the text boxes are therefore
    checked frame by frame now (see tools/qa/_jm1_render.py).
    """

    # ---------- drawn marks ----------

    def draw_arrow(self, a, b, t, shaft=2.4, halfw=3.0, head=7.0):
        """The printed force arrow redrawn in red, grown to fraction t of its length.

        Red is the colour the book prints F in, so the overlay matches the arrow underneath;
        the growth reads through a soft red glow and a slightly fatter shaft (2.4 pt against
        the printed 1.2 pt). The head is 7.0 x 6.0 pt, a little larger than the printed one
        (about 6.2 x 5.0 pt), so the printed head is covered instead of showing as a fringe.
        """
        A = np.array(a, float)
        B = np.array(b, float)
        if t <= 0.001:                      # nothing at all at t = 0, so the opening frame is bare print
            return VGroup()
        d = B - A
        L = float(np.hypot(*d))
        u = d / L
        q = A + d * t
        hl = min(head, L * 0.85)
        base = q - u * hl
        n = np.array([-u[1], u[0]])
        grp = VGroup()
        if float(np.hypot(*(base - A))) > 0.4:
            grp.add(Line(self.P(*A), self.P(*q), color=RED_GLOW,
                         stroke_width=self.w(5.2)).set_stroke(opacity=0.18))
            grp.add(Line(self.P(*A), self.P(*base), color=RED, stroke_width=self.w(shaft)))
        grp.add(Polygon(self.P(*q), self.P(*(base + n * halfw)), self.P(*(base - n * halfw)),
                        color=RED, fill_color=RED, fill_opacity=1.0, stroke_width=self.w(0.4)))
        return grp.set_z_index(5)

    def grow(self, a, b, run_time=0.55):
        """Grow a printed force arrow from its tail to its tip; returns the static final group.

        The growth is a ValueTracker redraw (the head keeps its size while the tip travels);
        when the growth ends the redraw object is swapped for a static copy so it can be faded.
        """
        tr = ValueTracker(0.0)
        live = always_redraw(lambda: self.draw_arrow(a, b, tr.get_value()))
        self.add(live)
        self.play(tr.animate.set_value(1.0), run_time=run_time, rate_func=smooth)
        self.remove(live)
        still = self.draw_arrow(a, b, 1.0)
        self.add(still)
        return still

    def darrow(self, a, b, width=1.6, tip=3.4):
        """The moment arm: everything about d is blue."""
        return DoubleArrow(self.P(*a), self.P(*b), color=BLUE, stroke_width=self.w(width),
                           tip_length=tip * self.k, buff=0).set_z_index(5)

    def seg(self, a, b, width=1.6, color=None):
        return Line(self.P(*a), self.P(*b), color=color or BLUE,
                    stroke_width=self.w(width)).set_z_index(5)

    def right_angle(self, v, p1, p2, s=5.5, width=1.5):
        """A hollow blue right-angle square at v whose two near sides lie on the printed lines.

        The sides run from v along v->p1 and v->p2, so the square cannot sit off the angle the
        printed lines make: it is pinned to their vertex, exactly where the right angle is.
        """
        V = np.array(v, float)
        u1 = np.array(p1, float) - V
        u1 /= np.linalg.norm(u1)
        u2 = np.array(p2, float) - V
        u2 /= np.linalg.norm(u2)
        pts = [V, V + u1 * s, V + (u1 + u2) * s, V + u2 * s]
        return Polygon(*[self.P(*q) for q in pts], color=BLUE, stroke_width=self.w(width),
                       fill_opacity=0.0).set_z_index(6)

    def construct(self):
        # ================= cell 1: F -> d -> right angle -> 30 deg swing about O -> = Fd =================
        d1 = self.darrow(*C1_D)
        mark = self.box(*MARK_BOX, stroke=0.0, fill=0.24, color=BLUE)
        fd1 = self.box(*FD_1)

        f1 = self.grow(*C1_F, run_time=0.55)
        self.wait(0.1)
        self.play(Create(d1), run_time=0.55)
        self.play(FadeIn(mark), run_time=0.25)
        # the door swings about O: a blue ring sector sweeps 30 deg DOWN from the rod and back.
        # Anticlockwise about O takes the A end down (the lever points left, so a CCW turn drops it);
        # the sector is pinned to the rod's underside, radius 12-30 pt, so it stays the 2 pt clear of
        # the printed moment-arm arrow (y 274.3) and 14 pt above the "moment arm d" text (y 286.3).
        sweep = ValueTracker(0.5)
        ring = always_redraw(lambda: AnnularSector(
            inner_radius=12 * self.k, outer_radius=30 * self.k,
            start_angle=PI,
            angle=np.radians(30) * sweep.get_value() / 30.0,
            arc_center=self.P(199.3, 257.3), fill_color=BLUE, fill_opacity=0.16,
            stroke_color=BLUE, stroke_width=self.w(1.0)).set_z_index(4))
        self.add(ring)
        self.play(sweep.animate.set_value(30.0), run_time=0.7, rate_func=smooth)
        self.wait(0.2)
        self.play(sweep.animate.set_value(0.5), run_time=0.6, rate_func=smooth)
        self.remove(ring)
        self.play(Create(fd1), run_time=0.35)
        self.pulse_stroke(fd1, 0.5, 0.45)
        self.wait(0.1)
        self.play(FadeOut(VGroup(f1, d1, mark, fd1)), run_time=0.3)

        # ================= cell 2: F -> extend to the foot -> right angle -> d sin th -> = Fd sin th =================
        dash2 = DashedLine(self.P(*C2_F[1]), self.P(*P2_FOOT), color=RED,
                           stroke_width=self.w(1.7), dash_length=2.6 * self.k).set_z_index(5)
        right2 = self.right_angle(P2_FOOT, C2_F[0], C2_O)
        perp2 = self.seg(*PERP_TRACE, width=1.6, color=BLUE)
        lab2 = self.box(*LAB_2, radius=6.0)
        fd2 = self.box(*FD_2)

        f2 = self.grow(*C2_F, run_time=0.55)
        self.wait(0.1)
        self.play(Create(dash2), run_time=0.5)
        self.play(Create(right2), run_time=0.3)
        self.pulse_stroke(right2, 0.5, 0.45)
        self.play(Create(perp2), run_time=0.5)
        self.play(FadeIn(lab2), run_time=0.3)
        self.pulse_stroke(lab2, 0.45, 0.45)
        self.play(Create(fd2), run_time=0.35)
        self.pulse_stroke(fd2, 0.45, 0.45)
        self.wait(0.1)
        self.play(FadeOut(VGroup(f2, dash2, right2, perp2, lab2, fd2)), run_time=0.3)

        # ================= cell 3: F -> F and d are the same line -> moment arm 0 -> = 0 =================
        rod3 = self.seg(C3_A, C3_O, width=1.5, color=BLUE)
        slashes = VGroup(*[
            Line(self.P(x, 258.9), self.P(x + 4.6, 252.7), color=RED,
                 stroke_width=self.w(1.4)).set_z_index(6)
            for x in C3_SLASH
        ]).set_stroke(opacity=0.0)
        lab3 = self.box(*LAB_3)
        fd3 = self.box(*FD_3)

        f3 = self.grow(*C3_F, run_time=0.5)
        self.wait(0.1)
        self.play(Create(rod3), run_time=0.5)
        self.play(slashes.animate.set_stroke(opacity=1.0), run_time=0.3)
        self.play(slashes.animate(rate_func=there_and_back).set_stroke(opacity=0.45), run_time=0.5)
        self.play(FadeIn(lab3), run_time=0.3)
        self.pulse_stroke(lab3, 0.45, 0.45)
        self.play(Create(fd3), run_time=0.35)
        self.pulse_stroke(fd3, 0.45, 0.45)
        self.wait(0.1)
        self.play(FadeOut(VGroup(f3, rod3, slashes, lab3, fd3)), run_time=0.3)

        # ---- back to the bare print ----
        self.wait(0.4)
