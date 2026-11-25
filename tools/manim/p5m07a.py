"""Manim film for the p5m07a concept page (page 2 of the PDF, printed as page 1).

The printed page already shows the four names with boxes and arrows; this film adds the
teaching motion the user asked for without repainting anything printed: it holds the printed
region as the base layer, fades it out, draws the same circle again cleanly in the page's own
colours, names the four parts one at a time (bilingual, as the widgets do), turns the radius
into the diameter by laying a second radius beside it (diameter = 2 x radius), and finally
shows a shorter parallel line inside the circle so "the diameter is the longest straight line"
is something you can see. It then fades the printed region back in, so the poster (last frame)
is the printed page exactly.

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

from manim import (
    Arc, CapStyleType, Circle, Create, Dot, FadeIn, FadeOut, Line, NORMAL, Polygon, Text, VGroup, Write,
)

from jpfm08 import PageFilm

ORANGE = "#ef9a33"
RED = "#e0453a"
GREEN = "#8cc63f"
BLUE = "#2f6fd6"
INK = "#1a1a1a"
GREY = "#8a8f98"
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
        self.wait(0.8)
        self.play(FadeOut(base), run_time=0.6)

        circle = Circle(radius=self.R * self.k, color=ORANGE, stroke_width=self.w(2.2)).move_to(self.P(*self.C))
        self.play(Create(circle), run_time=1.4)

        # 1. the circumference: a bold run of the rim where the name points
        a0, a1 = 196, 236
        arc = Arc(radius=self.R * self.k, start_angle=-math.radians(a0), angle=-math.radians(a1 - a0),
                  arc_center=self.P(*self.C), color=ORANGE, stroke_width=self.w(5))
        arc.set_cap_style(CapStyleType.ROUND)
        cap = self.word("圓周 Circumference", 103, 219, 9.6, ORANGE)
        lead = self.arrow(self.pt(a0 - 4, self.R + 26), self.pt((a0 + a1) / 2 - 3), ORANGE)
        self.play(Create(arc), FadeIn(cap), Create(lead), run_time=1.3)

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

        # 6. the diameter is the longest straight line inside the circle
        shorter = self.line((self.C[0] + 40, self.C[1] - 44), (self.C[0] + 40, self.C[1] + 44), GREY, width=1.8)
        note2 = self.word("直徑是圓內最長的直線", self.C[0], 339, 8.6, INK)
        self.play(FadeOut(note), Create(shorter), run_time=0.8)
        self.play(Write(note2), run_time=1.1)
        self.wait(1.0)

        # 7. back to the printed page, so the poster is the page itself
        drawn = VGroup(circle, arc, cap, lead, dot, cap2, lead2, rad, cap3, lead3, dia, cap4, lead4,
                       rad2, shorter, note2)
        self.play(FadeOut(drawn), run_time=0.45)
        self.play(FadeIn(base), run_time=0.45)
        self.wait(0.5)
