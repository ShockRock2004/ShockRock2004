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

# --- panel geometry -------------------------------------------------------
PITCH = 5          # px between dot centres
ROWS = 15          # hanzi and kana need this much to stay legible
COLS = 86
X0, Y0 = 717, 102  # top left dot centre; clear of the wordmark and lede
DOT_R = 1.5
SS = 8             # supersample factor used when rasterising glyphs
INK = 0.38         # coverage above which a grid cell counts as lit
CUR_GAP = 1        # columns between the text and the caret
CUR_W = 4          # caret width in columns
CUR_H = 2          # caret height in rows, sitting on the baseline

# --- animation ------------------------------------------------------------
SLOT = 3.2         # seconds each greeting owns
TYPE = 0.13        # seconds between characters
CLEAR = 0.45       # blank tail before the next greeting

CJK = "C:/Windows/Fonts/msyh.ttc"      # Microsoft YaHei: latin, cyrillic, greek, kana, hanzi
KOREAN = "C:/Windows/Fonts/malgun.ttf"  # Malgun Gothic: hangul

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


def main(out):
    cycle = SLOT * len(GREETINGS)
    pct = lambda t: round(100 * t / cycle, 3)

    groups, keyframes = [], []
    for w, (text, lang, path) in enumerate(GREETINGS):
        chars, cursors = rasterise(text, path)
        base = w * SLOT
        off = base + SLOT - CLEAR

        parts = []
        for i, dots in enumerate(chars):
            on = base + i * TYPE
            name = f"c{w}_{i}"
            keyframes.append(
                f"      @keyframes {name} {{ 0%{{opacity:0}} {pct(on)}%{{opacity:1}} "
                f"{pct(off)}%{{opacity:0}} 100%{{opacity:0}} }}"
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

        # cursor block advances one position per character, then holds until clear
        for i, col in enumerate(cursors):
            on = base + i * TYPE
            end = base + (i + 1) * TYPE if i < len(cursors) - 1 else off
            name = f"k{w}_{i}"
            keyframes.append(
                f"      @keyframes {name} {{ 0%{{opacity:0}} {pct(on)}%{{opacity:1}} "
                f"{pct(end)}%{{opacity:0}} 100%{{opacity:0}} }}"
            )
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

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="280" viewBox="0 0 1200 280" role="img" aria-label="ShockRock2004. Agentic AI, voice AI and LLM systems. Final year at IIT Madras. Open to SDE roles, graduating 2027.">
  <title>ShockRock2004</title>

  <defs>
    <pattern id="panel" width="{PITCH}" height="{PITCH}" patternUnits="userSpaceOnUse">
      <circle cx="{X0 % PITCH}" cy="{Y0 % PITCH}" r="1.0" fill="#15212B"/>
    </pattern>

    <filter id="led" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <style>
      .mono {{ font-family: ui-monospace, "Cascadia Mono", "Cascadia Code", "JetBrains Mono",
               "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace; }}

      .kicker {{ font-size: 11.5px; letter-spacing: 3px; fill: #55636F; }}
      .status {{ font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
                 font-size: 10.5px; font-weight: 700; letter-spacing: 1.4px; fill: #34D399; }}
      .lede   {{ font-size: 14px; fill: #7C8B9A; }}
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

  <rect x="0.5" y="0.5" width="1199" height="279" rx="14" fill="#0B0F14" stroke="#1B2733"/>

  <!-- dot matrix panel : hello, typed out in seven languages -->
  <rect x="{X0 - PITCH / 2}" y="{Y0 - PITCH / 2}" width="{COLS * PITCH}" height="{ROWS * PITCH}" fill="url(#panel)"/>
  <g id="hello" fill="#38BDF8" filter="url(#led)">
{chr(10).join(groups)}
  </g>

  <!-- top strip -->
  <g class="in">
    <text class="mono kicker" x="40" y="45">AGENTIC AI &#160;&#183;&#160; VOICE AI &#160;&#183;&#160; LLM SYSTEMS</text>

    <rect x="1020" y="28" width="140" height="26" rx="13" fill="#0C1A17" stroke="#1E3A34"/>
    <circle class="dot" cx="1040" cy="41" r="3.5" fill="#34D399"/>
    <text class="status" x="1054" y="45">OPEN TO WORK</text>
  </g>

  <line x1="40" y1="68" x2="1160" y2="68" stroke="#16202B"/>

  <!-- wordmark -->
  <g class="in" style="animation-delay:.08s">
    <text class="mono" x="40" y="142" font-size="52" font-weight="700" letter-spacing="-1" fill="#E6EDF3">ShockRock<tspan fill="#22D3EE">2004</tspan></text>
    <rect x="40" y="160" width="56" height="3" rx="1.5" fill="#22D3EE"/>
  </g>

  <g class="in" style="animation-delay:.16s">
    <text class="mono lede" x="40" y="192">final year at IIT Madras &#160;&#183;&#160; agentic systems and real time voice</text>
  </g>

  <!-- spec strip -->
  <line x1="40" y1="218" x2="1160" y2="218" stroke="#16202B"/>

  <g class="in" style="animation-delay:.24s">
    <line x1="305" y1="226" x2="305" y2="264" stroke="#16202B"/>
    <line x1="595" y1="226" x2="595" y2="264" stroke="#16202B"/>
    <line x1="885" y1="226" x2="885" y2="264" stroke="#16202B"/>

    <text class="mono lbl" x="40"  y="238">STACK</text>
    <text class="mono val" x="40"  y="257">C++ &#183; JavaScript &#183; Python</text>

    <text class="mono lbl" x="330" y="238">SHIPPED</text>
    <text class="mono val" x="330" y="257">grindz.dev</text>

    <text class="mono lbl" x="620" y="238">LEARNING</text>
    <text class="mono val" x="620" y="257">systems &#183; networks &#183; DSA</text>

    <text class="mono lbl" x="910" y="238">GRADUATING</text>
    <text class="mono val" x="910" y="257">2027</text>
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
    print(f"bytes {len(svg)}")


if __name__ == "__main__":
    main(sys.argv[1])
