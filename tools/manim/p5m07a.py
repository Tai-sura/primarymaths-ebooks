"""Manim film for the p5m07a concept page (page 2 of the PDF, printed as page 1).

The printed page already shows the four names with boxes and arrows; this film adds the
teaching motion the user asked for without repainting anything printed: it holds the printed
region as the base layer, fades it out, draws the same circle again cleanly in the page's own
colours, names the four parts one at a time (bilingual, as the widgets do), and turns the radius
into the diameter by laying a second radius beside it (diameter = 2 x radius). It then sweeps the
red diameter a full 360 deg about the centre at a constant speed while the remark that the
diameter is the longest straight line inside the circle comes in, in the same red. Finally the
overlay cross-fades back to the printed region - the drawn layer fades out as the printed page
fades in, so no frame is ever blank and the closing frame is the page itself.

Geometry, measured from books/p5m07a/pages/p02.jpg (1786 x 2526 px = 3.000 px/pt):

* The printed circle's ring runs x 156-342 pt and y 146-332 pt, i.e. centre (249, 239) and
  radius 93 pt. The re-drawn circle uses exactly that centre and radius, so the fade in and
  out does not jump.
* The printed radius (green) runs from the centre to about (183, 305): 225 deg, down-left.
  The printed diameter (red) is a near-vertical line through the centre. The film uses the
  clean pair: diameter vertical, radius at 225 deg.
* The four printed name boxes sit at x 45-170 (left: Circumference y 210-232, Radius y 248-274)
  and x 380-480 (right: Center y 168-190, Diameter y 208-236). Our labels go in the same four
  corners, drawn only while the printed layer is faded out.
* The strip y 332-346 pt between the circle and the blue rule box is blank;
  that is where the two captions go.
* REGION is (40, 130, 546, 346) = 506 x 216 pt, ratio 2.34, film 1518 x 648. It carries the
  four name boxes and the circle, and stops above the blue rule box.
"""

import math

import numpy as np

from manim import (
    Arc, CapStyleType, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, GrowFromCenter, Line,
    NORMAL, Polygon, Rectangle, Rotate, Scene, Text, VGroup, ValueTracker, Write, always_redraw,
    config, linear, smooth,
)

from jpfm08 import PageFilm

ORANGE = "#ef9a33"
ORANGE_DEEP = "#d9791a"
RED = "#e0453a"
GREEN = "#8cc63f"
BLUE = "#2f6fd6"
INK = "#1a1a1a"
CJK = "Microsoft JhengHei"


class CircleBasics(PageFilm):
    BOOK = "p5m07a"
    PAGE = 2
    REGION = (40.0, 130.0, 546.0, 346.0)

    C = (249.0, 239.0)          # the printed circle's centre
    R = 93.0                    # and its radius, both measured on the page

    # ---------- small helpers in page points ----------

    def pt(self, a_deg, r=None):
        """A point at a page angle (0 deg = east, 90 deg = down)."""
        r = self.R if r is None else r
        a = a_deg * math.pi / 180
        return (self.C[0] + r * math.cos(a), self.C[1] + r * math.sin(a))

    def line(self, a, b, color=INK, width=1.6):
        return Line(self.P(*a), self.P(*b), color=color, stroke_width=self.w(width))

    def dot(self, p, color=INK, r=2.0):
        return Dot(self.P(*p), radius=r * self.k, color=color)

    def _dir(self, a, b):
        d = self.P(*b) - self.P(*a)
        return d / float(((d ** 2).sum()) ** 0.5)

    def word(self, s, x, y, size, color, weight=NORMAL, anchor="center"):
        """Text whose ink is `size` page points tall, placed at (x, y)."""
        t = Text(s, font=CJK, font_size=64, color=color, weight=weight, disable_ligatures=True)
        t.scale(size * self.k / t.height)
        p = self.P(x, y)
        if anchor == "center":
            t.move_to(p)
        elif anchor == "left":
            t.shift(p - t.get_left())
        else:
            t.shift(p - t.get_right())
        return t

    def arrow(self, a, b, color, width=1.1, head=3.4):
        """A thin leader with a small solid head, like the printed box arrows."""
        d = self._dir(a, b)
        nrm = (-d[1], d[0], 0.0)
        tip = self.P(*b)
        back = tip - d * head * self.k
        shaft = Line(self.P(*a), back, color=color, stroke_width=self.w(width))
        hw = head * 0.42 * self.k
        tri = Polygon(tip, back + [nrm[0] * hw, nrm[1] * hw, 0], back - [nrm[0] * hw, nrm[1] * hw, 0],
                      color=color, fill_color=color, fill_opacity=1, stroke_width=0)
        return VGroup(shaft, tri)

    # ---------- the film ----------

    def construct(self):
        base = self.base
        self.wait(0.2)

        # the printed page is taken away on its own, and only then does anything get drawn: no
        # frame ever shows the printed labels and the drawn ones at the same time
        self.play(FadeOut(base), run_time=0.3)
        circle = Circle(radius=self.R * self.k, color=ORANGE, stroke_width=self.w(3.2)).move_to(self.P(*self.C))
        self.play(Create(circle), run_time=1.4)

        # 1. the circumference: the whole ring changes colour for a moment - same path, same
        #    3.2 pt stroke - so no stretch of it can ever look thicker than the rest
        a0, a1 = 196, 236
        cap = self.word("圓周 Circumference", 103, 219, 9.6, ORANGE)
        # the leader stops 3.5 pt outside the rim, so its ink never merges with the
        # ring and makes that stretch read thicker
        lead = self.arrow(self.pt(a0 - 4, self.R + 26),
                          self.pt((a0 + a1) / 2 - 3, self.R + 3.5), ORANGE)
        self.play(circle.animate.set_stroke(color=ORANGE_DEEP), FadeIn(cap), Create(lead),
                  run_time=0.9)
        self.wait(0.5)
        self.play(circle.animate.set_stroke(color=ORANGE), run_time=0.5)

        # 2. the centre
        dot = self.dot(self.C, color=BLUE, r=2.4)
        cap2 = self.word("圓心 Centre", 432, 179, 9.6, BLUE)
        lead2 = self.arrow((392, 184), (self.C[0] + 3, self.C[1] - 3), BLUE)
        self.play(FadeIn(dot), FadeIn(cap2), Create(lead2), run_time=1.2)

        # 3. the radius
        rad = self.line(self.C, self.pt(135), GREEN, width=2.2)
        cap3 = self.word("半徑 Radius", 104, 262, 9.6, GREEN)
        lead3 = self.arrow((150, 262), (self.C[0] - 30, self.C[1] + 30), GREEN)
        self.play(Create(rad), FadeIn(cap3), Create(lead3), run_time=1.2)

        # 4. the diameter: the same straight line carried through the centre
        dia = self.line(self.pt(270), self.pt(90), RED, width=2.2)
        cap4 = self.word("直徑 Diameter", 432, 221, 9.6, RED)
        lead4 = self.arrow((392, 225), (self.C[0] + 2, self.C[1] + 32), RED)
        self.play(Create(dia), FadeIn(cap4), Create(lead4), run_time=1.3)

        # 5. d = 2r: one more radius, laid on the other side of the centre
        rad2 = self.line(self.C, self.pt(315), GREEN, width=2.2)
        note = self.word("直徑 = 2 × 半徑", self.C[0], 339, 8.6, INK)
        self.play(Create(rad2), Write(note), run_time=1.6)
        self.wait(0.6)

        # 6. the red diameter sweeps one full turn about the centre, and the remark that it is
        #    the longest chord inside the circle comes in with it (same red as the diameter)
        # the green radii and the two leaders would end up lying under the turning diameter, so
        # they clear out first; only the circle, the diameter, its label and the remark remain
        note2 = self.word("直徑是圓內最長的直線", self.C[0], 339, 8.6, RED)
        self.play(FadeOut(note), FadeOut(rad), FadeOut(rad2), FadeOut(cap3), FadeOut(lead3),
                  FadeOut(lead2), FadeOut(lead4), run_time=0.4)
        self.play(
            Rotate(dia, -2 * math.pi, about_point=self.P(*self.C), rate_func=linear, run_time=2.8),
            FadeIn(note2, run_time=2.8),
            run_time=2.8,
        )
        self.wait(0.25)

        # 7. the drawn labels leave first, so no frame ever carries the drawn words and the
        #    printed ones together; then the geometry cross-fades back to the printed page,
        #    which is the image the film opens on
        self.play(FadeOut(VGroup(cap, cap2, cap4, note2, lead)), run_time=0.3)
        self.play(FadeOut(VGroup(circle, dot, dia)), FadeIn(base), run_time=0.6)
        self.wait(0.3)


# ------------------------------------------------------------------ the 6-panel comic film

C_INK = "#242424"
C_FRAME = "#141414"
C_BAND = "#ffcc73"
C_LEG = "#4a4f56"
C_HI = "#aab1b8"
C_METAL = "#dfe3e8"
C_AMBER = "#e8890c"
C_RULER = "#ffe9a0"        # translucent plastic ruler, cell 6
C_RULER_EDGE = "#c9a24a"


class CircleCompass(Scene):
    """The printed 6-panel strip "How to draw a circle?" redrawn and animated (p5m07a p.1).

    The printed strip is a licensed illustration, so none of it is reused: the six cells,
    the compass and every stroke below are drawn from scratch, in the page's own palette
    (orange band #ffcc73, ink line art, amber pencil). The layout and the reading order are
    the printed ones, so the reader's eye follows the same six steps:

        1 the compass is opened to the radius     2 the needle is set on the centre
        3 a short arc starts                      4 the arc grows
        5 the circle closes                       6 the radius is drawn in

    The film opens on the finished comic - all six cells drawn - because the reader sees
    frame 0 as the panel poster until they press play, and an empty strip there would hide
    the printed comic behind six blank frames. It holds that image 0.40 s, clears it in
    0.40 s, then draws the six cells again one at a time (step 1 at 0.80 s), and closes on
    exactly the same finished image for 1.3 s. Poster, first frame and last frame are the
    same pixels, so looping or stopping never jumps.

    Geometry, measured on books/p5m07a/pages/p02.jpg (1786 x 2526 px = 3.000 px/pt):
    the strip is one box x 68.0-298.0, y 556.3-750.0 pt. Its ink bands are the verticals
    x 68.00-68.67 / 144.33-145.00 / 221.00-221.67 / 297.33-298.00 and the horizontals
    y 556.33-557.00 / 653.66-654.00 / 749.33-750.00, so the frame line centres are
    x 68.33 / 144.67 / 221.33 / 297.67 and y 556.67 / 653.83 / 749.67 (six cells of
    76.3 x 96.5 pt). The orange band runs from each cell's top to +36.3 pt (measured
    556.7-593.0 in row 1 and 654.0-690.0 in row 2); the white paper under it is cut at
    the top-left, so the orange dips 15 pt lower over the first 21 pt of the cell.
    REGION = (68, 556, 298, 750) = 230 x 194 pt (ratio 1.1856; film 690 x 582, i.e.
    3 px/pt like the page). Its top edge is 0.33 pt above the printed frame and its left
    edge 0.33 pt left of it, both blank white, so the film's own frame at the measured
    positions replaces the printed one with no sliver of orange left over.

    Note the strip ends at y 750.0, not 725.0: rows y 739-749 carry the bottom row's
    drawings and y 749.33-750.00 is the frame's bottom line, with only white below
    (y 751-790: ink 0). A region cut at 725 would slice the bottom off cells 4-6.

    Step numbers 1-6 sit at each cell's top-left, 5.2 pt tall, as printed. The compass is
    geometrically honest: the needle touches the cell's centre point and the pencil sits
    exactly one radius away, so the arc it draws has radius = the compass opening.

    Cell 6 then measures that radius with a translucent ruler (48 % opaque pale yellow, so
    the radius line reads through it): its 0 graduation is on the centre and its 3 cm
    graduation on the rim, the body running 3.6 pt past the last mark like a real ruler's
    end margin, with the reading "r = 3 cm" written under it inside the circle. The ruler
    slides in from beyond the region's right edge 0.35 s after the radius is drawn and stays
    to the end, so the poster (frame 0), the hold before the clear, and the closing frame all
    carry the same finished comic with the ruler in place.
    """

    BOOK = "p5m07a"
    PAGE = 2
    REGION = (68.0, 556.0, 298.0, 750.0)

    COLS = (68.33, 144.67, 221.33, 297.67)      # frame line centres, page pt
    ROWS = (556.67, 653.83, 749.67)
    BAND = 36.3                                  # orange band height in every cell
    R_C = 26.0                                   # the circle the compass draws
    L = 22.0                                     # compass leg length (short enough to swing
                                                 # a full turn inside one cell)

    def setup(self):
        x0, y0, x1, y1 = self.REGION
        self.k = config.frame_height / (y1 - y0)
        self.px = (x0 + x1) / 2.0
        self.py = (y0 + y1) / 2.0
        self.camera.background_color = "#ffffff"

    # ---------- page points ----------

    def P(self, x, y):
        return np.array([(x - self.px) * self.k, (self.py - y) * self.k, 0.0])

    def w(self, pt):
        return pt * self.k * 100

    def cell(self, i):
        r, c = divmod(i, 3)
        return (self.COLS[c], self.ROWS[r], self.COLS[c + 1], self.ROWS[r + 1])

    def centre(self, i):
        """The needle point of cell i: the centre of the circle drawn there."""
        x0, y0, x1, y1 = self.cell(i)
        return (x0 + 0.47 * (x1 - x0), y1 - 4.0 - self.R_C)

    def polar(self, N, r, a_deg):
        a = math.radians(a_deg)
        return (N[0] + r * math.cos(a), N[1] + r * math.sin(a))

    # ---------- the six cells ----------

    def background(self):
        g = VGroup()
        for i in range(6):
            x0, y0, x1, y1 = self.cell(i)
            g.add(Polygon(self.P(x0, y0), self.P(x1, y0), self.P(x1, y0 + self.BAND),
                          self.P(x0, y0 + self.BAND), color=C_BAND, fill_color=C_BAND,
                          fill_opacity=1.0, stroke_width=0))
            g.add(Polygon(self.P(x0 + 21, y0 + self.BAND), self.P(x1, y0 + self.BAND),
                          self.P(x1, y1), self.P(x0, y1), self.P(x0, y0 + self.BAND + 15),
                          color="#dcdcda", fill_color="#ffffff", fill_opacity=1.0,
                          stroke_width=self.w(0.5)))
        for x in self.COLS:
            g.add(Line(self.P(x, self.ROWS[0]), self.P(x, self.ROWS[-1]), color=C_FRAME,
                       stroke_width=self.w(0.67)))
        for y in self.ROWS:
            g.add(Line(self.P(self.COLS[0], y), self.P(self.COLS[-1], y), color=C_FRAME,
                       stroke_width=self.w(0.67)))
        for i in range(6):
            x0, y0, x1, y1 = self.cell(i)
            t = Text(str(i + 1), font=CJK, font_size=64, color=C_FRAME, disable_ligatures=True)
            t.scale(5.2 * self.k / t.height)
            t.move_to(self.P(x0 + 4.6, y0 + 5.4))
            g.add(t)
        return g

    def ring(self, i):
        """A thin amber outline that marks the cell being drawn right now."""
        x0, y0, x1, y1 = self.cell(i)
        inset = 1.7
        return Rectangle(width=(x1 - x0 - 2 * inset) * self.k, height=(y1 - y0 - 2 * inset) * self.k,
                         stroke_color=C_AMBER, stroke_width=self.w(1.4), fill_opacity=0.0).move_to(
            self.P((x0 + x1) / 2.0, (y0 + y1) / 2.0))

    # ---------- the compass (our own drawing) ----------

    def compass(self, N, r, phi=0.0):
        """Flat 2D compass: needle at N, pencil one radius r away at page angle phi.

        The body turns rigidly about the needle with phi: the hinge sits on the perpendicular
        bisector of the two feet, on the side fixed in the instrument's own frame (the side
        that is "up" when the pencil is at 0 deg). So the pencil foot and the hinge swing round
        together, exactly as a real compass does when it is turned by its handle, and the leg
        opening never changes.
        """
        a = math.radians(phi)
        u = np.array([math.cos(a), math.sin(a)])
        Pn = np.array(N, float)
        Pp = Pn + r * u
        M = (Pn + Pp) / 2.0
        hh = math.sqrt(max(self.L * self.L - (r / 2.0) ** 2, 1.0))
        nrm = np.array([u[1], -u[0]])          # rigid: (sin phi, -cos phi), no side flipping
        H = M + hh * nrm

        def quad(a0, b0, wa, wb, color):
            d = b0 - a0
            ln = float(np.hypot(*d))
            du = d / ln
            nn = np.array([-du[1], du[0]])
            return Polygon(self.P(*(a0 + nn * wa / 2)), self.P(*(a0 - nn * wa / 2)),
                           self.P(*(b0 - nn * wb / 2)), self.P(*(b0 + nn * wb / 2)),
                           color=color, fill_color=color, fill_opacity=1.0, stroke_width=0)

        dn = (Pn - H) / float(np.hypot(*(Pn - H)))
        dp = (Pp - H) / float(np.hypot(*(Pp - H)))
        foot_n = Pn - dn * 5.0
        foot_p = Pp - dp * 6.4

        g = VGroup()
        g.add(quad(H, foot_n, 3.8, 2.0, C_LEG))
        g.add(quad(H, foot_p, 3.8, 2.2, C_LEG))
        for foot, dvec in ((foot_n, dn), (foot_p, dp)):
            nn = np.array([-dvec[1], dvec[0]]) * 0.95
            g.add(Line(self.P(*(H + nn)), self.P(*(foot + nn)), color=C_HI, stroke_width=self.w(0.55)))
        g.add(quad(H, H + nrm * 6.5, 3.1, 2.3, C_LEG))
        # hinge: knurled wheel, body and pin
        g.add(Circle(radius=5.2 * self.k, color=C_HI, stroke_width=self.w(0.7)).move_to(self.P(*H)))
        g.add(Circle(radius=3.3 * self.k, color=C_LEG, stroke_width=0, fill_color=C_LEG,
                     fill_opacity=1.0).move_to(self.P(*H)))
        g.add(Circle(radius=1.2 * self.k, color=C_METAL, stroke_width=0, fill_color=C_METAL,
                     fill_opacity=1.0).move_to(self.P(*H)))
        g.add(Circle(radius=1.8 * self.k, color=C_LEG, stroke_width=0, fill_color=C_LEG,
                     fill_opacity=1.0).move_to(self.P(*(H + nrm * 7.1))))
        # the needle and the pencil, both ending exactly on their circles' points
        g.add(Line(self.P(*foot_n), self.P(*Pn), color=C_INK, stroke_width=self.w(0.9)))
        g.add(Dot(self.P(*Pn), radius=0.8 * self.k, color=C_INK))
        g.add(quad(foot_p, Pp - dp * 3.6, 3.0, 2.6, C_METAL))
        g.add(quad(Pp - dp * 3.9, Pp - dp * 0.9, 2.7, 2.3, C_AMBER))
        g.add(quad(Pp - dp * 1.1, Pp, 1.9, 0.6, C_INK))
        return g

    def arc(self, N, r, a0, a1, color=C_INK, width=1.15):
        """An arc of the circle about N between page angles a0 and a1 (degrees, y down)."""
        if abs(a1 - a0) < 0.4:
            return VGroup()
        return Arc(radius=r * self.k, start_angle=math.radians(-a0),
                   angle=math.radians(-(a1 - a0)), arc_center=self.P(*N),
                   color=color, stroke_width=self.w(width))

    def span(self, N, r):
        """Cell 1: the opening of the compass, marked with a dashed span and two ticks."""
        Pb = self.polar(N, r, 0.0)
        g = VGroup()
        g.add(DashedLine(self.P(*N), self.P(*Pb), color="#8a8f98", stroke_width=self.w(0.8),
                         dash_length=1.7 * self.k))
        for p in (N, Pb):
            g.add(Line(self.P(p[0], p[1] - 1.8), self.P(p[0], p[1] + 1.8), color=C_INK,
                       stroke_width=self.w(1.0)))
        return g

    def radius(self, N, r):
        """Cell 6: the radius drawn in from the centre to the rim, ticked at both ends."""
        end = (N[0] - r, N[1])
        g = VGroup()
        g.add(Line(self.P(*N), self.P(*end), color=C_INK, stroke_width=self.w(1.3)))
        for p in (N, end):
            g.add(Line(self.P(p[0], p[1] - 1.8), self.P(p[0], p[1] + 1.8), color=C_INK,
                       stroke_width=self.w(1.1)))
        return g

    def ruler(self, N, r):
        """Cell 6: a translucent plastic ruler laid along the radius to measure it.

        The 0 graduation sits on the centre and the 3 cm graduation on the rim, so the
        measured span is exactly the radius (r = 26 pt in this scene); the body runs 3.6 pt
        past the last graduation, the way a real ruler has a margin at its end. The band is
        48 % opaque, so the radius line underneath shows through it, and the graduations and
        digits are printed in ink at the top edge, clear of that line.
        """
        xr = N[0]
        top, bot = N[1] - 7.6, N[1] + 2.0
        far = xr - r - 3.6
        g = VGroup()
        g.add(Polygon(self.P(xr, top), self.P(far, top), self.P(far, bot), self.P(xr, bot),
                      color=C_RULER_EDGE, stroke_width=self.w(0.55), stroke_opacity=0.9,
                      fill_color=C_RULER, fill_opacity=0.48))
        for k in range(7):                       # 0, 0.5, 1 ... 3 cm
            x = xr - k * (r / 6.0)
            major = k % 2 == 0
            g.add(Line(self.P(x, top), self.P(x, top + (2.2 if major else 1.2)),
                       color=C_INK, stroke_width=self.w(0.72 if major else 0.5),
                       stroke_opacity=0.9))
        for k in range(4):
            x = xr - k * (r / 3.0)
            t = Text(str(k), font=CJK, font_size=64, color=C_INK, disable_ligatures=True)
            t.scale(3.0 * self.k / t.height)
            t.move_to(self.P(x - 2.0, top + 4.0))
            g.add(t)
        cap = Text("r = 3 cm", font=CJK, font_size=64, color=C_INK, disable_ligatures=True)
        cap.scale(4.2 * self.k / cap.height)
        cap.move_to(self.P(xr - 9.5, bot + 7.2))
        g.add(cap)
        return g

    # ---------- the film ----------

    def fine(self, i):
        """The finished drawing of cell i, in the order the film builds it.

        The film opens on all six of these (that is the poster, so the reader sees the
        finished comic until they press play), clears them, and builds them again cell by
        cell; the closing frame is therefore this same group in the same order, and the
        poster, the first frame and the last frame are one and the same image.
        """
        N = self.centre(i)
        if i == 0:
            return VGroup(self.compass(N, self.R_C), self.span(N, self.R_C))
        if i == 1:
            return VGroup(self.compass(N, self.R_C),
                          Dot(self.P(*N), radius=1.0 * self.k, color=C_INK))
        if i in (2, 3, 4):
            end = {2: 70.0, 3: 250.0, 4: 360.0}[i]
            return VGroup(self.arc(N, self.R_C, 0.0, end), self.compass(N, self.R_C, end))
        return VGroup(self.arc(N, self.R_C, 0.0, 360.0), self.radius(N, self.R_C),
                      self.ruler(N, self.R_C))

    def construct(self):
        self.add(self.background())
        comic = VGroup(*[self.fine(i) for i in range(6)])
        self.add(comic)
        self.wait(0.40)                          # poster: the finished comic, as printed
        self.play(FadeOut(comic), run_time=0.40)  # clear, then draw it again step by step

        # 1: the compass is opened to the radius
        rg = self.ring(0)
        N = self.centre(0)
        self.play(FadeIn(rg), run_time=0.2)
        tr = ValueTracker(7.0)
        live = always_redraw(lambda: self.compass(N, tr.get_value()))
        self.add(live)
        self.play(tr.animate.set_value(self.R_C), run_time=0.85, rate_func=smooth)
        self.remove(live)
        self.add(self.compass(N, self.R_C))
        self.play(Create(self.span(N, self.R_C)), run_time=0.4)
        self.play(FadeOut(rg), run_time=0.2)
        self.wait(0.25)

        # 2: the needle is set on the centre
        rg = self.ring(1)
        N = self.centre(1)
        dot = Dot(self.P(*N), radius=1.0 * self.k, color=C_INK)
        ripple = Circle(radius=1.6 * self.k, color=C_AMBER, stroke_width=self.w(1.3)).move_to(self.P(*N))
        self.play(FadeIn(rg), run_time=0.2)
        self.play(FadeIn(self.compass(N, self.R_C)), GrowFromCenter(dot), run_time=0.5)
        self.play(ripple.animate.scale(3.4).set_stroke(opacity=0), run_time=0.6)
        self.remove(ripple)
        self.play(FadeOut(rg), run_time=0.2)
        self.wait(0.25)

        # 3-5: the compass turns about the needle, its pencil foot always on the arc's front
        for cell, a_from, a_to, rt, tail in ((2, 0.0, 70.0, 1.05, 0.25),
                                             (3, 70.0, 250.0, 1.35, 0.25),
                                             (4, 250.0, 360.0, 1.15, 0.3)):
            rg = self.ring(cell)
            N = self.centre(cell)
            self.play(FadeIn(rg), run_time=0.2)
            tr = ValueTracker(a_from)
            live = always_redraw(lambda: VGroup(
                self.arc(N, self.R_C, 0.0, tr.get_value()),
                self.compass(N, self.R_C, tr.get_value())))
            self.add(live)
            self.play(tr.animate.set_value(a_to), run_time=rt, rate_func=smooth)
            self.remove(live)
            self.add(self.arc(N, self.R_C, 0.0, a_to), self.compass(N, self.R_C, a_to))
            self.play(FadeOut(rg), run_time=0.2)
            self.wait(tail)

        # 6: the radius is drawn in, then a clear ruler measures it
        rg = self.ring(5)
        N = self.centre(5)
        self.play(FadeIn(rg), run_time=0.2)
        self.play(Create(self.arc(N, self.R_C, 0.0, 360.0)), run_time=0.55)
        self.play(Create(self.radius(N, self.R_C)), run_time=0.55)
        self.wait(0.35)                                   # a beat, then the ruler arrives
        rul = self.ruler(N, self.R_C)
        # start fully outside the region edge so it slides in rather than popping into view
        off = np.array([78.0 * self.k, 0.0, 0.0])
        rul.shift(off)
        self.add(rul)
        self.play(rul.animate.shift(-off), run_time=0.72, rate_func=smooth)
        self.play(FadeOut(rg), run_time=0.2)

        # the finished comic, ruler and reading included, holds; nothing fades to white
        self.wait(1.0)