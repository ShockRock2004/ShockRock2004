"""Generates assets/hero.svg.

The hero's right hand side is an LED dot matrix panel that types out "hello" in
seven languages, in their own scripts. Rendering CJK and Cyrillic as dots means
knowing which grid cells fall inside each glyph, so the glyphs are rasterised
here at build time and the SVG ships only circles. Nothing depends on the
viewer having a Chinese, Japanese or Korean font installed.

    python assets/hero_gen.py assets/hero.svg
"""

import sys
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib import instancer

# --- panel geometry -------------------------------------------------------
PITCH = 5          # px between dot centres
ROWS = 15          # hanzi and kana need this much to stay legible
COLS = 86
X0, Y0 = 717, 84   # top left dot centre; clear of the wordmark
DOT_R = 1.6
SS = 8             # supersample factor used when rasterising glyphs
INK = 0.38         # coverage above which a grid cell counts as lit
CUR_GAP = 1        # columns between the text and the caret
CUR_W = 4          # caret width in columns
CUR_H = 2          # caret height in rows, sitting on the baseline

# --- animation ------------------------------------------------------------
SLOT = 3.2         # seconds each greeting owns
TYPE = 0.13        # seconds between characters
CLEAR = 0.45       # blank tail before the next greeting
ERASE = 0.07       # seconds per character when backspacing the word away
BEZEL = 6          # padding between the dot grid and the panel frame

CJK = "C:/Windows/Fonts/msyh.ttc"      # Microsoft YaHei: latin, cyrillic, greek, kana, hanzi
KOREAN = "C:/Windows/Fonts/malgun.ttf"  # Malgun Gothic: hangul

# --- wordmark -------------------------------------------------------------
# Shipped as outlines rather than a font-family, so the wordmark is the same
# face for every viewer instead of resolving to whatever they happen to have.
WM_FONT = "C:/Windows/Fonts/bahnschrift.ttf"  # DIN-style, technical, not a terminal face
WM_WEIGHT = 600     # bahnschrift is variable (wght 300-700); default 400 reads too light
WM_TEXT = "ShockRock2004"
WM_SPLIT = 9        # "ShockRock" | "2004"
WM_SIZE = 54
WM_X, WM_BASE = 40, 128
WM_TRACK = -0.6     # px of extra tracking per glyph

GREETINGS = [
    ("HELLO", "english", CJK),
    ("\u4f60\u597d", "chinese", CJK),
    ("\u3053\u3093\u306b\u3061\u306f", "japanese", CJK),
    ("\uc548\ub155\ud558\uc138\uc694", "korean", KOREAN),
    ("\u041f\u0440\u0438\u0432\u0435\u0442", "russian", CJK),
    ("Hola", "spanish", CJK),
    ("Bonjour", "french", CJK),
]


def fit_font(text, path):
    """Largest font size whose rendering of `text` fits the dot grid."""
    box_w, box_h = (COLS - 2) * SS, ROWS * SS
    best = None
    for size in range(6, ROWS * SS + 24):
        font = ImageFont.truetype(path, size)
        l, t, r, b = font.getbbox(text)
        if r - l <= box_w and b - t <= box_h:
            best = (font, l, t, r, b)
        else:
            break
    if best is None:
        raise SystemExit(f"cannot fit {text!r}")
    return best


def rasterise(text, path):
    """Return (per-character dot lists, per-position cursor columns)."""
    font, bl, bt, br, bb = fit_font(text, path)
    W, H = COLS * SS, ROWS * SS
    total = br - bl
    x_start = (W - total) / 2 - bl
    # centre the ink box vertically inside the grid
    y_start = (H - (bb - bt)) / 2 - bt

    chars = []
    for i, ch in enumerate(text):
        img = Image.new("L", (W, H), 0)
        ImageDraw.Draw(img).text(
            (x_start + font.getlength(text[:i]), y_start), ch, font=font, fill=255
        )
        px = img.load()
        dots = []
        for r in range(ROWS):
            for c in range(COLS):
                acc = 0
                for dy in range(SS):
                    for dx in range(SS):
                        acc += px[c * SS + dx, r * SS + dy]
                if acc / (SS * SS * 255) >= INK:
                    dots.append((c, r))
        chars.append(dots)

    cursors = [
        max(0, min(COLS - CUR_W, round((x_start + bl + font.getlength(text[:i])) / SS) + CUR_GAP))
        for i in range(len(text) + 1)
    ]
    return chars, cursors


def keyframe(name, stops):
    """Build a keyframe from (time_percent, opacity) stops.

    CSS needs strictly increasing offsets, so collapse any that collide after
    rounding rather than emitting a rule the browser will silently drop.
    """
    clean = []
    for t, v in stops:
        if clean and t <= clean[-1][0]:
            # same offset after rounding: the later value wins. dropping it
            # instead silently deletes the turn-on stop for anything starting
            # at t=0, which is how the first glyph of the first word went dark.
            clean[-1] = (clean[-1][0], v)
        else:
            clean.append((t, v))
    if not any(v for _, v in clean):
        raise SystemExit(f"{name} never becomes visible: {stops}")
    body = " ".join(f"{t}%{{opacity:{v}}}" for t, v in clean)
    return f"      @keyframes {name} {{ {body} }}"


def wordmark():
    """Outline the wordmark, split into two differently coloured runs.

    Returns (path_for_name, path_for_year, total_advance).
    """
    font = TTFont(WM_FONT, fontNumber=0)
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": WM_WEIGHT})
    upem = font["head"].unitsPerEm
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    widths = font["hmtx"]
    scale = WM_SIZE / upem

    pens = [SVGPathPen(glyphs), SVGPathPen(glyphs)]
    cursor = 0.0
    for i, ch in enumerate(WM_TEXT):
        name = cmap[ord(ch)]
        # y is flipped: font outlines grow upward, SVG grows downward
        target = TransformPen(
            pens[0 if i < WM_SPLIT else 1],
            (scale, 0, 0, -scale, WM_X + cursor, WM_BASE),
        )
        glyphs[name].draw(target)
        cursor += widths[name][0] * scale + WM_TRACK
    return pens[0].getCommands(), pens[1].getCommands(), cursor


def main(out):
    cycle = SLOT * len(GREETINGS)
    pct = lambda t: round(100 * t / cycle, 3)

    groups, keyframes = [], []
    for w, (text, lang, path) in enumerate(GREETINGS):
        chars, cursors = rasterise(text, path)
        base = w * SLOT
        n = len(chars)
        erase_at = base + SLOT - CLEAR - n * ERASE  # backspacing starts here

        parts = []
        for i, dots in enumerate(chars):
            on = base + i * TYPE
            # the last character is deleted first
            off = erase_at + (n - 1 - i) * ERASE
            name = f"c{w}_{i}"
            keyframes.append(
                keyframe(name, [(0, 0), (pct(on), 1), (pct(off), 0), (100, 0)])
            )
            # r is a geometry property and does not inherit from the parent <g>,
            # so every circle carries it explicitly
            d = "".join(
                f'<circle cx="{X0 + c * PITCH}" cy="{Y0 + r * PITCH}" r="{DOT_R}"/>'
                for c, r in dots
            )
            # first greeting stays lit without CSS, so a renderer that ignores
            # animation still shows a complete panel
            vis = 1 if w == 0 else 0
            parts.append(f'<g opacity="{vis}" style="animation-name:{name}">{d}</g>')

        # caret advances one column per character while typing, then retreats
        # back through the same positions as the word is deleted
        for i, col in enumerate(cursors):
            name = f"k{w}_{i}"
            if i < n:
                stops = [
                    (0, 0),
                    (pct(base + i * TYPE), 1),
                    (pct(base + (i + 1) * TYPE), 0),
                    (pct(erase_at + (n - 1 - i) * ERASE), 1),
                    (pct(erase_at + (n - i) * ERASE), 0),
                    (100, 0),
                ]
            else:
                # parked at the end of the finished word until the delete starts
                stops = [(0, 0), (pct(base + n * TYPE), 1), (pct(erase_at), 0), (100, 0)]
            keyframes.append(keyframe(name, stops))
            # underscore caret rather than a block, so it never reads as an "l"
            blk = "".join(
                f'<circle cx="{X0 + (col + dc) * PITCH}" cy="{Y0 + r * PITCH}" r="{DOT_R}"/>'
                for dc in range(CUR_W)
                for r in range(ROWS - CUR_H, ROWS)
            )
            vis = 1 if w == 0 and i == 0 else 0
            parts.append(
                f'<g class="cur" opacity="{vis}" style="animation-name:{name}">'
                f'<g class="blink">{blk}</g></g>'
            )

        groups.append(
            f'    <g aria-label="{text} ({lang})">\n      ' + "\n      ".join(parts) + "\n    </g>"
        )

    wm_name, wm_year, wm_adv = wordmark()

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="238" viewBox="0 0 1200 238" role="img" aria-label="ShockRock2004. Stack C++, JavaScript, Python. Shipped grindz.dev. Open to SDE roles, graduating 2027.">
  <title>ShockRock2004</title>

  <defs>
    <pattern id="panel" width="{PITCH}" height="{PITCH}" patternUnits="userSpaceOnUse">
      <circle cx="{X0 % PITCH}" cy="{Y0 % PITCH}" r="1.1" fill="#1C2B37"/>
    </pattern>

    <filter id="led" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="1.3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <style>
      .mono {{ font-family: ui-monospace, "Cascadia Mono", "Cascadia Code", "JetBrains Mono",
               "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace; }}

      .status {{ font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
                 font-size: 10.5px; font-weight: 700; letter-spacing: 1.4px; fill: #34D399; }}
      .lbl    {{ font-size: 9.5px; letter-spacing: 2px; fill: #46525E; }}
      .val    {{ font-size: 12.5px; fill: #C6D2DE; }}

      /* base state is the finished state. the fade runs FROM hidden via fill-mode
         both, and the first greeting carries opacity="1" as an attribute, so a
         renderer that ignores CSS animation still shows a complete banner. */
      .in {{ animation: in .7s cubic-bezier(.2,.7,.3,1) both; }}
      @keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}

      .dot {{ animation: dot 2.8s ease-in-out infinite; }}
      @keyframes dot {{ 0%, 100% {{ opacity: .4; }} 50% {{ opacity: 1; }} }}

      #hello g {{ animation-duration: {cycle}s; animation-timing-function: steps(1, end);
                 animation-iteration-count: infinite; }}
      .blink {{ animation: blink .9s steps(1, end) infinite !important; }}
      @keyframes blink {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: .12; }} }}

{chr(10).join(keyframes)}
    </style>
  </defs>

  <rect x="0.5" y="0.5" width="1199" height="237" rx="14" fill="#0B0F14" stroke="#1B2733"/>

  <!-- dot matrix panel : hello, typed out in seven languages -->
  <rect x="{X0 - PITCH / 2 - BEZEL}" y="{Y0 - PITCH / 2 - BEZEL}" width="{COLS * PITCH + BEZEL * 2}" height="{ROWS * PITCH + BEZEL * 2}" rx="8" fill="#0D151C" stroke="#1B2733"/>
  <rect x="{X0 - PITCH / 2}" y="{Y0 - PITCH / 2}" width="{COLS * PITCH}" height="{ROWS * PITCH}" fill="url(#panel)"/>
  <g id="hello" fill="#38BDF8" filter="url(#led)">
{chr(10).join(groups)}
  </g>

  <!-- status -->
  <g class="in">
    <rect x="1020" y="26" width="140" height="26" rx="13" fill="#0C1A17" stroke="#1E3A34"/>
    <circle class="dot" cx="1040" cy="39" r="3.5" fill="#34D399"/>
    <text class="status" x="1054" y="43">OPEN TO WORK</text>
  </g>

  <line x1="40" y1="66" x2="1160" y2="66" stroke="#16202B"/>

  <!-- wordmark, shipped as outlines so the face is identical for every viewer -->
  <g class="in" style="animation-delay:.08s">
    <path d="{wm_name}" fill="#E6EDF3"/>
    <path d="{wm_year}" fill="#22D3EE"/>
    <rect x="{WM_X}" y="144" width="56" height="3" rx="1.5" fill="#22D3EE"/>
  </g>

  <!-- spec strip -->
  <line x1="40" y1="172" x2="1160" y2="172" stroke="#16202B"/>

  <g class="in" style="animation-delay:.16s">
    <line x1="305" y1="180" x2="305" y2="218" stroke="#16202B"/>
    <line x1="595" y1="180" x2="595" y2="218" stroke="#16202B"/>
    <line x1="885" y1="180" x2="885" y2="218" stroke="#16202B"/>

    <text class="mono lbl" x="40"  y="192">STACK</text>
    <text class="mono val" x="40"  y="211">C++ &#183; JavaScript &#183; Python</text>

    <text class="mono lbl" x="330" y="192">SHIPPED</text>
    <text class="mono val" x="330" y="211">grindz.dev</text>

    <text class="mono lbl" x="620" y="192">LEARNING</text>
    <text class="mono val" x="620" y="211">systems &#183; networks &#183; DSA</text>

    <text class="mono lbl" x="910" y="192">GRADUATING</text>
    <text class="mono val" x="910" y="211">2027</text>
  </g>
</svg>
'''
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)

    # stdout may be cp1252 on Windows, so report codepoints rather than glyphs
    print(f"cycle {cycle:.1f}s over {len(GREETINGS)} greetings")
    for text, lang, _ in GREETINGS:
        cps = " ".join(f"U+{ord(c):04X}" for c in text)
        print(f"  {lang:9} {len(text)} chars  {cps}")
    print(f"wordmark advance {wm_adv:.1f}px, ends at x={WM_X + wm_adv:.0f} (panel starts {X0 - PITCH/2:.0f})")
    print(f"bytes {len(svg)}")


if __name__ == "__main__":
    main(sys.argv[1])
