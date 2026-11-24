"""Manim scenes for the phy11 concept panels.

Each scene builds on the printed panel itself: the panel is rendered from the QUE
pdf into the camera frame, white covers hide the parts to be shown, and the scene
reassembles them in teaching order before wiping the covers away, so its last frame
is the printed panel (that frame becomes the poster). Coordinates are page points
(595 x 842, origin top left), measured on the 3x page render.
"""

import json
from pathlib import Path

import fitz
import numpy as np
from manim import (
    BOLD, DOWN, LEFT, RIGHT, UP, AnimationGroup, ArcBetweenPoints, Arrow, Circle, Create, DashedLine, FadeIn,
    FadeOut, ImageMobject, Line, ORIGIN, Polygon, Rectangle, RoundedRectangle, Scene, Succession, Text,
    VGroup, VMobject, ValueTracker, Wait, config, linear,
)

from guide import GuideScene

ROOT = Path(__file__).resolve().parents[2]
Z = 5  # pixels per point of the panel render

INK = "#1a1a1a"
BLUE = "#1f4fff"
GREEN = "#1d8a4a"
RED = "#d02a2a"
AMBER = "#f0a030"


class PrintScene(Scene):
    BOOK = "phy11"
    PAGE = 1
    REGION = (0, 0, 595, 842)

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

    def cover(self, x0, y0, x1, y1):
        c = Rectangle(width=(x1 - x0) * self.k, height=(y1 - y0) * self.k, stroke_width=0,
                      fill_color="#ffffff", fill_opacity=1).move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2))
        c.set_z_index(2)
        self.add(c)
        return c

    def wipe(self, c, run_time=0.8, edge="left"):
        keep = {"left": RIGHT, "top": DOWN, "right": LEFT, "bottom": UP}[edge]
        self.play(c.animate(run_time=run_time).stretch_to_fit_width(1e-4, about_edge=keep))
        self.remove(c)

    def ring(self, x0, y0, x1, y1, color, pad=2.0, width=1.8):
        r = RoundedRectangle(corner_radius=3 * self.k, width=(x1 - x0 + 2 * pad) * self.k,
                             height=(y1 - y0 + 2 * pad) * self.k, color=color, stroke_width=self.w(width))
        return r.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(5)

    def label(self, x, y, s, color=INK, size=13):
        t = Text(s, color=color)
        t.scale_to_fit_height(size * self.k * 0.75)
        return t.move_to(self.P(x, y)).set_z_index(6)


class ResolvingVelocity(PrintScene):
    """p1 'Resolving velocity': v is split into v cosθ across and v sinθ up.

    The printed figure already draws the velocity, the two dashed component guides and every
    label, so the film adds no words: it fills each printed guide in with a solid arrow of the
    printed colour, one at a time, and then lights the formula that ties them together. Every
    point below is measured on pages/p01.jpg, so each overlay sits on the line it explains:
    the vector runs (403.0, 258.9) -> (521.7, 164.4) at 38.6 deg, the horizontal guide is at
    y = 265.5 from x 403.7 to 522.3, and the vertical guide is at x = 402.2 from y 259.0 to
    142.3.
    """

    PAGE = 1
    REGION = (40, 103, 577, 318)

    def construct(self):
        A = self.P(403.0, 258.9)          # the muzzle: v and both components leave here
        T = self.P(521.7, 164.4)          # the printed vector's tip

        # the print's own colours, so a filled guide reads as that guide becoming solid
        v = Arrow(A, T, buff=0, color="#1404ff", stroke_width=self.w(3.2), tip_length=8.5 * self.k)
        self.wait(0.5)
        self.play(Create(v), run_time=1.0)
        self.wait(0.5)

        vx = Arrow(self.P(403.7, 265.5), self.P(522.3, 265.5), buff=0, color="#19eb16",
                   stroke_width=self.w(2.6), tip_length=7.5 * self.k)
        self.play(Create(vx), run_time=0.9)
        self.wait(0.4)

        vy = Arrow(self.P(402.2, 259.0), self.P(402.2, 142.3), buff=0, color="#fe030a",
                   stroke_width=self.w(2.6), tip_length=7.5 * self.k)
        self.play(Create(vy), run_time=0.9)
        self.wait(0.8)

        # the formula that ties vx and vy back into v
        ring = self.ring(136, 124, 270, 205, AMBER)
        self.play(FadeIn(ring), run_time=0.7)
        self.wait(0.9)
        self.play(FadeOut(ring), run_time=0.5)
        # hand the panel back to the print: the last frame is the printed figure
        self.play(FadeOut(VGroup(v, vx, vy)), run_time=0.7)
        self.wait(0.4)


class HorizontalProjectile(PrintScene):
    """p1 'Horizontal projectile motion': a steady sideways drift, an accelerating fall.

    The printed figure is a stroboscope: six positions at equal time steps, and red
    lines that pair the projectile with a ball simply dropped from rest. The film
    replays that live instead of hiding it -one ball on the gravity-free line, one on
    the drop column, the projectile between them -so the print underneath is already
    correct at every instant, and the last frame is the printed panel itself.
    """

    PAGE = 1
    REGION = (198, 419, 486, 618)

    X0, Y0 = 251.8, 452.0    # the ball leaves the muzzle here, in page points
    DX = 32.44               # across per time step: uniform, so the printed steps are equal
    DROP = 4.90              # down per time step squared: the fall accelerates
    N = 5                    # the print shows t = 0 -5

    def at(self, n):
        """Projectile after n time steps, in page points."""
        return self.P(self.X0 + self.DX * n, self.Y0 + self.DROP * n * n)

    def construct(self):
        n = ValueTracker(0.0)

        def ball(color):
            return Circle(radius=2.5 * self.k, stroke_width=0, fill_color=color,
                          fill_opacity=1).set_z_index(7)

        proj, across, dropped = ball(GREEN), ball(BLUE), ball(AMBER)
        for mob, place in (
            (proj, lambda v: self.at(v)),
            (across, lambda v: self.P(self.X0 + self.DX * v, self.Y0)),
            (dropped, lambda v: self.P(self.X0, self.Y0 + self.DROP * v * v)),
        ):
            mob.add_updater(lambda m, f=place: m.move_to(f(n.get_value())))

        # the two legs of the right triangle, live: the height below the gravity-free
        # line and the distance from the drop column
        leg_h = Line(self.P(self.X0, self.Y0), self.P(self.X0, self.Y0), color=RED,
                     stroke_width=self.w(1.5), stroke_opacity=0.75).set_z_index(6)
        leg_v = Line(self.P(self.X0, self.Y0), self.P(self.X0, self.Y0), color=RED,
                     stroke_width=self.w(1.5), stroke_opacity=0.75).set_z_index(6)

        def bend_legs(_=None):
            v = n.get_value()
            y = self.Y0 + self.DROP * v * v
            x = self.X0 + self.DX * v
            a, b = self.P(self.X0, y), self.P(x, y)
            if np.linalg.norm(b - a) < 1e-3:
                b = a + np.array([1e-3, 0.0, 0.0])
            leg_h.put_start_and_end_on(a, b)
            a, b = self.P(x, self.Y0), self.P(x, y)
            if np.linalg.norm(b - a) < 1e-3:
                b = a + np.array([0.0, -1e-3, 0.0])
            leg_v.put_start_and_end_on(a, b)

        bend_legs()
        self.add(leg_h, leg_v)
        leg_h.add_updater(bend_legs)
        leg_v.add_updater(bend_legs)

        # the throw: u to the right, and the same height at t = 0
        arrow = Arrow(self.P(self.X0, self.Y0), self.P(self.X0 + 16, self.Y0), buff=0, color=BLUE,
                      stroke_width=self.w(2.0), tip_length=5 * self.k).set_z_index(6)
        lab_u = self.label(self.X0 + 9, self.Y0 - 7, "u", BLUE, 11)

        self.play(FadeIn(arrow), FadeIn(lab_u), FadeIn(proj), FadeIn(across), FadeIn(dropped),
                  run_time=0.7)
        # linear in n, so the horizontal steps stay equal while the drops grow
        self.play(n.animate.set_value(self.N), run_time=4.0, rate_func=linear)
        self.wait(1.2)
        # hand the panel back to the print: the last frame is the printed figure
        self.play(FadeOut(VGroup(proj, across, dropped, arrow, lab_u, leg_h, leg_v)), run_time=0.8)
        self.wait(0.4)

class ProjectileAngle(PrintScene):
    """p4 'Projectile motion with an angle': v is a constant vx plus a vy that dies at the top.

    The printed figure already shows the launch triangle and the lone vx at the apex, so the
    film only adds the live pair travelling with the ball: the horizontal arrow keeps its
    length, the vertical one shrinks to nothing at the highest point and then grows downwards.
    """

    PAGE = 4
    REGION = (50, 108, 478, 281)

    AX, AY = 171.7, 232.0    # the ball leaves the table here, in page points
    BX = 447.0               # and lands here
    RISE = 111.0             # apex height above the launch
    VX_LEN = 42.0            # the printed horizontal arrow at the apex is this long
    VY_LEN = 30.0            # the vertical speed at t = 0 and again at the floor

    def path(self, s):
        """Point on the printed parabola after a fraction s of the flight, in page points."""
        return (self.AX + (self.BX - self.AX) * s, self.AY - 4 * self.RISE * s * (1 - s))

    def construct(self):
        s = ValueTracker(0.2)

        def make_vec(color, width):
            shaft = Line(ORIGIN, ORIGIN, color=color, stroke_width=self.w(width))
            head = Polygon(ORIGIN, ORIGIN, ORIGIN, ORIGIN, color=color, fill_color=color,
                           fill_opacity=1, stroke_width=0)
            return VGroup(shaft, head)

        def aim(g, start, end):
            vec = end - start
            length = float(np.linalg.norm(vec))
            head_len = 6.0 * self.k
            if length <= head_len * 1.05:
                g.set_opacity(0)
                return
            g.set_opacity(1)
            d = vec / length
            n = np.array([-d[1], d[0], 0.0])
            base = end - d * head_len
            g[0].put_start_and_end_on(start, base)
            w = 2.6 * self.k
            g[1].set_points_as_corners([base + n * w, end, base - n * w, base + n * w])

        vx, vy = make_vec(GREEN, 2.2), make_vec(RED, 2.2)

        def update_vx(g):
            v = s.get_value()
            x, y = self.path(v)
            aim(g, self.P(x, y), self.P(x + self.VX_LEN, y))

        def update_vy(g):
            v = s.get_value()
            x, y = self.path(v)
            aim(g, self.P(x, y), self.P(x, y - self.VY_LEN * (1 - 2 * v)))

        vx.add_updater(update_vx)
        vy.add_updater(update_vy)

        halo = Circle(radius=3.4 * self.k, stroke_width=0, fill_color="#ffffff", fill_opacity=1)
        core = Circle(radius=2.2 * self.k, stroke_width=0, fill_color=AMBER, fill_opacity=1)
        ball = VGroup(halo, core)
        ball.add_updater(lambda m: m.move_to(self.P(*self.path(s.get_value()))))

        update_vx(vx)
        update_vy(vy)
        ball.move_to(self.P(*self.path(s.get_value())))
        self.add(ball, vx, vy)

        # linear in s, so the sideways step per frame stays equal while the fall speeds up
        self.play(s.animate.set_value(0.92), run_time=3.4, rate_func=linear)
        self.wait(0.9)
        for mob in (ball, vx, vy):
            mob.clear_updaters()
        # hand the panel back to the print: the last frame is the printed figure
        self.play(FadeOut(VGroup(ball, vx, vy)), run_time=0.7)
        self.wait(0.3)


class ProjectileRanges(PrintScene):
    """p7 'Horizontal Range R': same range, different flights.

    The printed family is not one physical speed - it is drawn about 1.6x taller than a real
    projectile of that range - so each ball rides a parabola whose apex is measured off that
    printed curve. Only the timing is physical: t is proportional to sin(theta), so the 30 deg
    ball lands well before the 60 deg ball even though they share a landing point.
    """

    PAGE = 7
    REGION = (344, 80, 562, 244)

    X0, Y0 = 374.8, 216.0
    # apex heights measured on pages/p07.jpg, launch (374.8, 216.0), all residuals <= 1 pt
    H = {15: 7.00, 30: 30.95, 45: 65.30, 60: 95.45, 75: 120.85}
    LAND = {15: 454.0, 30: 514.8, 45: 537.2, 60: 514.8, 75: 454.0}
    # t ~ sin(theta) / sin(30 deg): 30 deg is the unit
    TIME = {15: 0.518, 30: 1.000, 45: 1.414, 60: 1.732, 75: 1.932}

    def setup(self):
        # take the panel from the same jpg the book ships, not a fresh pdf render, so the
        # last frame is that crop exactly and the poster cannot drift by a pixel
        from PIL import Image as _Image
        x0, y0, x1, y1 = self.REGION
        self.k = config.frame_height / (y1 - y0)
        self.c = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.camera.background_color = "#ffffff"
        folder = ROOT / "books" / self.BOOK
        page = _Image.open(folder / "pages" / ("p%02d.jpg" % self.PAGE)).convert("RGB")
        self.img = np.array(page)
        self.add(self.crop(*self.REGION))

    def crop(self, x0, y0, x1, y1):
        z = self.img.shape[1] / 595.32
        part = self.img[round(y0 * z):round(y1 * z), round(x0 * z):round(x1 * z)]
        m = ImageMobject(part)
        m.stretch_to_fit_width((x1 - x0) * self.k).stretch_to_fit_height((y1 - y0) * self.k)
        return m.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2))

    def spot(self, theta, s):
        """Point on that printed curve after a fraction s of its flight, in page points."""
        s = min(max(s, 0.0), 1.0)
        x = self.X0 + (self.LAND[theta] - self.X0) * s
        return self.P(x, self.Y0 - 4 * self.H[theta] * s * (1 - s))

    def construct(self):
        for pair, span in (((30, 60), 1.732), ((15, 75), 1.932), ((45,), 1.414)):
            clock = ValueTracker(0.0)
            balls = []
            for theta in pair:
                ball = Circle(radius=3.75 * self.k, fill_color=GREEN, fill_opacity=1,
                              stroke_color="#ffffff", stroke_width=self.w(1.1)).set_z_index(9)
                ball.add_updater(lambda m, th=theta: m.move_to(
                    self.spot(th, clock.get_value() / self.TIME[th])))
                ball.move_to(self.spot(theta, 0.0))
                balls.append(ball)

            anims = [clock.animate(run_time=span).set_value(span)]
            for theta in pair:
                ring = Circle(radius=4.2 * self.k, fill_opacity=0, stroke_color=GREEN,
                              stroke_width=self.w(1.6)).set_z_index(8)
                ring.move_to(self.P(self.LAND[theta], self.Y0))
                ring.set_opacity(0)
                anims.append(Succession(
                    Wait(self.TIME[theta] - 0.12),
                    ring.animate(run_time=0.1).set_opacity(1),
                    ring.animate(run_time=0.4).scale(1.9).set_opacity(0),
                ))

            self.add(*balls)
            self.play(*anims, rate_func=linear)
            for ball in balls:
                ball.clear_updaters()
            # the ball that landed first waits on the printed egg, so the later one lands on top
            self.play(FadeOut(VGroup(*balls)), run_time=0.3)
            self.wait(0.15)
        self.wait(0.5)

class Q17(GuideScene):
    """p8 Q17, monkey and hunter - the principle only, never the printed numbers.

    The printed 20 deg / 60 m / 25 m cannot make the arrow hit: at 60 m the arrow rises
    60 tan 20 = 21.84 m, so from the bow drawn 4.4 m up it passes 1.24 m above the coconut
    (from the ground it would pass 3.16 m below). So the film shows only the argument: the arrow
    leaves along the printed aim line and the coconut is released at the same instant, and the
    two red bars - the arrow's fall below the aim line and the coconut's fall from its branch -
    are equal at every instant because one fall(t) drives both. It flies 65% of the way and
    stops before the coconut's column: no meeting, no numbers, no flash.
    """

    BOOK = "phy11"
    PAGE = 8
    REGION = (280.0, 186.0, 595.3, 363.4)
    Z = 6                       # page pixels per point for the crop

    LX, LY = 351.38, 268.47     # the arrow leaves the bow here, on the printed aim line
    CX, CY = 532.38, 202.79     # the coconut's centre on the branch, the aim line's far end
    GY = 282.5                  # the printed ground line
    T = 1.42                    # 60 m / (45 cos 20 deg) = 1.42 s, the book's rounded answer
    SV = (282.5 - 202.79) / 25.0    # page points per metre, from the printed 25 m
    DROP = 0.5 * 9.81 * T * T * SV  # 1/2 g T^2 in page points = 9.89 m

    def setup(self):
        super().setup()
        folder = ROOT / "books" / self.BOOK
        book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
        page = fitz.open(folder / book["source"]["que"])[self.PAGE - 1]
        x0, y0, x1, y1 = self.REGION
        pix = page.get_pixmap(matrix=fitz.Matrix(self.Z, self.Z), clip=fitz.Rect(x0, y0, x1, y1))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        m = ImageMobject(img.copy())
        m.stretch_to_fit_width((x1 - x0) * self.k).stretch_to_fit_height((y1 - y0) * self.k)
        m.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(-2)
        self.add(m)
        # the last two lines of the question bleed into the figure's bounding box on the page;
        # they are question text, not diagram, so the guide opens on the figure alone
        r = Rectangle(width=(446 - 280) * self.k, height=(208 - 186) * self.k, stroke_width=0,
                      fill_color="#ffffff", fill_opacity=1)
        self.add(r.move_to(self.P(363, 197)).set_z_index(-1))

    # ---------- the one fall(t) ----------

    def spot(self, s):
        """The arrow after a fraction s of the flight, in page points."""
        return (self.LX + (self.CX - self.LX) * s,
                self.LY + (self.CY - self.LY) * s + self.DROP * s * s)

    def aim(self, x):
        """The printed aim line's height at x: both drops hang from this line."""
        return self.LY + (self.CY - self.LY) * (x - self.LX) / (self.CX - self.LX)

    def fall(self, s):
        return self.DROP * s * s

    def construct(self):
        s = ValueTracker(0.0)
        K = self.k

        # the arrow that flies: a shaft with a filled head, lying along the velocity
        shaft = Line(ORIGIN, ORIGIN, color=BLUE, stroke_width=self.w(2.0))
        head = Polygon(ORIGIN, ORIGIN, ORIGIN, ORIGIN, color=BLUE, fill_color=BLUE,
                       fill_opacity=1, stroke_width=0)
        arrow = VGroup(shaft, head).set_z_index(8).set_opacity(0)

        def steer(_=None):
            v = s.get_value()
            e = 0.012
            d = self.P(*self.spot(min(v + e, 1.0))) - self.P(*self.spot(max(v - e, 0.0)))
            d = d / np.linalg.norm(d)
            mid = self.P(*self.spot(v))
            tip = mid + d * 4.0 * K
            tail = mid - d * 4.0 * K
            base = tip - d * 3.6 * K
            n = np.array([-d[1], d[0], 0.0])
            shaft.put_start_and_end_on(tail, base)
            head.set_points_as_corners([base + n * 1.7 * K, tip, base - n * 1.7 * K, base + n * 1.7 * K])

        arrow.add_updater(steer)
        steer()

        # the path flown so far: the parabola the arrow really takes, below the printed aim line
        trail = VMobject(color=BLUE, stroke_width=self.w(0.9)).set_z_index(4)
        trail.set_stroke(opacity=0.55)

        def draw_trail(_=None):
            v = max(s.get_value(), 1e-3)
            trail.set_points_as_corners([self.P(*self.spot(u)) for u in np.linspace(0.0, v, 64)])

        trail.add_updater(draw_trail)
        draw_trail()

        # the coconut leaves the branch at the same instant
        coco = (Circle(radius=2.7 * K, stroke_width=self.w(0.9), stroke_color="#ffffff",
                       fill_color=AMBER, fill_opacity=1)
                .move_to(self.P(self.CX, self.CY)).set_z_index(9).set_opacity(0))

        def drop_coco(_=None):
            coco.move_to(self.P(self.CX, self.CY + self.fall(s.get_value())))

        coco.add_updater(drop_coco)
        drop_coco()

        # two drop rulers, both measured from the same aim line, so both are fall(t); the top
        # tick marks the aim line and the object itself marks the other end, so the red length
        # is the fall and nothing else
        def ruler():
            ln = Line(ORIGIN, ORIGIN, color=RED, stroke_width=self.w(1.4))
            cap = Line(ORIGIN, ORIGIN, color=RED, stroke_width=self.w(1.4))
            return VGroup(ln, cap).set_z_index(10)

        def set_ruler(g, x, top, bottom):
            if bottom - top < 0.45:
                g.set_opacity(0)
                return
            g.set_opacity(1)
            a, b = self.P(x, top), self.P(x, bottom)
            g[0].put_start_and_end_on(a, b)
            w = 2.1 * K
            g[1].put_start_and_end_on(a + np.array([-w, 0, 0]), a + np.array([w, 0, 0]))

        ruler_arrow, ruler_coco = ruler(), ruler()

        def bend_rulers(_=None):
            v = s.get_value()
            x, y = self.spot(v)
            set_ruler(ruler_arrow, x, self.aim(x), y)
            set_ruler(ruler_coco, self.CX, self.CY, self.CY + self.fall(v))

        ruler_arrow.add_updater(bend_rulers)
        ruler_coco.add_updater(bend_rulers)
        bend_rulers()

        self.add(arrow, trail, coco, ruler_arrow, ruler_coco)
        self.wait(0.5)

        # the bow and the coconut, released at the same instant
        self.play(arrow.animate(run_time=0.6).set_opacity(1), coco.animate(run_time=0.6).set_opacity(1))
        self.hold(0.4)
        # The printed 20 deg / 60 m / 25 m do not actually make the arrow hit, so this is the
        # principle only: it flies 65% of the way and stops well before the coconut's column,
        # while both drops stay equal. No numbers, no flash, no meeting point.
        self.play(s.animate(run_time=2.6, rate_func=linear).set_value(0.65))
        self.hold(1.0)
        # hand the panel back to the print: the last frame is the printed figure, as the poster
        self.play(FadeOut(VGroup(arrow, trail, coco, ruler_arrow, ruler_coco)), run_time=0.7)
        self.wait(0.4)


class Q18(GuideScene):
    """p8 Q18(a)(1): one circle per 0.05 s on the printed grid (Figure 4.2).

    The grid and the four X marks of the ball released from rest are printed, so the film adds
    only what the student is asked to draw: the bearing after 1, 2 and 3 steps of 0.05 s, each
    joined by a level line to the printed X of the same instant. Positions come from the printed
    marks themselves: the first image at (387.7, 599.0), 56.4 pt per step across (three grid
    columns) and 13.7 pt per step squared down (the least-squares fit to the four printed X,
    height = 599.0 + 13.7 k^2). One step of 0.05 s at 1 m/s is 8.2 pt/mm... in metres it is
    0.05 m across and 1/2 g (0.05)^2 = 0.0123 m down, which is the 1128 / 1117 pt per metre
    pair the printed figure is drawn with (1% apart).
    """

    BOOK = "phy11"
    PAGE = 8
    REGION = (342.0, 583.0, 595.3, 735.0)
    Z = 6
    X0, Y0 = 387.7, 599.0     # the first image: the printed leading O and the first X
    DX, A = 56.4, 13.7        # one step across; one step squared down

    def setup(self):
        super().setup()
        folder = ROOT / "books" / self.BOOK
        book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
        page = fitz.open(folder / book["source"]["que"])[self.PAGE - 1]
        x0, y0, x1, y1 = self.REGION
        pix = page.get_pixmap(matrix=fitz.Matrix(self.Z, self.Z), clip=fitz.Rect(x0, y0, x1, y1))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        m = ImageMobject(img.copy())
        m.stretch_to_fit_width((x1 - x0) * self.k).stretch_to_fit_height((y1 - y0) * self.k)
        m.move_to(self.P((x0 + x1) / 2, (y0 + y1) / 2)).set_z_index(-2)
        self.add(m)

    def at(self, k):
        """The bearing after k steps of 0.05 s, in page points."""
        return (self.X0 + self.DX * k, self.Y0 + self.A * k * k)

    def construct(self):
        self.wait(0.5)
        # the given interval, between the first two columns, above the first row
        lab = self.value("0.05 s", (self.X0 + self.DX / 2, 591.5), INK, 7.5)
        self.play(FadeIn(lab), run_time=0.6)
        self.hold(0.4)
        for k in (1, 2, 3):
            x, y = self.at(k)
            link = DashedLine(self.P(self.X0, y), self.P(x, y), color=AMBER,
                              stroke_width=self.w(0.9), dash_length=2.0 * self.k).set_opacity(0.85)
            ring = Circle(radius=2.9 * self.k, stroke_color=BLUE, stroke_width=self.w(1.6)).move_to(self.P(x, y))
            self.play(Create(link), Create(ring), run_time=0.9)
            self.hold(0.5)
        self.hold(1.0)
