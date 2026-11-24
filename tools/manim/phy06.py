"""Manim scenes for the phy06-force2 concept panels.

A panel film draws on the printed panel itself: the panel is rendered from the QUE
pdf into the camera frame, the film writes over it in colour, and its last frame is
the printed panel, which becomes the poster. Coordinates are page points (595 x 842,
origin top left) measured on the 3x render of pages/pNN.jpg.

PrintScene mirrors the camera maths of tools/manim/phy11.py so that both books' films
sit on their panels the same way (phy11.py is not imported, so nothing there can
break this book).
"""

import json
import math
from pathlib import Path

import fitz
import numpy as np
from manim import (
    Arc, Arrow, Circle, Create, DashedLine, Group, RIGHT, FadeIn, FadeOut, ImageMobject, Line, Polygon, RoundedRectangle, Scene, Text, ValueTracker,
    VGroup, always_redraw, config, linear,
)

ROOT = Path(__file__).resolve().parents[2]
Z = 5  # pixels per point of the panel render

INK = "#1a1a1a"
BLUE = "#1f4fff"
GREEN = "#1d8a4a"
AMBER = "#f0a030"
RED = "#d02a2a"
GREY = "#8a8f98"


class PrintScene(Scene):
    BOOK = "phy06-force2"
    PAGE = 1
    REGION = (46.1, 104.0, 572.4, 279.3)

    def setup(self):
        x0, y0, x1, y1 = self.REGION
        self.k = config.frame_height / (y1 - y0)
        self.c = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.camera.background_color = "#ffffff"
        folder = ROOT / "books" / self.BOOK
        book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
        page = fitz.open(folder / book["source"]["que"])[self.PAGE - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=fitz.Rect(page.rect))
        self.img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].copy()
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

    def label(self, s, color=INK, size=11):
        t = Text(s, color=color)
        t.scale_to_fit_height(size * self.k * 0.75)
        return t.set_z_index(6)

    # ---- film-deck helpers (Cine, Inclined-Plane-Narrated-v22, palette A) ----
    C0 = "#FDFCF8"; C1 = "#F0EBE0"
    WEDGE_A = "#E8E1D4"; WEDGE_EDGE = "#6E6048"; HATCH = "#786950"
    INK2 = "#22262A"; MUTE = "#5F6C72"
    AMBER = "#A96B0F"; AMBER_TXT = "#8A5200"; TEAL = "#0C7A6C"; CORAL = "#C4472C"; LIME = "#4F7F16"; AZURE = "#1C6FBB"

    def txt(self, s, size, color, font="Cambria"):
        t = Text(s, color=color, font=font)
        t.scale_to_fit_height(size * self.k * 0.75)
        return t

    def chip(self, x, y, s, color, size=8.0):
        t = self.txt(s, size, color)
        w_pt = t.width / self.k + 6.0
        h_pt = size * 0.75 + 4.0
        r = RoundedRectangle(corner_radius=2.0 * self.k, width=w_pt * self.k,
                             height=h_pt * self.k, fill_color=self.C0,
                             fill_opacity=0.94, stroke_color=color,
                             stroke_width=self.w(1.0))
        return VGroup(r, t).move_to(self.P(x, y)).set_z_index(7)

    def arrow(self, p0, p1, color, width=3.0, head=7.5, headw=3.8, z=5):
        x0, y0 = p0; x1, y1 = p1
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        bx, by = x1 - ux * head, y1 - uy * head
        line = Line(self.P(x0, y0), self.P(bx, by), color=color, stroke_width=self.w(width))
        tri = Polygon(self.P(bx + nx * headw, by + ny * headw),
                      self.P(bx - nx * headw, by - ny * headw),
                      self.P(x1, y1), fill_color=color, fill_opacity=1.0, stroke_width=0)
        return VGroup(line, tri).set_z_index(z)

    def hatch(self, pts, spacing=5.0, angle=45.0, width=0.55, opacity=0.13):
        th = math.radians(angle)
        d = (math.cos(th), -math.sin(th))
        n = (-d[1], d[0])
        proj = [p[0] * n[0] + p[1] * n[1] for p in pts]
        lo, hi = min(proj), max(proj)
        out = VGroup()
        s = lo
        while s <= hi:
            ts = []
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                da = a[0] * n[0] + a[1] * n[1] - s
                db = b[0] * n[0] + b[1] * n[1] - s
                if da == db:
                    continue
                if (da <= 0 < db) or (db <= 0 < da):
                    k = da / (da - db)
                    ts.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            if len(ts) >= 2:
                out.add(Line(self.P(*ts[0]), self.P(*ts[1]), color=self.HATCH,
                             stroke_width=self.w(width), stroke_opacity=opacity))
            s += spacing
        return out.set_z_index(3)

    def cream_card(self, region=None):
        X0, Y0, X1, Y1 = region or self.REGION
        c0 = np.array([0xFD, 0xFC, 0xF8]); c1 = np.array([0xF0, 0xEB, 0xE0])
        grad = np.zeros((256, 2, 3), dtype=np.uint8)
        for i in range(256):
            f = i / 255.0
            grad[i, :, :] = (c0 * (1 - f) + c1 * f).astype(np.uint8)
        card = ImageMobject(grad)
        card.stretch_to_fit_width((X1 - X0) * self.k)
        card.stretch_to_fit_height((Y1 - Y0) * self.k)
        card.move_to(self.P((X0 + X1) / 2, (Y0 + Y1) / 2)).set_z_index(2)
        return card


class ResolveForce(PrintScene):
    """p1 "Resolution of force": F is split into F cos θ across and F sin θ up.

    Measured on pages/p01.jpg (3 px per page point); every overlay below sits on the
    printed line it explains:
      * printed arrow     (396.08, 229.12) -> (494.53, 151.53): 125.35 pt at 38.25簞
      * horizontal guide  y = 228.7, x 396.1 -> 494.6 (arrowhead at the right)
      * vertical guide    x = 396.3, y 229.1 -> 151.3 (arrowhead at the top)
    Printed marks the film must leave readable: "F" (496-503, 140-148), "F_y"
    (397-407, 138-147), "F_x" (497-506, 217-226), the grey captions "vertical
    component" (358-395, 139-159) and "horizontal component" (513-560, 216-239), and
    the θ arc at the origin.

    The film fills the printed arrow and then both printed guides with colour, and
    then turns the same-length F up to 60簞: F cos θ and F sin θ trade sizes
    (98.4 / 77.6 pt -> 62.7 / 108.5 pt), so the total stays and only the split moves.
    No number that the panel does not print is written on it.
    """

    PAGE = 1
    REGION = (46.1, 104.0, 572.4, 279.3)

    O = (396.08, 229.12)
    LEN = 125.35      # pt, the printed arrow's length, kept through the turn
    THETA = 38.25     # deg, the printed arrow's angle above the horizontal
    TURN = 60.0       # deg, the angle the film turns it to

    def construct(self):
        O = self.P(*self.O)
        k, L = self.k, self.LEN
        th = ValueTracker(self.THETA)
        s_f = ValueTracker(0.0)   # how much of F has been drawn
        s_c = ValueTracker(0.0)   # how much of the two components has been drawn

        def pv(dx, dy):
            """displacement in page points, +y upward (as the figure reads) -> manim"""
            return np.array([dx * k, dy * k, 0.0])

        def c_end():
            a = math.radians(th.get_value())
            return pv(L * math.cos(a), L * math.sin(a)) * s_c.get_value()

        def f_end():
            a = math.radians(th.get_value())
            return O + pv(L * math.cos(a), L * math.sin(a)) * s_f.get_value()

        def arrow(start, end, color, width, tip):
            if np.linalg.norm(end - start) < 1e-3:
                end = start + np.array([1e-3, -1e-3, 0.0])
            return Arrow(start, end, buff=0, color=color,
                         stroke_width=self.w(width), tip_length=tip * k)

        F = always_redraw(lambda: arrow(O, f_end(), BLUE, 3.0, 9).set_z_index(3.2))
        Fx = always_redraw(lambda: arrow(O, O + np.array([c_end()[0], 0.0, 0.0]), GREEN, 2.6, 7.5).set_z_index(3.0))
        Fy = always_redraw(lambda: arrow(O, O + np.array([0.0, c_end()[1], 0.0]), AMBER, 2.6, 7.5).set_z_index(3.0))

        lab_x = self.label("F cos θ", GREEN, 11)
        lab_y = self.label("F sin θ", AMBER, 11)

        def up_x(m):
            m.move_to(O + np.array([c_end()[0] / 2, -12 * k, 0.0]))

        def up_y(m):
            m.move_to(O + np.array([0.0, c_end()[1] / 2, 0.0]))
            m.shift(np.array([-(m.width / 2) - 8 * k, 0.0, 0.0]))

        lab_x.add_updater(up_x)
        lab_y.add_updater(up_y)

        # 1) the printed panel
        self.add(Fx, Fy, F)
        self.wait(0.5)
        # 2) F leaves the origin along the printed arrow
        self.play(s_f.animate.set_value(1.0), run_time=1.0, rate_func=linear)
        self.wait(0.4)
        # 3) both components grow along the printed guides
        self.play(s_c.animate.set_value(1.0), run_time=0.9, rate_func=linear)
        self.wait(0.5)
        # 4) the recipe for each component
        self.play(FadeIn(lab_x), FadeIn(lab_y), run_time=0.6)
        self.wait(0.8)
        # 5) the same F, a steeper angle: one component trades size with the other
        self.play(th.animate.set_value(self.TURN), run_time=2.0, rate_func=linear)
        self.wait(1.0)
        self.play(th.animate.set_value(self.THETA), run_time=0.9, rate_func=linear)
        # 6) hand the panel back to the print
        self.play(FadeOut(lab_x), FadeOut(lab_y), run_time=0.4)
        self.play(s_c.animate.set_value(0.0), s_f.animate.set_value(0.0), run_time=0.7)
        self.remove(F, Fx, Fy)
        self.wait(0.4)


class SmoothIncline(PrintScene):
    """p6 "Motion along a smooth inclined plane": the two printed figures only.

    The film touches nothing but the two small figures on the right of the panel (the
    area the teacher ringed in red): a cream card covers that block, the incline is drawn
    again **running down to the right** (the printed one runs up to the right), and the
    block slides a long way down and then climbs back to the height it started from, with
    v following the motion and a always pointing down the plane. The angle theta is drawn
    on the slope. The print comes back at the end, so the poster stays the printed panel.

    Region was measured on pages/p06.jpg: the text ends at x 388, the figures start at
    x 402, so the card edge sits at 394 and clips neither.

    Copy deck from Cine's Inclined-Plane-Narrated-v22 (film-theme.html, palette A).
    """

    PAGE = 6
    REGION = (394.0, 258.0, 576.0, 456.5)

    # palette (film-theme.html, PAL.A)
    C0 = "#FDFCF8"; C1 = "#F0EBE0"
    WEDGE_A = "#E8E1D4"; WEDGE_EDGE = "#6E6048"; HATCH = "#786950"
    INK2 = "#22262A"; MUTE = "#5F6C72"
    AMBER = "#A96B0F"; AMBER_TXT = "#8A5200"; TEAL = "#0C7A6C"; CORAL = "#C4472C"; LIME = "#4F7F16"; AZURE = "#1C6FBB"

    # geometry, page pt: the incline runs DOWN to the right
    GROUND = 440.0
    TOP_L = (402.0, 440.0)          # foot of the high (left) end
    BOT_R = (566.0, 440.0)          # foot of the low (right) end
    THETA = 30.0
    BLOCK_S = 22.0
    D_TOP = 34.0                    # start, measured from the top vertex down the slope
    D_LOW = 118.0                   # the far end of the slide down

    # ---------------------------------------------------------------- helpers
    def txt(self, s, size, color, font="Cambria"):
        t = Text(s, color=color, font=font)
        t.scale_to_fit_height(size * self.k * 0.75)
        return t

    def chip(self, x, y, s, color, size=8.0):
        t = self.txt(s, size, color)
        w_pt = t.width / self.k + 6.0
        h_pt = size * 0.75 + 4.0
        r = RoundedRectangle(corner_radius=2.0 * self.k, width=w_pt * self.k,
                             height=h_pt * self.k, fill_color=self.C0,
                             fill_opacity=0.94, stroke_color=color,
                             stroke_width=self.w(1.0))
        return VGroup(r, t).move_to(self.P(x, y)).set_z_index(7)

    def arrow(self, p0, p1, color, width=3.0, head=7.5, headw=3.9, z=5):
        x0, y0 = p0; x1, y1 = p1
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        bx, by = x1 - ux * head, y1 - uy * head
        line = Line(self.P(x0, y0), self.P(bx, by), color=color,
                    stroke_width=self.w(width))
        tri = Polygon(self.P(bx + nx * headw, by + ny * headw),
                      self.P(bx - nx * headw, by - ny * headw),
                      self.P(x1, y1), fill_color=color, fill_opacity=1.0,
                      stroke_width=0)
        return VGroup(line, tri).set_z_index(z)

    def hatch(self, pts, spacing=5.0, angle=45.0, width=0.55, opacity=0.13):
        th = math.radians(angle)
        d = (math.cos(th), -math.sin(th))
        n = (-d[1], d[0])
        proj = [p[0] * n[0] + p[1] * n[1] for p in pts]
        lo, hi = min(proj), max(proj)
        out = VGroup()
        s = lo
        while s <= hi:
            ts = []
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                da = a[0] * n[0] + a[1] * n[1] - s
                db = b[0] * n[0] + b[1] * n[1] - s
                if da == db:
                    continue
                if (da <= 0 < db) or (db <= 0 < da):
                    k = da / (da - db)
                    ts.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            if len(ts) >= 2:
                out.add(Line(self.P(*ts[0]), self.P(*ts[-1]), color=self.HATCH,
                             stroke_width=self.w(width), stroke_opacity=opacity))
            s += spacing
        return out.set_z_index(3)

    # ---------------------------------------------------------------- scene
    def construct(self):
        X0, Y0, X1, Y1 = self.REGION
        th = math.radians(self.THETA)
        rise = (self.BOT_R[0] - self.TOP_L[0]) * math.tan(th)
        apex = (self.TOP_L[0], self.GROUND - rise)
        ud = (math.cos(th), math.sin(th))          # down the slope (to the right)
        nn = (math.sin(th), -math.cos(th))         # out of the slope (up-right)

        # cream ground
        c0 = np.array([0xFD, 0xFC, 0xF8]); c1 = np.array([0xF0, 0xEB, 0xE0])
        grad = np.zeros((256, 2, 3), dtype=np.uint8)
        for i in range(256):
            f = i / 255.0
            grad[i, :, :] = (c0 * (1 - f) + c1 * f).astype(np.uint8)
        card = ImageMobject(grad)
        card.stretch_to_fit_width((X1 - X0) * self.k)
        card.stretch_to_fit_height((Y1 - Y0) * self.k)
        card.move_to(self.P((X0 + X1) / 2, (Y0 + Y1) / 2)).set_z_index(2)

        wedge_pts = [apex, (self.TOP_L[0], self.GROUND), self.BOT_R]
        wedge = Polygon(*[self.P(*p) for p in wedge_pts],
                        fill_color=self.WEDGE_A, fill_opacity=0.96,
                        stroke_color=self.WEDGE_EDGE,
                        stroke_width=self.w(1.3)).set_z_index(3)
        hatch = self.hatch(wedge_pts)
        ground = VGroup(
            Line(self.P(398.0, self.GROUND), self.P(572.0, self.GROUND),
                 color=self.WEDGE_EDGE, stroke_width=self.w(1.3)),
            *[Line(self.P(x, self.GROUND), self.P(x - 5.0, self.GROUND + 8.0),
                   color=self.WEDGE_EDGE, stroke_width=self.w(0.8),
                   stroke_opacity=0.32)
              for x in [404.0 + n * 12.0 for n in range(14)]],
        ).set_z_index(3.05)

        # the angle theta, at the corner where the plane meets the ground
        corner = self.P(*self.BOT_R)
        arc = Arc(radius=17.0 * self.k, start_angle=math.radians(180.0 - self.THETA),
                  angle=math.radians(self.THETA), color=self.WEDGE_EDGE,
                  stroke_width=self.w(1.1)).move_arc_center_to(corner).set_z_index(6)
        mid = math.radians(180.0 - self.THETA / 2.0)
        theta_lbl = self.txt("θ", 8.2, self.WEDGE_EDGE).move_to(
            corner + np.array([math.cos(mid), math.sin(mid), 0.0]) * 26.0 * self.k).set_z_index(6)

        def block_at(d):
            foot = (apex[0] + ud[0] * d, apex[1] + ud[1] * d)
            half = self.BLOCK_S / 2
            cen = (foot[0] + nn[0] * half, foot[1] + nn[1] * half)
            corners = []
            for su, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                corners.append((cen[0] + su * half * ud[0] + sn * half * nn[0],
                                cen[1] + su * half * ud[1] + sn * half * nn[1]))
            body = Polygon(*[self.P(*p) for p in corners],
                           fill_color="#FFFFFF", fill_opacity=0.98,
                           stroke_color=self.INK2, stroke_width=self.w(1.2)).set_z_index(4)
            s0, s1 = -0.40 * half, 0.40 * half
            stripe = Polygon(
                self.P(cen[0] + s0 * ud[0] + 0.30 * half * nn[0], cen[1] + s0 * ud[1] + 0.30 * half * nn[1]),
                self.P(cen[0] + s1 * ud[0] + 0.30 * half * nn[0], cen[1] + s1 * ud[1] + 0.30 * half * nn[1]),
                self.P(cen[0] + s1 * ud[0] - 0.02 * half * nn[0], cen[1] + s1 * ud[1] - 0.02 * half * nn[1]),
                self.P(cen[0] + s0 * ud[0] - 0.02 * half * nn[0], cen[1] + s0 * ud[1] - 0.02 * half * nn[1]),
                fill_color=self.AMBER, fill_opacity=0.42, stroke_width=0).set_z_index(4.2)
            body.add(stripe)
            return body, cen

        block, cen = block_at(self.D_TOP)

        def v_and_chip(cen, up):
            """v sits above the block, parallel to the plane, as the print draws it."""
            lift = self.BLOCK_S / 2 + 9.0
            d = (-ud[0], -ud[1]) if up else (ud[0], ud[1])
            tail = (cen[0] + nn[0] * lift + d[0] * -13.0, cen[1] + nn[1] * lift + d[1] * -13.0)
            tip = (tail[0] + d[0] * 30.0, tail[1] + d[1] * 30.0)
            arr = self.arrow(tail, tip, self.TEAL)
            ch = self.chip(tail[0] - d[0] * 8.0 + nn[0] * 9.0,
                           tail[1] - d[1] * 8.0 + nn[1] * 9.0, "v", self.TEAL)
            return arr, ch

        a0 = cen
        a1 = (cen[0] + ud[0] * 26.0, cen[1] + ud[1] * 26.0)
        a_arrow = self.arrow(a0, a1, self.CORAL)
        c_a = self.chip(a1[0] + ud[0] * 10.0 + nn[0] * 7.0, a1[1] + ud[1] * 10.0 + nn[1] * 7.0, "a", self.CORAL)

        v_dn, c_vd = v_and_chip(cen, False)
        cap1 = self.txt("moving down \u00b7 a down the plane", 7.4, self.INK2)
        cap1.move_to(self.P(485.0, 278.0)).set_z_index(6)
        cap2 = self.txt("moving up \u00b7 a still down", 7.4, self.INK2)
        cap2.move_to(self.P(485.0, 278.0)).set_z_index(6)

        drop = np.array([ud[0], -ud[1], 0.0]) * (self.D_LOW - self.D_TOP) * self.k
        back = -drop

        # ------------------------------------------------------------ timeline
        self.wait(0.5)
        self.play(FadeIn(card), run_time=0.6)
        self.play(Create(wedge), Create(ground), run_time=0.7)
        self.play(FadeIn(hatch), run_time=0.4)
        self.play(Create(arc), FadeIn(theta_lbl), run_time=0.5)
        self.play(FadeIn(block), run_time=0.4)
        self.play(FadeIn(v_dn), FadeIn(c_vd), FadeIn(a_arrow), FadeIn(c_a), run_time=0.6)
        self.play(FadeIn(cap1), run_time=0.5)
        self.wait(0.3)

        # a long slide down the plane
        rider = VGroup(block, v_dn, c_vd, a_arrow, c_a)
        self.play(rider.animate.shift(drop), run_time=1.8)
        self.wait(0.4)

        # turn round and climb back to the height it started from: v flips, a does not
        cen2 = (cen[0] + ud[0] * (self.D_LOW - self.D_TOP),
                cen[1] + ud[1] * (self.D_LOW - self.D_TOP))
        v_up, c_vu = v_and_chip(cen2, True)
        self.play(FadeOut(v_dn), FadeOut(c_vd), FadeIn(v_up), FadeIn(c_vu), run_time=0.5)
        self.play(FadeOut(cap1), FadeIn(cap2), run_time=0.4)
        rider2 = VGroup(block, v_up, c_vu, a_arrow, c_a)
        self.play(rider2.animate.shift(back), run_time=2.2)
        self.wait(0.7)

        self.play(FadeOut(Group(card, wedge, ground, hatch, arc, theta_lbl, block,
                                v_up, c_vu, a_arrow, c_a, cap2)), run_time=0.45)
        self.wait(0.3)


class RoughIncline(PrintScene):
    """p6 "Motion along a rough inclined plane": the two printed figures, redrawn.

    The inclines keep the printed orientation (rising to the right, theta at the lower
    left corner) and are placed on the measured print, so the card can hand the panel
    back without a jump. The block is a square turned by theta with its lower face on
    the plane, so it moves along the plane and not just across it:
        1  block climbs a little  ->  a1  ->  mg sin theta  ->  f  ->  the equation
        2  a2  ->  mg sin theta  ->  f  ->  block slides back down  ->  the equation
    v sits above the block and follows the motion; mg sin theta leaves the block's centre
    and runs down the plane; f leaves the contact face at the end it points away from,
    so it hugs the plane beside the block rather than crossing it.

    Measured on pages/p06.jpg (3 px per page point):
      left  triangle  (75.7, 619.1) (278.2, 619.1) apex (278.2, 552.8)   18.16 deg
      right triangle  (330.7, 619.1) (532.0, 619.1) apex (532.0, 549.7)  19.02 deg
      equations       ink y 632..647
    """

    PAGE = 6
    REGION = (46.0, 514.0, 575.0, 652.0)

    LEFT = ((75.7, 619.1), (278.2, 619.1), (278.2, 552.8))
    RIGHT = ((330.7, 619.1), (532.0, 619.1), (532.0, 549.7))
    BLOCK_S = 30.0
    BLOCK_AT = 0.62          # centre of the resting face, as a fraction along the base
    GLIDE = 22.0             # how far the block slides along the plane (page points)

    def one_figure(self, tri, moving_up, a_label, a_color, eq_text, eq_x, eq_y):
        (bl, br, apex) = tri
        th = math.atan2(bl[1] - apex[1], br[0] - bl[0])     # the plane rises to the right
        up = (math.cos(th), -math.sin(th))                  # along the plane, uphill
        down = (-math.cos(th), math.sin(th))                # along the plane, downhill
        out = (-math.sin(th), -math.cos(th))                # away from the wedge, above the plane
        S = self.BLOCK_S

        wedge = Polygon(self.P(*bl), self.P(*br), self.P(*apex),
                        fill_color=self.WEDGE_A, fill_opacity=0.96,
                        stroke_color=self.WEDGE_EDGE, stroke_width=self.w(1.2)).set_z_index(3)
        hatch = self.hatch([bl, br, apex], spacing=5.0)
        arc = Arc(radius=18.0 * self.k, start_angle=0, angle=th,
                  color=self.WEDGE_EDGE, stroke_width=self.w(1.0)
                  ).move_arc_center_to(self.P(*bl)).set_z_index(6)
        theta_lbl = self.txt("θ", 8.4, self.WEDGE_EDGE).move_to(
            self.P(bl[0] + 28.0 * math.cos(th / 2), bl[1] - 28.0 * math.sin(th / 2))).set_z_index(6)

        # the block lies on the plane: a square turned by theta, its lower face on the surface
        w = br[0] - bl[0]
        x_r = bl[0] + self.BLOCK_AT * w
        surf_r = bl[1] - (x_r - bl[0]) * math.tan(th)
        contact = (x_r, surf_r)                 # centre of the face resting on the plane
        half = S / 2
        cx = contact[0] + out[0] * half
        cy = contact[1] + out[1] * half

        def bc(su, so):
            """block corner: su along the plane (+ uphill), so away from the plane."""
            return (cx + up[0] * su * half + out[0] * so * half,
                    cy + up[1] * su * half + out[1] * so * half)

        block = Polygon(self.P(*bc(-1, -1)), self.P(*bc(1, -1)),
                        self.P(*bc(1, 1)), self.P(*bc(-1, 1)),
                        fill_color="#FFFFFF", fill_opacity=0.98,
                        stroke_color=self.INK2, stroke_width=self.w(1.2)).set_z_index(4)
        top_mid = (cx + out[0] * half, cy + out[1] * half)

        # v above the block, along the motion
        md = up if moving_up else down
        v0 = (top_mid[0] + out[0] * 7.0 - md[0] * 6.0,
              top_mid[1] + out[1] * 7.0 - md[1] * 6.0)
        v_tip = (v0[0] + md[0] * 40.0, v0[1] + md[1] * 40.0)
        v_arrow = self.arrow(v0, v_tip, self.TEAL, width=2.6, head=6.6, headw=3.4)
        v_txt = self.txt("v", 9.0, self.TEAL).move_to(
            self.P(v0[0] - md[0] * 8.0 + 1.0, v0[1] - md[1] * 8.0 - 8.0)).set_z_index(7)

        # a: a separate arrow up the page, parallel to the plane, always downhill
        a_tail = (cx - up[0] * (half + 30.0) + out[0] * (half + 7.0),
                  cy - up[1] * (half + 30.0) + out[1] * (half + 7.0))
        a_tip = (a_tail[0] + down[0] * 34.0, a_tail[1] + down[1] * 34.0)
        a_arrow = self.arrow(a_tail, a_tip, a_color, width=3.0, head=10.5, headw=4.6)
        a_txt = self.txt(a_label, 10.0, a_color).move_to(
            self.P(a_tail[0] - up[0] * 7.0, a_tail[1] - up[1] * 7.0 - 13.0)).set_z_index(7)

        # mg sin theta: out of the block's centre, down the plane
        m_tip = (cx + down[0] * 58.0, cy + down[1] * 58.0)
        mg = self.arrow((cx, cy), m_tip, self.CORAL, width=3.2, head=8.0, headw=4.0)
        mg_txt = self.txt("mg sin θ", 9.0, self.CORAL).move_to(
            self.P(m_tip[0] + down[0] * 24.0 - 4.0, m_tip[1] + down[1] * 24.0 + 6.0)).set_z_index(7)

        # f: hugging the plane beside the block, always against the motion, drawn from
        # the end of the contact face it points away from so it never crosses the block
        fd = down if moving_up else up
        foot = (contact[0] + fd[0] * half, contact[1] + fd[1] * half)
        f0 = (foot[0] + out[0] * 3.0, foot[1] + out[1] * 3.0)
        f1 = (f0[0] + fd[0] * 34.0, f0[1] + fd[1] * 34.0)
        fr = self.arrow(f0, f1, self.AMBER_TXT, width=2.6, head=6.4, headw=3.2)
        f_mid = ((f0[0] + f1[0]) / 2, (f0[1] + f1[1]) / 2)
        f_txt = self.txt("f", 10.0, self.AMBER_TXT).move_to(
            self.P(f_mid[0] - out[0] * 12.0, f_mid[1] - out[1] * 12.0)).set_z_index(7)

        # d: the printed equation, rewritten and then underlined
        eq = self.txt(eq_text, 9.8, self.INK2).move_to(self.P(eq_x, eq_y)).set_z_index(7)
        half_w = eq.width / self.k / 2 + 3.0
        rule = Line(self.P(eq_x - half_w, eq_y + 8.4), self.P(eq_x + half_w, eq_y + 8.4),
                    color=self.INK2, stroke_width=self.w(1.6)).set_z_index(7)

        static = VGroup(wedge, hatch, arc, theta_lbl)
        # the block and the things pinned to it are their own group, so they can travel
        # along the plane without being owned twice; forces stay a plain list
        atom = VGroup(block, v_arrow, v_txt)
        forces = [a_arrow, a_txt, mg, mg_txt, fr, f_txt]
        # a displacement in page points goes through P() like every other coordinate,
        # so the frame's flipped y is handled once, here
        glide = (self.P(up[0] * self.GLIDE, up[1] * self.GLIDE) - self.P(0.0, 0.0))
        # both figures move the same way: drawn where it ends up, entering from the far end
        shift = glide if moving_up else -glide
        atom.shift(-shift)
        return (static, atom, forces, [a_arrow, a_txt], [mg, mg_txt], [fr, f_txt],
                [eq, rule], shift)

    def construct(self):
        card = self.cream_card()
        ground = VGroup(
            Line(self.P(64.0, 619.1), self.P(566.0, 619.1), color=self.WEDGE_EDGE,
                 stroke_width=self.w(1.2)),
            *[Line(self.P(x, 619.1), self.P(x - 4.0, 619.1 + 7.0), color=self.WEDGE_EDGE,
                   stroke_width=self.w(0.7), stroke_opacity=0.30)
              for x in [70.0 + n * 11.0 for n in range(45)]],
        ).set_z_index(3.05)

        L_static, L_atom, L_forces, L_a, L_mg, L_f, L_eq, L_shift = self.one_figure(
            self.LEFT, True, "a₁", self.CORAL, "mg sin θ + f = m a₁", 186.0, 641.0)
        R_static, R_atom, R_forces, R_a, R_mg, R_f, R_eq, R_shift = self.one_figure(
            self.RIGHT, False, "a₂", self.AZURE, "mg sin θ - f = m a₂", 442.0, 641.0)

        self.wait(0.5)
        self.play(FadeIn(card), run_time=0.6)
        self.play(FadeIn(L_static), FadeIn(R_static), FadeIn(L_atom), FadeIn(R_atom),
                  Create(ground), run_time=0.8)
        self.wait(0.3)

        # left: it climbs a little first, so v is seen to be the motion, then the forces,
        # and only then the equation the forces add up to
        self.play(L_atom.animate.shift(L_shift), run_time=1.2)
        self.wait(0.2)
        for part in (L_a, L_mg, L_f):
            self.play(*[FadeIn(m) for m in part], run_time=0.7)
            self.wait(0.25)
        self.wait(0.3)
        self.play(*[FadeIn(m) for m in L_eq], run_time=0.7)
        self.wait(0.5)

        # right, in the same order: it slides down the same plane first, then the forces
        # are named where it has come to rest (f turns round with the motion), then the
        # equation closes the figure
        self.play(R_atom.animate.shift(R_shift), run_time=1.2)
        self.wait(0.2)
        for part in (R_a, R_mg, R_f):
            self.play(*[FadeIn(m) for m in part], run_time=0.7)
            self.wait(0.25)
        self.wait(0.3)
        self.play(*[FadeIn(m) for m in R_eq], run_time=0.7)
        self.wait(1.0)

        # fade out the overlay only: the printed panel underneath is what the card hands back
        self.play(FadeOut(Group(card, ground, L_static, R_static, L_atom, R_atom,
                                *L_forces, *R_forces, *L_eq, *R_eq)), run_time=0.45)
        self.wait(0.3)


class FrictionComp(PrintScene):
    """p6 "Friction-compensated": the printed figure only, in the v22 film language.

    The card covers just the small incline drawing on the right of the panel; the four
    lines of definition on the left are untouched. Measured on pages/p06.jpg, the printed
    incline RISES to the right: base line y 769.7 running from x 364.3, hypotenuse
    18.22 deg (fitted over 109 columns), tall vertical edge at x 567.5, block side 37 pt.
    The film draws the same incline and shows the two forces that cancel: mg sin theta
    down the plane through the block's centre and friction up it hugging the surface,
    equal in length, so a = 0.
    """

    PAGE = 6
    # the printed figure only: text column ends at x 350, panel frame at 577.5
    REGION = (352.0, 698.0, 566.0, 776.0)

    THETA = 18.22              # printed hypotenuse angle, rising to the right
    GROUND = 769.7             # printed base line
    LOW_X = 364.3              # the low corner, at the left
    APEX_X = 567.5             # the tall vertical edge, at the right
    BLOCK_S = 37.0             # printed block side
    D0 = 100.8                 # contact point, along the plane from the low corner
    ARM = 41.0                 # mg sin theta and f are equal, because they cancel
    LAB_MG = (395.0, 741.3)    # printed label centres
    LAB_F = (494.2, 718.0)
    THETA_LBL = (420.8, 761.3)
    CHIP_AT = (520.0, 706.5)

    def construct(self):
        th = math.radians(self.THETA)
        card = self.cream_card()
        low = (self.LOW_X, self.GROUND)
        apex = (self.APEX_X, self.GROUND - (self.APEX_X - self.LOW_X) * math.tan(th))
        wedge_pts = [low, (self.APEX_X, self.GROUND), apex]
        wedge = Polygon(*[self.P(*p) for p in wedge_pts], fill_color=self.WEDGE_A,
                        fill_opacity=0.96, stroke_color=self.WEDGE_EDGE,
                        stroke_width=self.w(1.2)).set_z_index(3)
        hatch = self.hatch(wedge_pts, spacing=4.5)
        ground = VGroup(
            Line(self.P(low[0] - 4.0, self.GROUND), self.P(self.APEX_X + 3.0, self.GROUND),
                 color=self.WEDGE_EDGE, stroke_width=self.w(1.2)),
            *[Line(self.P(x, self.GROUND), self.P(x - 4.0, self.GROUND + 6.0),
                   color=self.WEDGE_EDGE, stroke_width=self.w(0.7),
                   stroke_opacity=0.30)
              for x in [self.LOW_X + 8.0 + n * 10.0 for n in range(20)]],
        ).set_z_index(3.05)
        arc = Arc(radius=7.0 * self.k, start_angle=0, angle=th,
                  color=self.WEDGE_EDGE, stroke_width=self.w(0.9)
                  ).move_arc_center_to(self.P(*low)).set_z_index(6)
        c_th = self.txt("θ", 6.6, self.WEDGE_EDGE).move_to(
            self.P(*self.THETA_LBL)).set_z_index(6)

        ud = (-math.cos(th), math.sin(th))      # down the plane: left and down the page
        nn = (-math.sin(th), -math.cos(th))     # away from the plane: left and up
        half = self.BLOCK_S / 2
        foot = (low[0] - ud[0] * self.D0, low[1] - ud[1] * self.D0)
        cen = (foot[0] + nn[0] * half, foot[1] + nn[1] * half)
        corners = []
        for su, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            corners.append((cen[0] + su * half * ud[0] + sn * half * nn[0],
                            cen[1] + su * half * ud[1] + sn * half * nn[1]))
        block = Polygon(*[self.P(*p) for p in corners], fill_color="#FFFFFF",
                        fill_opacity=0.98, stroke_color=self.INK2,
                        stroke_width=self.w(1.1)).set_z_index(4)

        # mg sin theta: down the plane, out of the block's centre
        mg = self.arrow(cen, (cen[0] + ud[0] * self.ARM, cen[1] + ud[1] * self.ARM),
                        self.CORAL, head=6.5, headw=3.2)
        c_mg = self.txt("mg sin θ", 7.2, self.CORAL).move_to(
            self.P(*self.LAB_MG)).set_z_index(7)

        # friction: along the surface beside the block, up the plane, the same length
        f0 = (foot[0] + ud[0] * half + nn[0] * 1.5, foot[1] + ud[1] * half + nn[1] * 1.5)
        f1 = (f0[0] - ud[0] * self.ARM, f0[1] - ud[1] * self.ARM)
        fr = self.arrow(f0, f1, self.TEAL, head=6.5, headw=3.2)
        c_fr = self.txt("f", 7.4, self.TEAL).move_to(self.P(*self.LAB_F)).set_z_index(7)

        zero = self.chip(self.CHIP_AT[0], self.CHIP_AT[1], "a = 0", self.INK2, 7.2)

        self.wait(0.5)
        self.play(FadeIn(card), run_time=0.6)
        self.play(Create(wedge), Create(ground), run_time=0.7)
        self.play(FadeIn(hatch), FadeIn(arc), FadeIn(c_th), run_time=0.4)
        self.play(FadeIn(block), run_time=0.4)
        self.play(FadeIn(mg), FadeIn(c_mg), run_time=0.6)
        self.play(FadeIn(fr), FadeIn(c_fr), run_time=0.6)
        self.wait(0.4)
        self.play(FadeIn(zero), run_time=0.5)
        self.wait(1.4)

        self.play(FadeOut(Group(card, wedge, ground, hatch, arc, c_th, block,
                                mg, c_mg, fr, c_fr, zero)), run_time=0.45)
        self.wait(0.3)
