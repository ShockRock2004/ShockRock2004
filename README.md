<div align="center">

<img src="assets/hero.svg" alt="ShockRock2004 — agentic AI, voice AI and telephony" width="100%" />

<br/>

<img src="https://img.shields.io/badge/IIT_Madras-final_year-A78BFA?style=flat-square&labelColor=0B0F14" alt="IIT Madras final year" />
<img src="https://img.shields.io/badge/focus-agentic_AI_&_voice-22D3EE?style=flat-square&labelColor=0B0F14" alt="focus" />
<img src="https://img.shields.io/github/stars/ShockRock2004/kamar-taj?style=flat-square&logo=github&label=kamar-taj&color=5EEAD4&labelColor=0B0F14" alt="kamar-taj stars" />
<img src="https://img.shields.io/badge/open_to-SDE_roles_2026-34D399?style=flat-square&labelColor=0B0F14" alt="open to SDE roles 2026" />

</div>

---

## About

Final year undergraduate at IIT Madras, working on systems that put language models to real work rather than demos.

Most of my time goes to two things. Building agentic workflows where an LLM has tools, state and a verification loop instead of a single prompt. And real time voice, where a model has to hold a conversation over a phone line inside a latency budget that does not forgive mistakes.

I have production experience with telephony infrastructure: FreeSWITCH dialplans, SIP trunking, WebRTC and Verto signalling, codec negotiation between G.711 and Opus, call supervision, and forking live call audio into AI agents. That work sits in private repositories, so this profile shows the public side.

---

## Focus areas

| Area | What that means in practice |
|---|---|
| **Agentic AI workflows** | Giving models tools, memory and a verification step. Making the loop reliable enough that the output can be trusted without reading every line. |
| **Voice AI and telephony** | Streaming speech pipelines over SIP and WebRTC. Turn detection, barge in, codec negotiation, and keeping a conversational turn under budget. |
| **Applying LLMs to real problems** | Evaluating where automation actually holds up, and where it quietly fails. Building the harness before trusting the model. |

---

## Real time voice agent pipeline

The architecture I work in and keep rebuilding. The interesting engineering is not the model call. It is everything around it that has to happen inside roughly 800 milliseconds.

<div align="center">

<img src="assets/voice-pipeline.svg" alt="Real time voice agent pipeline with latency budget" width="100%" />

</div>

Two things dominate the budget and neither is speech processing. Turn detection has to decide the caller actually stopped talking, and the model has to produce its first token. Everything else is streaming and can be overlapped.

---

## Core CS foundations

Currently working through the fundamentals in parallel with building.

<div align="center">

<img src="assets/foundations.svg" alt="System design, networking, operating systems, DBMS, DSA and competitive programming" width="100%" />

</div>

---

## Tech

<div align="center">

<img src="https://skillicons.dev/icons?i=python,ts,js,react,nodejs&theme=dark" alt="languages and frameworks" />

<br/>

<img src="https://skillicons.dev/icons?i=postgres,supabase,docker,linux,git,vercel&theme=dark" alt="data and infrastructure" />

<br/><br/>

<img src="https://img.shields.io/badge/FreeSWITCH-0B0F14?style=for-the-badge&logoColor=22D3EE&color=0B0F14&labelColor=0B0F14" alt="FreeSWITCH" />
<img src="https://img.shields.io/badge/SIP-0B0F14?style=for-the-badge&color=0B0F14&labelColor=0B0F14" alt="SIP" />
<img src="https://img.shields.io/badge/WebRTC-333333?style=for-the-badge&logo=webrtc&logoColor=white&labelColor=0B0F14&color=0B0F14" alt="WebRTC" />
<img src="https://img.shields.io/badge/LLM_agents-0B0F14?style=for-the-badge&color=0B0F14&labelColor=0B0F14" alt="LLM agents" />
<img src="https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logo=anthropic&logoColor=white&labelColor=0B0F14&color=0B0F14" alt="Anthropic" />

</div>

---

## Selected work

### [kamar-taj](https://github.com/ShockRock2004/kamar-taj) &nbsp;·&nbsp; Python

Agent tooling for Claude Code. Three skills that address a specific failure mode of coding agents: one turns a day of AI assisted work into a readable study guide, one refuses to call a bug fixed until it has watched the test pass, and one sends the work to a second model to argue against it.

Built because reviewing agent output by reading every diff does not scale. Starred by developers outside my network.

### [grindz](https://github.com/ShockRock2004/grindz) &nbsp;·&nbsp; TypeScript

A workout tracker running as a React Native Android app and an installable PWA against one Supabase backend and an image CDN. Shipped to a real device with a signed APK, which is where the interesting bugs live.

### [Lodestar](https://github.com/ShockRock2004/Lodestar) &nbsp;·&nbsp; JavaScript

A study tracking system with a React and Vite dashboard plus an Expo Android client on a shared Supabase backend.

---

## Activity

<div align="center">

<img src="https://github-readme-stats-sigma-five.vercel.app/api?username=ShockRock2004&show_icons=true&include_all_commits=true&count_private=true&hide_border=true&bg_color=0B0F14&title_color=22D3EE&icon_color=A78BFA&text_color=9FB3C8&ring_color=22D3EE" alt="GitHub statistics" height="165" />
<img src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=ShockRock2004&theme=github_dark" alt="most committed languages" height="165" />

<br/><br/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=ShockRock2004&bg_color=0B0F14&color=9FB3C8&line=22D3EE&point=A78BFA&area=true&area_color=22D3EE&hide_border=true&custom_title=commits%20over%20time" alt="commit activity" width="100%" />

</div>

---

## Contact

<div align="center">

<a href="mailto:chardave2004@gmail.com">
  <img src="https://img.shields.io/badge/email-chardave2004@gmail.com-22D3EE?style=for-the-badge&logo=gmail&logoColor=white&labelColor=0B0F14" alt="email" />
</a>
<a href="https://grindz.dev">
  <img src="https://img.shields.io/badge/grindz.dev-live-34D399?style=for-the-badge&logo=vercel&logoColor=white&labelColor=0B0F14" alt="grindz.dev" />
</a>

</div>
