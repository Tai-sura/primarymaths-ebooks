/**
 * Interactive graphics for this book, opened from a question's graphic button.
 * Build them from the shared kit; house rules are in docs/03-authoring-style.md.
 * books/jm26b/widgets.js has many worked examples (sliders, number lines,
 * bar models, MC checkers).
 *
 * Nothing is registered here on purpose: a template that ships a worked example
 * gets copied into every new book, and a mathematics example then shows up in a
 * physics book until someone notices (jpfm08 shipped the marble inequality this
 * way). Write the book's own graphic, then register it below.
 */

import { C, T, scene, clear, bar, slider, readout, question, buttonRow } from "../../engine/widgets/kit.js";

const REGISTRY = {};

export function hasGraphic(id) {
  return Boolean(REGISTRY[id]);
}

export function mountGraphic(id, root) {
  REGISTRY[id]?.(root);
}
