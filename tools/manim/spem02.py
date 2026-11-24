"""Manim scenes for the spem02 (Electric Circuits) concept panels.

A panel film draws on the printed panel itself: the panel is rendered from the QUE
pdf into the camera frame, the film writes over it in colour, and its last frame is
the printed panel, which becomes the poster. Coordinates are page points (595.3 x
841.9, origin top left) measured on the 3x render of pages/pNN.jpg.

PrintScene mirrors the camera maths of tools/manim/phy06.py so both books' films sit
on their panels the same way (phy06.py is not imported, so nothing there can break
this book).
"""

import json
import math
from pathlib import Path

import fitz
import numpy as np
from manim import (
    Circle, Create, DashedVMobject, Dot, DoubleArrow, FadeIn, FadeOut, Group, ImageMobject,
    Line, Polygon, Rectangle, RoundedRectangle, Scene, Text, VGroup, config,
)

ROOT = Path(__file__).resolve().parents[2]
Z = 5  # pixels per point of the panel render

INK = "#1a1a1a"

# film-deck palette (same as the phy06 panels)
C0 = "#FDFCF8"
C1 = "#F0EBE0"
INK2 = "#22262A"
MUTE = "#5F6C72"
TEAL = "#0C7A6C"
CORAL = "#C4472C"
LIME = "#4F7F16"
AZURE = "#1C6FBB"
RES_FILL = "#D8EED2"     # the printed resistors are a light green slab
RES_EDGE = "#2E7D3A"


class PrintScene(Scene):
    BOOK = "spem02"
    PAGE = 5
    REGION = (24.0, 104.0, 578.0, 266.0)

    def setup(self):
        x0, y0, x1, y1 = self.REGION
        self.k = config.frame_height / (y1 - y0)
        self.c = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.camera.background_color = "#ffffff"
        folder = ROOT / "books" / self.BOOK
        book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
        page = fitz.open(folder / book["source"]["que"])[self.PAGE - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=fitz.Rect(page.rect))
        self.img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n)[:, :, :3].copy()
        self.add(self.crop(*self.REGION))

    def P(self, x, y):
        return np.array([(x - self.c[0]) * self.k, (self.c[1] - y) * self.k, 0.0])

    def w(self, pt):
        return pt * self.k * 100

    def crop(self, x0, y0, x1, y1):
        part = self.img[round(y0 * Z):round(y1 * Z), round(x0 * Z):round(x1 * Z)]
        m = ImageMobject(part)
        m.stretch_to_fit_width((x1 - x0) * self.k).stretch_to_fit_height((y1 - y0) * self.k)
        return m.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2))

    def txt(self, s, size, color, font="Cambria"):
        t = Text(s, color=color, font=font)
        t.scale_to_fit_height(size * self.k * 0.75)
        return t

    def label(self, s, x, y, size=9.0, color=INK2):
        return self.txt(s, size, color).move_to(self.P(x, y)).set_z_index(7)

    def wire(self, *pts, color=INK2, width=1.6, z=3):
        """Polyline through page points."""
        out = VGroup()
        for a, b in zip(pts, pts[1:]):
            out.add(Line(self.P(*a), self.P(*b), color=color, stroke_width=self.w(width)))
        return out.set_z_index(z)

    def res_box(self, cx, cy, w=44.0, h=11.0, label=None, ldy=-11.0):
        """A resistor: the printed ones are a light green slab with a green edge."""
        box = Rectangle(width=w * self.k, height=h * self.k,
                        fill_color=RES_FILL, fill_opacity=1.0,
                        stroke_color=RES_EDGE, stroke_width=self.w(1.3))
        box.move_to(self.P(cx, cy)).set_z_index(4)
        grp = VGroup(box)
        if label:
            grp.add(self.label(label, cx, cy + ldy, 9.0))
        return grp

    def battery(self, x, y0, y1, color=INK2):
        """A cell in a vertical rail: long plate up, short plate down."""
        mid = (y0 + y1) / 2
        grp = VGroup(
            Line(self.P(x, y0), self.P(x, mid - 4.0), color=color, stroke_width=self.w(1.6)),
            Line(self.P(x, mid + 4.0), self.P(x, y1), color=color, stroke_width=self.w(1.6)),
            Line(self.P(x - 9.0, mid - 4.0), self.P(x + 9.0, mid - 4.0),
                 color=color, stroke_width=self.w(2.2)),
            Line(self.P(x - 4.5, mid + 4.0), self.P(x + 4.5, mid + 4.0),
                 color=color, stroke_width=self.w(2.2)),
        )
        return grp.set_z_index(4)

    def wash(self, x0, y0, x1, y1, color=LIME, op=0.14, z=1.5, dash=True):
        """A soft highlighter slab over printed artwork (the print shows through)."""
        r = RoundedRectangle(corner_radius=3.0 * self.k, width=(x1 - x0) * self.k,
                             height=(y1 - y0) * self.k,
                             fill_color=color, fill_opacity=op,
                             stroke_color=color, stroke_opacity=0.55,
                             stroke_width=self.w(1.0))
        r.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(z)
        return r

    def cream_card(self, region=None):
        X0, Y0, X1, Y1 = region or self.REGION
        a = np.array([0xFD, 0xFC, 0xF8])
        b = np.array([0xF0, 0xEB, 0xE0])
        grad = np.zeros((256, 2, 3), dtype=np.uint8)
        for i in range(256):
            f = i / 255.0
            grad[i, :, :] = (a * (1 - f) + b * f).astype(np.uint8)
        card = ImageMobject(grad)
        card.stretch_to_fit_width((X1 - X0) * self.k)
        card.stretch_to_fit_height((Y1 - Y0) * self.k)
        card.move_to(self.P((X0 + X1) / 2, (Y0 + Y1) / 2)).set_z_index(2)
        return card


class ResistorNetwork(PrintScene):
    """A1: the printed series and parallel figures, explained where they stand.

    This film only ever adds highlighter washes and short annotations on top of the
    printed band; it never redraws or replaces a printed figure, and its last frame is
    the print itself.  The formulae are the ones the page already states:
      series    "Current through each resistor in series must be the same."
                V = V1 + V2   (printed under the figure)   and   V is proportional to R
      parallel  "Voltage across each resistor in parallel must be the same."
                I = I1 + I2   (printed in the box)          and   1/R = 1/R1 + 1/R2
                (the box derives V/R = V/R1 + V/R2 first)

    Measured on pages/p05.jpg (3 px per page point):
      title box            x  58.3..182.7   y  71.0..102.0   (outside the region)
      "In series" tab      x  29.0.. 91.3   y 109.0..136.0
      series circuit       x  86.7..272.7   y 138.0..264.0
      "In parallel" tab    x 498.6..572.3   y 107.0..133.0
      parallel circuit     x 346.3..527.0   y 138.0..262.0
      gap between them     x 272.7..346.3   (1 stray ink pixel at y 262, else blank)
      explanation boxes start at y 267.0     (kept out of the region)
      resistors in series  x 107.8..160.4 and 179.7..234.1, y 184.2..194.1
      resistors parallel   x 418.4..467.5, y 181.4..191.3 and 207.1..216.9
    Region (24, 104, 578, 266) = 554 x 162 pt: the 3 pt bands inside its top, left
    and right edges carry no ink, and the lowest ink stops at y 264 (2 pt clear).
    """

    PAGE = 5
    REGION = (24.0, 104.0, 578.0, 266.0)

    SER_WASH = (102.0, 173.0, 240.0, 200.0)     # R1 and R2 of the series figure
    PAR_WASH = (351.0, 176.0, 525.0, 238.0)   # bus to bus, 7.3 pt clear above R1 and below R2     # the two branches of the parallel figure
    GAP_X = 309.5                               # centre of the blank strip between them
    L1, L2, L3 = 155.0, 177.0, 199.0            # the three annotation rows

    def construct(self):
        self.wait(0.4)

        # ------------------------------------------------------------ in series
        ws = self.wash(*self.SER_WASH, color=LIME, op=0.15)
        s1 = self.label("same I", self.GAP_X, self.L1, 9.0, MUTE)
        s2 = self.label("V = V₁ + V₂", self.GAP_X, self.L2, 9.0, MUTE)
        s3 = self.label("V ∝ R", self.GAP_X, self.L3, 9.0, MUTE)
        self.play(FadeIn(ws, run_time=0.6))
        self.play(FadeIn(s1, run_time=0.45))
        self.play(FadeIn(s2, run_time=0.45))
        self.play(FadeIn(s3, run_time=0.45))
        self.wait(0.9)
        self.play(FadeOut(s1, run_time=0.4), FadeOut(s2, run_time=0.4),
                  FadeOut(s3, run_time=0.4), FadeOut(ws, run_time=0.5))

        # ----------------------------------------------------------- in parallel
        wp = self.wash(*self.PAR_WASH, color=AZURE, op=0.15)
        p1 = self.label("same V", self.GAP_X, self.L1, 9.0, MUTE)
        p2 = self.label("I = I₁ + I₂", self.GAP_X, self.L2, 9.0, MUTE)
        p3 = self.label("1/R = 1/R₁ + 1/R₂", self.GAP_X, self.L3, 8.5, MUTE)
        self.play(FadeIn(wp, run_time=0.6))
        self.play(FadeIn(p1, run_time=0.45))
        self.play(FadeIn(p2, run_time=0.45))
        self.play(FadeIn(p3, run_time=0.45))
        self.wait(0.9)
        self.play(FadeOut(p1, run_time=0.4), FadeOut(p2, run_time=0.4),
                  FadeOut(p3, run_time=0.4), FadeOut(wp, run_time=0.5))
        self.wait(0.4)


class InternalResistance(PrintScene):
    """A2: e.m.f. and internal resistance -- V = epsilon - I r.

    The first three beats only highlight what the print already draws: the open circuit
    that reads the e.m.f., the same supply on a lamp where the reading drops, and the
    power-supply inset where the lost volts are marked (so nothing is drawn twice).  The
    fourth beat takes the band over and puts the two cases side by side: the circuit
    (e.m.f., internal resistance r, terminal voltage V) and the V-I line whose intercept
    is the e.m.f. and whose slope is -r.

    Measured on pages/p18.jpg (3 px per page point):
      figure 1  open circuit, reads 12 V      x  62.0..184.3   y 111.7..241.3
      figure 2  12 V, 24 W lamp, reads 8.5 V  x 230.3..354.6   y 111.7..241.3
      figure 3  power-supply inset            x 380.6..572.6   y 112.0..257.3
      label gap between figures 1 and 2       x 184.3..230.3   (ink free)
      blank bands above and below the band    y 105..108 and y 261..264 (ink free)
    Region (56, 108, 578, 261) = 522 x 153 pt: the 3 pt bands inside all four edges
    carry no ink, so no printed line is cut.
    """

    PAGE = 18
    REGION = (56.0, 108.0, 578.0, 261.0)

    # the printed figures, as highlight boxes
    W1 = (58.0, 110.0, 188.0, 244.0)
    W2 = (226.0, 110.0, 358.0, 244.0)
    W3 = (377.0, 110.0, 576.0, 258.0)
    GAP_X = 207.0

    # the card stage: circuit on the left, V-I line on the right
    TOP_Y = 148.0
    BOT_Y = 226.0
    LX = 115.0
    RX = 300.0
    ORIGIN = (352.0, 236.0)
    V_TOP = 132.0
    I_END = 540.0

    def construct(self):
        # ------------------------------------------------ the printed cases
        w1 = self.wash(*self.W1, color=LIME, op=0.15)
        l1 = self.label("V = ε", self.GAP_X, 152.0, 9.5, MUTE)
        self.wait(0.4)
        self.play(FadeIn(w1, run_time=0.6))
        self.play(FadeIn(l1, run_time=0.5))
        self.wait(0.7)

        w2 = self.wash(*self.W2, color=LIME, op=0.15)
        l2 = self.label("V < ε", self.GAP_X, 152.0, 9.5, MUTE)
        self.play(FadeOut(l1, run_time=0.4))
        self.play(FadeIn(w2, run_time=0.6))
        self.play(FadeIn(l2, run_time=0.5))
        self.wait(0.7)

        w3 = self.wash(*self.W3, color=AZURE, op=0.13)
        self.play(FadeOut(l2, run_time=0.4), FadeOut(w1, run_time=0.4),
                  FadeOut(w2, run_time=0.4))
        self.play(FadeIn(w3, run_time=0.7))
        self.wait(1.0)

        # ------------------------------------------------ the card: circuit and line
        card = self.cream_card()
        self.play(FadeOut(w3, run_time=0.4), FadeIn(card, run_time=0.6))

        ty, by, lx, rx = self.TOP_Y, self.BOT_Y, self.LX, self.RX
        mid_y = (ty + by) / 2
        loop = VGroup(
            self.wire((lx, ty), (rx, ty)),
            self.wire((rx, ty), (rx, by)),
            self.wire((rx, by), (lx, by)),
            self.wire((lx, by), (lx, ty)),
        )
        cell = self.battery(lx, ty, by)
        rbox = self.res_box(207.0, ty, label="R", ldy=-12.0)
        supply = DashedVMobject(
            RoundedRectangle(corner_radius=3.0 * self.k, width=30.0 * self.k,
                             height=58.0 * self.k, stroke_color=INK2,
                             stroke_width=self.w(1.2), fill_opacity=0.0),
            num_dashes=20).move_to(self.P(lx, mid_y)).set_z_index(4)
        eps = self.label("ε, r", 85.0, 200.0, 9.5)
        vmark = DoubleArrow(self.P(lx + 30.0, mid_y - 26.0), self.P(lx + 30.0, mid_y + 26.0),
                            color=CORAL, stroke_width=self.w(1.1),
                            tip_length=0.17, buff=0).set_z_index(4)
        vlab = self.label("V", lx + 39.0, mid_y, 9.5, CORAL)
        formula = self.label("V = ε − Ir", 207.0, 246.0, 10.5)

        ox, oy = self.ORIGIN
        axes = VGroup(
            self.wire((ox, oy), (ox, self.V_TOP), width=1.6),
            self.wire((ox, oy), (self.I_END, oy), width=1.6),
        )
        av = self.label("V", ox - 10.0, self.V_TOP - 5.0, 9.5)
        ai = self.label("I", self.I_END + 8.0, oy + 4.0, 9.5)
        line = self.wire((ox, 158.0), (500.0, 212.0), color=AZURE, width=2.2)
        dots = VGroup(Dot(self.P(ox, 158.0), radius=2.6 * self.k, color=AZURE).set_z_index(5),
                      Dot(self.P(440.0, 190.0), radius=2.6 * self.k, color=CORAL).set_z_index(5))
        eps_l = self.label("ε", ox - 11.0, 152.0, 10.0, AZURE)
        slope = self.label("slope = −r", 470.0, 146.0, 9.0, MUTE)

        self.play(Create(loop, run_time=0.9), FadeIn(cell, run_time=0.4))
        self.play(FadeIn(rbox, run_time=0.4), FadeIn(supply, run_time=0.5),
                  FadeIn(eps, run_time=0.4))
        self.play(FadeIn(vmark, run_time=0.4), FadeIn(vlab, run_time=0.3))
        self.wait(0.4)
        self.play(Create(axes, run_time=0.7), FadeIn(av, run_time=0.3),
                  FadeIn(ai, run_time=0.3))
        self.play(Create(line, run_time=0.8), FadeIn(dots, run_time=0.4),
                  FadeIn(eps_l, run_time=0.3))
        self.play(FadeIn(slope, run_time=0.5))
        self.play(FadeIn(formula, run_time=0.6))
        self.wait(1.2)

        # ------------------------------------------------------- hand back the print
        self.play(FadeOut(Group(card, loop, cell, rbox, supply, eps, vmark, vlab,
                                axes, av, ai, line, dots, eps_l, slope, formula),
                          run_time=0.5))
        self.wait(0.3)


class HighlightP2(PrintScene):
    """spem02 p2: four groups of teaching highlights laid over the printed page.

    Nothing is redrawn: each group is a rounded band at alpha 0.30 grown 1.5 pt past the
    printed text bbox, plus one 0.12 wash behind the Ohm's-law box, so the print stays
    fully readable.  The ammeter's A circle and the voltmeter's V circle each give one
    1.5x halo pulse (0.55 s) when their group comes up.  The last frame is the plain print.

    Coordinates come from the book's layout / PDF text layer (not estimated here):
      group 1 amber #B07418  Resistance =  143..195, 116..130
                             Voltage      217..259, 108..121
                             current      217..259, 126..138
                             Unit: Ohms   145..200, 175..193
      group 2 green #2E7D5B  the relationship words, one band per printed word, the phrase
                             runs over two lines and "to" is part of it:
                             directly     307.7..346.7, 267.8..281.0  (line 1, right end)
                             proportional  50.2..115.4, 285.8..299.0  (line 2, left end)
                             to           118.9..128.3, 285.8..299.0  (line 2, its own band)
             amber #B07418  the two quantities, in the same window:
                             voltage       76.1..111.4, 267.8..281.0  (line 1)
                             current      150.1..183.9, 285.8..299.0  (line 2)
                             (the whole-box wash that used to sit behind this group is gone:
                              the user asked for it to be removed, the five word bands stay)
      group 3 coral #C0563F  ammeter.     518..563, 78..92
                             Ammeter ... in series 376..545, 96..110
                             "in series" 506..545 brighter
      group 4 sky   #2C6E9B  voltmeter.   442..488, 278..292
                             in parallel  442..478, 296..310
      A circle centre (441.0, 201.3) r 14.0   V circle centre (522.7, 237.4) r 13.3
    """

    PAGE = 2
    REGION = (40.0, 60.0, 580.0, 330.0)

    AMBER = "#B07418"
    GREEN = "#2E7D5B"
    CORAL = "#C0563F"
    SKY = "#2C6E9B"
    A_C, A_R = (441.0, 201.3), 14.0
    V_C, V_R = (522.7, 237.4), 13.3

    B1 = ((143.0, 116.0, 195.0, 130.0), (217.0, 108.0, 259.0, 121.0),
          (217.0, 126.0, 259.0, 138.0), (145.0, 175.0, 200.0, 193.0))
    # "directly proportional to" is one phrase printed over two lines: three green bands,
    # each on its own word box, so the gap between "proportional" and "to" stays white
    B2_GREEN = ((307.7, 267.8, 346.7, 281.0),
                (50.2, 285.8, 115.4, 299.0),
                (118.9, 285.8, 128.3, 299.0))
    # the two quantities the sentence is about, in amber like group 1
    B2_AMBER = ((76.1, 267.8, 111.4, 281.0),
                (150.1, 285.8, 183.9, 299.0))
    # the old whole-box 0.12 wash (44..300, 255..315) is deliberately NOT drawn any more
    B3 = ((518.0, 78.0, 563.0, 92.0), (376.0, 96.0, 545.0, 110.0))
    B3_HOT = (506.0, 96.0, 545.0, 110.0)
    B4 = ((442.0, 278.0, 488.0, 292.0), (442.0, 296.0, 478.0, 310.0))

    def band(self, b, color, op=0.30):
        x0, y0, x1, y1 = b
        g = 1.5
        r = RoundedRectangle(corner_radius=2.5 * self.k,
                             width=(x1 - x0 + 2 * g) * self.k,
                             height=(y1 - y0 + 2 * g) * self.k,
                             fill_color=color, fill_opacity=op,
                             stroke_color=color, stroke_opacity=0.40,
                             stroke_width=self.w(0.9))
        return r.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(1.5)

    def ring(self, c, r, color):
        return Circle(radius=r * self.k, stroke_color=color, stroke_opacity=0.55,
                      stroke_width=self.w(1.8), fill_opacity=0.0
                      ).move_to(self.P(*c)).set_z_index(1.6)

    def pulse(self, ring):
        self.play(ring.animate.scale(1.5), run_time=0.28)
        self.play(ring.animate.scale(1.0 / 1.5), run_time=0.15)
        self.play(FadeOut(ring), run_time=0.12)

    def construct(self):
        self.wait(0.5)

        # 0.5 - 2.2  group 1: what resistance means
        g1 = Group(*[self.band(b, self.AMBER) for b in self.B1])
        self.play(FadeIn(g1, run_time=0.5))
        self.wait(1.2)

        # 2.2 - 4.0  group 2: Ohm's law. Only the five word bands, no box wash any more.
        g2 = Group(*[self.band(b, self.GREEN) for b in self.B2_GREEN],
                   *[self.band(b, self.AMBER) for b in self.B2_AMBER])
        self.play(FadeIn(g2, run_time=0.5))
        self.wait(1.3)

        # 4.0 - 6.0  group 3: the ammeter, then a pulse on its A circle
        g3 = Group(*[self.band(b, self.CORAL) for b in self.B3],
                   self.band(self.B3_HOT, self.CORAL, 0.55))
        self.play(FadeIn(g3, run_time=0.5))
        self.pulse(self.ring(self.A_C, self.A_R, self.CORAL))
        self.wait(0.95)

        # 6.0 - 8.0  group 4: the voltmeter, then a pulse on its V circle
        g4 = Group(*[self.band(b, self.SKY) for b in self.B4])
        self.play(FadeIn(g4, run_time=0.5))
        self.pulse(self.ring(self.V_C, self.V_R, self.SKY))
        self.wait(0.95)

        # 8.0 - 9.0  everything fades, 9.0 - 10.0 the printed page alone
        self.play(FadeOut(Group(g1, g2, g3, g4)), run_time=1.0)
        self.wait(1.0)
