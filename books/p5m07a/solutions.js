/**
 * Worked solutions for P5 Maths 07 Circles (A), following the teacher's ANS key.
 * Field reference: docs/02-book-format.md. House style: docs/03-authoring-style.md.
 *
 * The ANS key gives only the answers for the fill-in-the-blank questions, so those
 * entries carry the full working (definition / formula) before the underlined answer.
 */

import { m, t, h, note, L, lk } from "../../engine/authoring.js";

const U = (s) => `\\underline{\\underline{${s}}}`;

export const SOLUTIONS = [
  {
    id: "q1",
    boxes: [{
      steps: [
        t("Every diameter passes through the same point inside the circle."),
        t("That point is the centre of the circle."),
        m(`= ${U("\\text{centre}")}`),
      ],
    }],
  },
  {
    id: "q2",
    boxes: [{
      steps: [
        t("A line segment from the centre to any point on the circumference is a radius."),
        m(`= ${U("\\text{radius}")}`),
      ],
    }],
  },
  {
    id: "q3",
    boxes: [{
      steps: [
        t("A diameter is made of two radii."),
        m(`\\text{length of diameter}`),
        m(`= \\underline{2} \\times \\text{length of radius}`),
      ],
    }],
  },
  {
    id: "q4",
    boxes: [{
      steps: [
        t("The point marked in the middle of the circle is the centre."),
        m(`= ${U("O")}`),
      ],
    }],
  },
  {
    id: "q5",
    boxes: [{
      steps: [
        t("A radius joins the centre O to a point on the circumference."),
        m(`= ${U("OA, OC, OD, OF")}`),
      ],
    }],
  },
  {
    id: "q6",
    boxes: [{
      steps: [
        t("The longest straight lines in a circle pass through the centre."),
        t("These are AD and CF, and each of them is a diameter."),
        m(`= ${U("AD")} \\text{ and } ${U("CF")}; \\text{ they are } ${U("\\text{diameters}")}`),
      ],
    }],
  },
  {
    id: "q7",
    boxes: [{
      steps: [
        t("A line segment with both end points on the circumference, passing through the centre,"),
        t("is a diameter."),
        m(`= ${U("\\text{diameter}")}`),
      ],
    }],
  },
  {
    id: "q8",
    boxes: [{
      steps: [
        t("All radii of the same circle join the centre to the circumference."),
        m(`= \\text{the } ${U("\\text{same}")} \\text{ length}`),
      ],
    }],
  },
  {
    id: "q9",
    boxes: [{
      steps: [
        t("Every diameter of the same circle is twice its radius."),
        m(`= \\text{the } ${U("\\text{same}")} \\text{ length}`),
      ],
    }],
  },
  {
    id: "q10",
    boxes: [{
      steps: [
        m(`\\text{length of diameter} = 2 \\times \\text{length of radius}`),
        m(`= ${U("2")} \\text{ times}`),
      ],
    }],
  },
  {
    id: "q11",
    boxes: [{
      steps: [
        t("OR joins the centre O to R on the circumference, so OR is a radius."),
        m(`\\text{(a) } = ${U("\\text{radius}")}`),
      ],
    }, {
      steps: [
        t("QR passes through the centre O with both ends on the circumference."),
        m(`\\text{(b) } = ${U("\\text{diameter}")}`),
      ],
    }, {
      steps: [
        m(`\\text{QR} = 18 \\text{ cm is the diameter}`),
        m(`\\text{OR} = 18 \\div 2`),
        m(`\\text{(c) } = ${U("9")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q12",
    boxes: [{
      steps: [
        t("BE passes through the centre O, so BE is a diameter. ✓"),
        m(`\\text{(a) } = ${U("\\checkmark")}`),
      ],
    }, {
      steps: [
        t("OA is a radius of 8 cm, so the diameter AC = 8 × 2 = 16 cm. ✓"),
        m(`\\text{(b) } = ${U("\\checkmark")}`),
      ],
    }, {
      steps: [
        t("AD does not pass through O, so it is shorter than the diameter AC. ✗"),
        m(`\\text{(c) } = ${U("\\times")}`),
      ],
    }, {
      steps: [
        t("OC is a radius of 8 cm, while BE is a diameter of 16 cm; OC is not double BE. ✗"),
        m(`\\text{(d) } = ${U("\\times")}`),
      ],
    }],
  },
  {
    id: "q13",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times \\text{radius}`),
        t("So the radius is half of the diameter."),
        m(`= ${U("\\text{half}")}`),
      ],
    }],
  },
  {
    id: "q14",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times \\text{radius}`),
        m(`= 2 \\times 7`),
        m(`= ${U("14")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q15",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times \\text{radius}`),
        m(`= 2 \\times 4`),
        m(`= ${U("8")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q16",
    boxes: [{
      steps: [
        m(`\\text{radius} = \\text{diameter} \\div 2`),
        m(`= 9 \\div 2`),
        m(`= ${U("4.5")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q17",
    boxes: [{
      steps: [
        m(`\\text{radius} = \\text{diameter} \\div 2`),
        m(`= 12 \\div 2`),
        m(`= ${U("6")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q18",
    boxes: [{
      steps: [
        m(`\\text{Circle A: radius} = 3 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 3`),
        m(`= ${U("6")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q19",
    boxes: [{
      steps: [
        m(`\\text{Circle B: radius} = 2 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 2`),
        m(`= ${U("4")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q20",
    boxes: [{
      steps: [
        m(`\\text{Circle C: radius} = 5 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 5`),
        m(`= ${U("10")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q21",
    boxes: [{
      steps: [
        m(`\\text{Circle D: radius} = 1.5 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 1.5`),
        m(`= ${U("3")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q22",
    boxes: [{
      steps: [
        m(`\\text{Circle E: radius} = 3 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 3`),
        m(`= ${U("6")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q23",
    boxes: [{
      steps: [
        m(`\\text{Circle F: radius} = 6 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 6`),
        m(`= ${U("12")} \\text{ cm}`),
      ],
    }],
  },

  {
    id: "q24",
    boxes: [{
      steps: [
        m(`\\text{Small circle diameter} = 40 \\div 2 = 20 \\text{ cm}`),
        m(`\\text{(a) radius} = 20 \\div 2`),
        m(`= ${U("10")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`\\text{Rectangle width} = 20 + 40 = 60 \\text{ cm}`),
        m(`\\text{Perimeter} = 2 \\times (60 + 40)`),
        m(`\\text{(b) } = ${U("200")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q25",
    boxes: [{
      steps: [
        m(`\\text{OQ is a radius} = 9 \\text{ cm}`),
        m(`\\text{(a) diameter} = 2 \\times 9`),
        m(`= ${U("18")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`\\text{PR} = 18 \\text{ cm is shared by 3 equal circles}`),
        m(`\\text{small diameter} = 18 \\div 3 = 6 \\text{ cm}`),
        m(`\\text{(b) radius} = 6 \\div 2 = ${U("3")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q26",
    boxes: [{
      steps: [
        t("The point marked in the middle of the circle is the centre."),
        m(`= ${U("O")}`),
      ],
    }],
  },
  {
    id: "q27",
    boxes: [{
      steps: [
        t("A radius joins the centre to the circumference."),
        m(`= ${U("OA, OC, OF")}`),
      ],
    }],
  },
  {
    id: "q28",
    boxes: [{
      steps: [
        t("AC passes through the centre O with both ends on the circumference."),
        m(`= ${U("AC")}`),
      ],
    }],
  },
  {
    id: "q30",
    boxes: [{
      steps: [
        t("Each square of the grid is 1 cm."),
        m(`\\text{OF} = 5 \\text{ squares} = 5 \\text{ cm}`),
        m(`= ${U("5")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q31",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times \\text{radius}`),
        m(`= 2 \\times 5`),
        m(`= ${U("10")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q32",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times \\text{radius}`),
        m(`= ${U("2")} \\text{ times}`),
      ],
    }],
  },
  {
    id: "q33",
    boxes: [{
      steps: [
        t("BD joins the centre of the large circle to the centre of a small circle,"),
        m(`\\text{BD} = R + r = 24`),
        t("AC joins the two small-circle centres and passes through B,"),
        m(`\\text{AC} = (R + r) + R = 39`),
        m(`R = 39 - 24 = 15`),
        m(`\\text{(a) diameter} = 2 \\times 15 = ${U("30")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`R + r = 24`),
        m(`15 + r = 24`),
        m(`\\text{(b) } r = ${U("9")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q34",
    boxes: [{
      steps: [
        t("AX and CX are radii, so X is the centre; BX is also a radius."),
        t("AY does not pass through the centre X, so AY is a chord, not a diameter."),
        m(`\\text{not correct} = ${U("B")}`),
      ],
    }],
  },
  {
    id: "q35",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times 15 = 30 \\text{ cm}`),
        m(`\\text{Rectangle: } 60 \\text{ cm by } 30 \\text{ cm}`),
        m(`\\text{Perimeter} = 2 \\times (60 + 30)`),
        m(`= ${U("180")} \\text{ cm} \\quad (B)`),
      ],
    }],
  },
  {
    id: "q36",
    boxes: [{
      steps: [
        t("AB joins the centre of the first circle to the centre of the fourth."),
        m(`\\text{4 circles} \\to 3 \\text{ gaps, each } 24 \\text{ cm}`),
        m(`\\text{AB} = 3 \\times 24`),
        m(`= ${U("72")} \\text{ cm} \\quad (B)`),
      ],
    }],
  },
  {
    id: "q37",
    boxes: [{
      steps: [
        t("The rectangle is 2r tall and r wide (see the figure)."),
        m(`2(2r + r) = 90`),
        m(`6r = 90`),
        m(`r = ${U("15")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`\\text{Area} = r \\times 2r`),
        m(`= 15 \\times 30`),
        m(`= ${U("450")} \\text{ cm}^2 \\quad (C)`),
      ],
    }],
  },
  {
    id: "q38",
    boxes: [{
      steps: [
        t("F lies on chord AB, not on the circumference, so FG is not a radius."),
        m(`\\text{not correct} = ${U("B")}`),
      ],
    }],
  },
  {
    id: "q39",
    boxes: [{
      steps: [
        m(`\\text{side of square} = 12 \\div 4 = 3 \\text{ m}`),
        t("The gardener stands at the centre, so the shortest walk is half a side."),
        m(`= 3 \\div 2 = ${U("1.5")} \\text{ m} \\quad (A)`),
      ],
    }],
  },
  {
    id: "q40",
    boxes: [{
      steps: [
        t("Each circle passes through the other's centre, so AB = r."),
        m(`\\text{PQ} = r + r + r = 48`),
        m(`r = 16 \\text{ cm}`),
      ],
    }, {
      steps: [
        t("AT = TB = BR = RA = r, so ATBR is a rhombus."),
        m(`\\text{Perimeter} = 4 \\times 16`),
        m(`= ${U("64")} \\text{ cm} \\quad (C)`),
      ],
    }],
  },
  {
    id: "q41",
    boxes: [{
      steps: [
        t("AR = BR = AB = 16 cm (each is a radius, and AB = r)."),
        t("Three equal sides make ARB an equilateral triangle."),
        m(`= ${U("D")}`),
      ],
    }],
  },
  {
    id: "q42",
    boxes: [{
      steps: [
        t("The largest circle is limited by the shorter side, 15 cm."),
        m(`\\text{diameter} = 15 \\text{ cm}`),
        m(`\\text{radius} = 15 \\div 2`),
        m(`= ${U("7.5")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q43",
    boxes: [{
      steps: [
        t("A, B and C are centres, so each side of the triangle is 2r."),
        m(`3 \\times 2r = 54`),
        m(`\\text{diameter} = 54 \\div 3`),
        m(`= ${U("18")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q44",
    boxes: [{
      steps: [
        m(`\\text{large radius} = 2.5 \\times 3 = 7.5 \\text{ m}`),
        m(`\\text{(a) BC} = 2.5 \\times 3 + 2.5`),
        m(`= 7.5 + 2.5 = ${U("10")} \\text{ m (so XY = 10 m)}`),
      ],
    }, {
      steps: [
        m(`\\text{(b) Perimeter} = (10 + 2.5 \\times 3) \\times 2`),
        m(`= (10 + 7.5) \\times 2`),
        m(`= ${U("35")} \\text{ m}`),
      ],
    }],
  },
  {
    id: "q45",
    boxes: [{
      steps: [
        t("Each small circle is half of the next circle across."),
        m(`\\text{radius of C} = 26 \\div 2 \\div 2 \\div 2`),
        m(`= ${U("3.25")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "q46",
    boxes: [{
      steps: [
        m(`\\text{large radius} = 8 \\text{ cm}`),
        m(`\\text{small diameter} = 8 \\div 2 = 4 \\text{ cm}`),
        m(`\\text{(a) small radius} = 4 \\div 2 = ${U("2")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`\\text{(b) PQ} = 8 + 4`),
        m(`= ${U("12")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`\\text{(c) Area of } \\triangle OPS = \\tfrac{1}{2} \\times 8 \\times 4`),
        m(`= ${U("16")} \\text{ cm}^2`),
      ],
    }],
  },

  {
    id: "hw1",
    boxes: [{
      steps: [
        t("A, B, C and D are points on the circle, so they lie on the circumference."),
        m(`= ${U("\\text{circumference}")}`),
      ],
    }],
  },
  {
    id: "hw2",
    boxes: [{
      steps: [
        t("The diameter passes through the centre O and has both ends on the circumference."),
        m(`= ${U("AC")}`),
      ],
    }],
  },
  {
    id: "hw3",
    boxes: [{
      steps: [
        t("A radius joins the centre O to a point on the circumference."),
        m(`= ${U("OC, OD")} \\text{ (they are } ${U("\\text{radii}")} \\text{)}`),
      ],
    }],
  },
  {
    id: "hw4",
    boxes: [{
      steps: [
        t("C and D are on the circumference and O is the centre,"),
        t("so OC = OD and triangle CDO is isosceles."),
        m(`= ${U("D, O")}`),
      ],
    }],
  },
  {
    id: "hw5",
    boxes: [{
      steps: [
        t("(a) Draw AB through O, with A and B on the circle — a diameter."),
        t("(b) Draw another diameter CD through O, not on AB."),
        t("(c) Draw OE from the centre to the circumference — a radius."),
        t("(d) Draw FG with F and G on the circle, the line missing O — a chord."),
      ],
    }],
  },
  {
    id: "hw6",
    boxes: [{
      steps: [
        t("Measure the diameter AB and the radius OE from the figure."),
        m(`\\text{(a) AB} = ${U("5")} \\text{ cm}`),
        m(`\\text{OE} = ${U("2.5")} \\text{ cm}`),
      ],
    }, {
      steps: [
        m(`\\text{OE} = 5 \\div 2 = 2.5 \\text{ cm}`),
        t("(b) So the radius is half of the diameter."),
      ],
    }, {
      steps: [
        t("FG is a chord that does not pass through the centre."),
        t("A chord never exceeds the diameter, so (c) FG is shorter than AB."),
      ],
    }],
  },
  {
    id: "hw7",
    boxes: [{
      steps: [
        t("The longest segment inside a circle is the diameter."),
        t("No point pair on the circle can be farther apart than the diameter."),
        m(`\\text{(a) } = ${U("cannot")}`),
      ],
    }, {
      steps: [
        t("The radius is shorter than the diameter, so a segment shorter than OE can be drawn."),
        m(`\\text{(b) } = ${U("can")}`),
      ],
    }],
  },
  {
    id: "hw8",
    boxes: [{
      steps: [
        m(`\\text{Circle P: radius} = 33 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 33`),
        m(`= ${U("66")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "hw9",
    boxes: [{
      steps: [
        m(`\\text{Circle Q: diameter} = 24 \\text{ cm}`),
        m(`\\text{radius} = 24 \\div 2`),
        m(`= ${U("12")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "hw10",
    boxes: [{
      steps: [
        m(`\\text{Circle R: radius} = 9.5 \\text{ cm}`),
        m(`\\text{diameter} = 2 \\times 9.5`),
        m(`= ${U("19")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "hw11",
    boxes: [{
      steps: [
        m(`\\text{1 cm} = 10 \\text{ mm}`),
        m(`\\text{radius} = 10 \\div 2`),
        m(`= ${U("5")} \\text{ mm}`),
      ],
    }],
  },
  {
    id: "hw12",
    boxes: [{
      steps: [
        m(`\\text{diameter} = 2 \\times 12 = 24 \\text{ cm}`),
        t("AB spans four diameters."),
        m(`\\text{AB} = 8 \\times 12 = ${U("96")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "hw13",
    boxes: [{
      steps: [
        m(`\\text{large diameter} = 16 \\text{ cm, small diameter} = 11 \\text{ cm}`),
        m(`\\text{Perimeter} = 11 \\times 2 + 16 \\times 2`),
        m(`= 22 + 32`),
        m(`= ${U("54")} \\text{ cm}`),
      ],
    }],
  },
  {
    id: "hw14",
    boxes: [{
      steps: [
        m(`\\text{BC is the diameter, radius} = 10 \\text{ cm}`),
        m(`\\text{BC} = 2 \\times 10 = 20 \\text{ cm}`),
        m(`\\text{Area} = 10 \\times 2 \\times 10`),
        m(`= ${U("200")} \\text{ cm}^2`),
      ],
    }],
  },
];
