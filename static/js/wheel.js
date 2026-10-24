import { $, sleep } from "./dom.js";

// European wheel order (clockwise, starting at 0). Used only for drawing.
const WHEEL_ORDER = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11,
  30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35,
  3, 26];
const RED_NUMBERS = new Set([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25,
  27, 30, 32, 34, 36]);
const COLORS = { red: "#b3261e", black: "#1c1c1c", green: "#1b7f3b" };
const STEP = 360 / WHEEL_ORDER.length;
const SPIN_MS = 3500;

let rotation = 0;                  // total wheel rotation in degrees

function colorOf(pocket) {
  if (pocket === 0) return "green";
  return RED_NUMBERS.has(pocket) ? "red" : "black";
}

function svgEl(name, attrs) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  return el;
}

// angle is measured clockwise from 12 o'clock
function polar(radius, deg) {
  const rad = (deg * Math.PI) / 180;
  return [radius * Math.sin(rad), -radius * Math.cos(rad)];
}

export function buildWheel() {
  const svg = $("wheel");
  const R = 100;
  svg.appendChild(svgEl("circle", { r: 108, fill: "#5b3a1e" }));

  WHEEL_ORDER.forEach((number, i) => {
    const a0 = i * STEP;
    const a1 = (i + 1) * STEP;
    const [x0, y0] = polar(R, a0);
    const [x1, y1] = polar(R, a1);
    svg.appendChild(svgEl("path", {
      d: `M0,0 L${x0},${y0} A${R},${R} 0 0 1 ${x1},${y1} Z`,
      fill: COLORS[colorOf(number)],
      stroke: "#d4af37",
      "stroke-width": 0.4,
    }));

    const label = svgEl("text", {
      transform: `rotate(${a0 + STEP / 2}) translate(0,-86)`,
      "text-anchor": "middle",
      "dominant-baseline": "middle",
      fill: "#ffffff",
      "font-size": 6,
      "font-family": "system-ui, sans-serif",
    });
    label.textContent = number;
    svg.appendChild(label);
  });

  svg.appendChild(svgEl("circle", {
    r: 30, fill: "#2b2b2b", stroke: "#d4af37", "stroke-width": 1,
  }));
}

// Spin the wheel so that `pocket` ends up under the pointer at the top.
// The server already decided the result; this only draws it.
export function animateWheel(pocket) {
  const svg = $("wheel");
  const centerAngle = WHEEL_ORDER.indexOf(pocket) * STEP + STEP / 2;
  const extra = (((-centerAngle - rotation) % 360) + 360) % 360;
  rotation += 360 * 5 + extra;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ms = reduceMotion ? 0 : SPIN_MS;
  svg.style.transition = ms
    ? `transform ${ms}ms cubic-bezier(0.15, 0.6, 0.1, 1)`
    : "none";
  svg.style.transform = `rotate(${rotation}deg)`;
  return sleep(ms + 300);
}
