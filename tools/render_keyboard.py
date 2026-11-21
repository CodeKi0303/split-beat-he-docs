"""Top-view diagram of both C86 halves with their USB-C ports, for the guide.

Geometry comes from the real CAD sources through ../shipping-foam/geometry.py
(upper/lower plate DXF, keycap sizes, D20 knob STEP, wheel module STEP). The
USB-C positions come from the C86 PCB (J401 PC, J501 left link, J551 right
link), mapped into the plate frame by the MX switch and knob centres (residual
printed below). Writes an inline <svg> between the keyboard-diagram markers in
site/index.html, styled by .kb-* classes in site/style.css.

Run with the CAD venv:
  .tools/cad-venv/Scripts/python.exe -X utf8 split-beat-he-docs/tools/render_keyboard.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

DOCS = Path(__file__).resolve().parents[1]
ROOT = DOCS.parent
sys.path.insert(0, str(ROOT / "shipping-foam"))
import geometry as g  # noqa: E402

PCB = ROOT / "output/rev-c86-four-layer/pcb/split-hall-c86-four-layer-REVIEW-NOT-ORDER.kicad_pcb"
INDEX = DOCS / "site/index.html"

# Default mapping labels by plate key name (Studio default-bindings).
LABELS = {
    "L": {"CAPS": "Tab", "Q": "A", "W": "S", "E": "D", "R": "F", "SHIFT": "L Shift", "SPACE": "Space", "1": "F1", "4": "F5"},
    "R": {"CAPS": "Enter", "Q": ";", "W": "L", "E": "K", "R": "J", "SHIFT": "R Shift", "SPACE": "R Alt", "1": "→", "4": "←"},
}
MX = {"1", "4"}


def pcb_refs():
    s = PCB.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'\(footprint "[^"]+"(.*?)\n\t\)', s, re.S):
        ref = re.search(r'\(property "Reference" "([^"]+)"', m.group(1))
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)", m.group(1))
        if ref and at:
            out[ref.group(1)] = (float(at.group(1)), float(at.group(2)))
    return out


def fit(src, dst):
    """Rigid fit with optional reflection: returns f(points) and RMS residual."""
    src, dst = np.asarray(src, float), np.asarray(dst, float)
    best = None
    for refl in (1, -1):
        s = src * [1, refl]
        sc, dc = s.mean(0), dst.mean(0)
        u, _, vt = np.linalg.svd((s - sc).T @ (dst - dc))
        r = (u @ vt).T
        if np.linalg.det(r) < 0:
            continue
        res = np.sqrt((((s - sc) @ r.T + dc - dst) ** 2).sum(1).mean())
        if best is None or res < best[0]:
            best = (res, refl, r, sc, dc)
    res, refl, r, sc, dc = best
    return (lambda p: (np.asarray(p, float) * [1, refl] - sc) @ r.T + dc), res


def ports():
    refs = pcb_refs()
    out = {}
    for side, mx1, mx4, enc, port_refs in (
        ("L", "SW1201", "SW1204", "ENC1401", {"pc": "J401", "link": "J501"}),
        ("R", "SW1301", "SW1304", "ENC1501", {"link": "J551"}),
    ):
        k, kn = g.keys(side), g.knob(side)[-1]
        f, res = fit([refs[mx1], refs[mx4], refs[enc]], [(k["1"]["x"], k["1"]["y"]), (k["4"]["x"], k["4"]["y"]), (kn["cx"], kn["cy"])])
        print(side, "PCB->plate fit residual mm", round(float(res), 3))
        assert res < 0.2, res
        for role, ref in port_refs.items():
            out[(side, role)] = tuple(float(v) for v in f([refs[ref]])[0])
    return out


def svg_poly(poly, cls):
    pts = " ".join(f"{x:.1f},{-y:.1f}" for x, y in poly.exterior.coords)
    return f'<polygon class="{cls}" points="{pts}"/>'


def render():
    p = ports()
    parts = []
    for side in "LR":
        body = g.lower_outline(side)
        plate, _, _ = g.plate(side)
        parts.append(svg_poly(body, "kb-body"))
        parts.append(svg_poly(plate, "kb-plate"))
        wheel, _ = g.wheel_cluster(side)
        w = wheel["wheel"][0].minimum_rotated_rectangle.buffer(-2.5).buffer(2.5, 8)
        parts.append(svg_poly(w, "kb-wheel"))
        wc = w.centroid
        parts.append(f'<text class="kb-note" x="{wc.x:.1f}" y="{-wc.y + 1.6:.1f}">롤러</text>')
        bezel, knob = g.knob(side)
        parts.append(f'<circle class="kb-bezel" cx="{knob["cx"]:.1f}" cy="{-knob["cy"]:.1f}" r="{bezel["d"] / 2:.1f}"/>')
        parts.append(f'<circle class="kb-knob" cx="{knob["cx"]:.1f}" cy="{-knob["cy"]:.1f}" r="{knob["d"] / 2:.1f}"/>')
        parts.append(f'<text class="kb-note" x="{knob["cx"]:.1f}" y="{-knob["cy"] + 1.6:.1f}">노브</text>')
        for name, k in g.keys(side).items():
            cls = "kb-key kb-mx" if name in MX else "kb-key kb-hall"
            w_, h_ = k["w"] - 1.2, k["h"] - 1.2
            tf = f'translate({k["x"]:.2f} {-k["y"]:.2f}) rotate({-k["angle"]:.1f})'
            parts.append(f'<g transform="{tf}"><rect class="{cls}" x="{-w_ / 2:.2f}" y="{-h_ / 2:.2f}" width="{w_:.2f}" height="{h_:.2f}" rx="2.4"/>'
                         f'<text class="kb-label" y="1.8">{LABELS[side][name]}</text></g>')
        cx = (body.bounds[0] + body.bounds[2]) / 2
        parts.append(f'<text class="kb-side" x="{cx:.1f}" y="{-body.bounds[1] + 12:.1f}">{"왼쪽" if side == "L" else "오른쪽"}</text>')

    top = 56.0  # back edge of the case (lower plate) in the plate frame
    (pcx, _), (llx, _), (rlx, _) = p[("L", "pc")], p[("L", "link")], p[("R", "link")]
    # Cables: PC lead leaves the left outer port backwards; the split cable
    # loops between the two inner ports.
    parts.append(f'<path class="kb-cable kb-cable-pc" d="M {pcx:.1f} {-top:.1f} V {-top - 26:.1f}"/>')
    parts.append(f'<path class="kb-cable kb-cable-link" d="M {llx:.1f} {-top:.1f} C {llx:.1f} {-top - 34:.1f}, {rlx:.1f} {-top - 34:.1f}, {rlx:.1f} {-top:.1f}"/>')
    pc_box_y = -top - 44
    parts.append(f'<rect class="kb-pc" x="{pcx - 16:.1f}" y="{pc_box_y:.1f}" width="32" height="18" rx="3"/>'
                 f'<text class="kb-pc-text" x="{pcx:.1f}" y="{pc_box_y + 11.8:.1f}">PC</text>')
    for (x, _), n in ((p[("L", "pc")], 1), (p[("L", "link")], 2), (p[("R", "link")], 2)):
        parts.append(f'<rect class="kb-port" x="{x - 5:.1f}" y="{-top - 2.2:.1f}" width="10" height="4.4" rx="2.2"/>')
    badges = [(pcx + 12, -top - 14, "1"), ((llx + rlx) / 2, -top - 31, "2")]
    for x, y, n in badges:
        parts.append(f'<circle class="kb-badge" cx="{x:.1f}" cy="{y:.1f}" r="5.2"/><text class="kb-badge-text" x="{x:.1f}" y="{y + 2:.1f}">{n}</text>')
    parts.append(f'<text class="kb-front" x="0" y="{85 + 16:.1f}">↓ 사용자 쪽</text>')

    vb = f"-160 {-top - 50:.0f} 320 {top + 50 + 85 + 22:.0f}"
    svg = (f'<svg class="kb-diagram" viewBox="{vb}" role="img" aria-labelledby="kbTitle kbDesc" xmlns="http://www.w3.org/2000/svg">'
           '<title id="kbTitle">C86 왼쪽·오른쪽 키보드와 USB-C 포트 위치</title>'
           '<desc id="kbDesc">위에서 본 두 반쪽. 왼쪽 키보드 뒤쪽 바깥 모서리의 포트 1은 PC에 연결하고, '
           '왼쪽 뒤쪽 안쪽 모서리와 오른쪽 뒤쪽 안쪽 모서리의 포트 2끼리 USB-C 케이블로 연결합니다.</desc>'
           + "".join(parts) + "</svg>")
    html = INDEX.read_text(encoding="utf-8")
    new, n = re.subn(r"(<!-- keyboard-diagram:start -->).*?(<!-- keyboard-diagram:end -->)",
                     lambda m: m.group(1) + "\n" + svg + "\n" + m.group(2), html, flags=re.S)
    assert n == 1, "keyboard-diagram markers not found"
    INDEX.write_bytes(new.encode("utf-8"))
    print("ports (plate frame mm):", {k: tuple(round(v, 1) for v in xy) for k, xy in p.items()})
    print("diagram written:", len(svg), "bytes")


if __name__ == "__main__":
    render()
