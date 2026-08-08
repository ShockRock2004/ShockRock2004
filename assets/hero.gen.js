// Generates assets/hero.svg. The dot-matrix panel is too many primitives to
// hand-place, so the lit-dot geometry is derived from a 5x7 bitmap font here.
const fs = require("fs");

const FONT = {
  A: ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
  B: ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
  C: ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
  E: ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
  H: ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
  I: ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
  J: ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
  L: ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
  N: ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
  O: ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
  P: ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
  R: ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
  T: ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
  U: ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
  V: ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
};

// hello, in six world languages
const WORDS = ["HELLO", "HOLA", "BONJOUR", "HALLO", "CIAO", "PRIVET"];
const LANGS = ["english", "spanish", "french", "german", "italian", "russian"];

const PITCH = 7;
const COLS = 45; // widest word is 7 glyphs = 41 columns, plus padding
const ROWS = 7;
const X0 = 810; // panel centred on x=964, clear of the lede text
const Y0 = 110;

const litDots = (word) => {
  const w = word.length * 5 + (word.length - 1); // 1 blank column between glyphs
  const start = Math.floor((COLS - w) / 2);
  const out = [];
  word.split("").forEach((ch, i) => {
    const rows = FONT[ch];
    if (!rows) throw new Error(`no glyph for ${ch}`);
    rows.forEach((bits, r) =>
      bits.split("").forEach((bit, c) => {
        if (bit === "1") out.push([start + i * 6 + c, r]);
      })
    );
  });
  return out;
};

const SLOT = 2.6; // seconds each word holds the panel
const SLOTPCT = 100 / WORDS.length; // each word owns one slot of the cycle
const groups = WORDS.map((word, i) => {
  const dots = litDots(word)
    .map(([c, r]) => `<circle cx="${X0 + c * PITCH}" cy="${Y0 + r * PITCH}" r="2.1"/>`)
    .join("");
  return (
    `    <g class="hw" opacity="${i === 0 ? 1 : 0}" style="animation-delay:${(i * SLOT).toFixed(1)}s" ` +
    `aria-label="${word.toLowerCase()}, ${LANGS[i]}">${dots}</g>`
  );
}).join("\n");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="280" viewBox="0 0 1200 280" role="img" aria-label="ShockRock2004. Agentic AI, voice AI and LLM systems. Final year at IIT Madras. Open to SDE roles, graduating 2027.">
  <title>ShockRock2004</title>

  <defs>
    <pattern id="panel" width="${PITCH}" height="${PITCH}" patternUnits="userSpaceOnUse">
      <circle cx="${X0 % PITCH}" cy="${Y0 % PITCH}" r="1.4" fill="#16232E"/>
    </pattern>

    <filter id="led" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <style>
      .sans { font-family: "Inter", "Segoe UI Variable Display", "Segoe UI", -apple-system,
              BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif; }
      .mono { font-family: ui-monospace, "Cascadia Code", "JetBrains Mono", Consolas, monospace; }

      .kicker { font-size: 11.5px; letter-spacing: 3px; fill: #55636F; }
      .status { font-size: 10.5px; font-weight: 700; letter-spacing: 1.4px; fill: #34D399; }
      .lede   { font-size: 14px; fill: #7C8B9A; }
      .lbl    { font-size: 9.5px; letter-spacing: 2px; fill: #46525E; }
      .val    { font-size: 12.5px; fill: #C6D2DE; }

      /* base state is the finished state. animations run FROM hidden via fill-mode both,
         so a renderer that ignores CSS animation still shows a complete banner. the first
         hello carries opacity="1" as an attribute for the same reason. */
      .in { animation: in .7s cubic-bezier(.2,.7,.3,1) both; }
      @keyframes in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

      .dot { animation: dot 2.8s ease-in-out infinite; }
      @keyframes dot { 0%, 100% { opacity: .4; } 50% { opacity: 1; } }

      .hw { animation: hw ${(WORDS.length * SLOT).toFixed(1)}s steps(1, end) infinite; }
      @keyframes hw {
        0%    { opacity: 0; }
        ${(SLOTPCT * 0.08).toFixed(2)}%  { opacity: 1; }
        ${(SLOTPCT * 0.92).toFixed(2)}% { opacity: 1; }
        ${SLOTPCT.toFixed(2)}% { opacity: 0; }
        100%  { opacity: 0; }
      }
    </style>
  </defs>

  <rect x="0.5" y="0.5" width="1199" height="279" rx="14" fill="#0B0F14" stroke="#1B2733"/>

  <!-- dot matrix panel : hello, cycling through languages -->
  <rect x="${X0 - PITCH / 2}" y="${Y0 - PITCH / 2}" width="${(COLS - 1) * PITCH + PITCH}" height="${(ROWS - 1) * PITCH + PITCH}" fill="url(#panel)"/>
  <g fill="#38BDF8" filter="url(#led)">
${groups}
  </g>

  <!-- top strip -->
  <g class="in">
    <text class="mono kicker" x="40" y="45">AGENTIC AI &#160;&#183;&#160; VOICE AI &#160;&#183;&#160; LLM SYSTEMS</text>

    <rect x="1020" y="28" width="140" height="26" rx="13" fill="#0C1A17" stroke="#1E3A34"/>
    <circle class="dot" cx="1040" cy="41" r="3.5" fill="#34D399"/>
    <text class="sans status" x="1054" y="45">OPEN TO WORK</text>
  </g>

  <line x1="40" y1="68" x2="1160" y2="68" stroke="#16202B"/>

  <!-- wordmark -->
  <g class="in" style="animation-delay:.08s">
    <text class="sans" x="40" y="142" font-size="60" font-weight="700" letter-spacing="-1.5" fill="#E6EDF3">ShockRock<tspan fill="#22D3EE">2004</tspan></text>
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
`;

fs.writeFileSync(process.argv[2], svg);
console.log("words:", WORDS.join(", "));
console.log("lit dots per word:", WORDS.map((w) => litDots(w).length).join(", "));
console.log("bytes:", svg.length);
