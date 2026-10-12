// Gera as 8 imagens promocionais da Play Store (1080x1920) nos 3 idiomas:
// captura de store/screenshots/<idioma>_N_nome.png dentro de um celular, com
// cenário ilustrado (cemitério à noite) e título grande.
// Uso: node tools/make_store_promo.mjs   (precisa do Playwright; não usa o Godot)
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  ({ chromium } = await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright'));
}
const root = fileURLToPath(new URL('../', import.meta.url));
const b64 = (p) => readFileSync(root + p).toString('base64');
const shade = (hex, f) => {
  const n = parseInt(hex.slice(1), 16);
  const c = [n >> 16, (n >> 8) & 255, n & 255].map((v) => Math.max(0, Math.min(255, Math.round(v * f))));
  return `rgb(${c.join(',')})`;
};

// pasta de saída (idioma da ficha) -> prefixo das capturas
const SRC = { pt_BR: 'pt_BR', en_US: 'en_US', es_419: 'es_ES' };
const LANGS = Object.keys(SRC);
const OUT = 'store/promo';
const SHOT = (lang, shot) => `store/screenshots/${SRC[lang]}_${shot}.png`;
const FONTS_CSS = `
  @font-face{font-family:Body;font-weight:300 700;src:url(data:font/ttf;base64,${b64('art/fonts/Fredoka-Variable.ttf')}) format('truetype')}
  @font-face{font-family:Title;font-weight:300 700;src:url(data:font/ttf;base64,${b64('art/fonts/Fredoka-Variable.ttf')}) format('truetype')}`;
const TITLE = { ink: '#160b20', outline: '#f6e7c4', weight: 700, size: 130 };

// [captura, cenário, textos por idioma: [linha pequena, linha grande]]
const SLIDES = [
  ['1_hub', 0, { pt_BR: ['RPG de esqueleto', 'Monte seu corpo!'], en_US: ['Skeleton RPG', 'Build your body!'], es_419: ['RPG de esqueleto', '¡Arma tu cuerpo!'] }],
  ['2_ossuary', 1, { pt_BR: ['Melhorias e companheiros', 'Fique mais forte!'], en_US: ['Upgrades and companions', 'Grow stronger!'], es_419: ['Mejoras y compañeros', '¡Hazte más fuerte!'] }],
  ['3_collection', 2, { pt_BR: ['Ossos de monstros', 'Colecione todos!'], en_US: ['Monster bones', 'Collect them all!'], es_419: ['Huesos de monstruos', '¡Colecciónalos!'] }],
  ['4_shop', 3, { pt_BR: ['Ofertas do dia', 'Itens e relíquias!'], en_US: ['Daily deals', 'Items and relics!'], es_419: ['Ofertas del día', '¡Objetos y reliquias!'] }],
  ['5_combat', 4, { pt_BR: ['Combate por turnos', 'Lute na cripta!'], en_US: ['Turn-based combat', 'Fight in the crypt!'], es_419: ['Combate por turnos', '¡Lucha en la cripta!'] }],
  ['6_boss', 5, { pt_BR: ['Enfrente os chefes', 'Derrote o Rei Rato!'], en_US: ['Face the bosses', 'Defeat the Rat King!'], es_419: ['Enfrenta a los jefes', '¡Vence al Rey Rata!'] }],
  ['7_form', 6, { pt_BR: ['Combine os ossos', 'Formas secretas!'], en_US: ['Combine bones', 'Secret forms!'], es_419: ['Combina los huesos', '¡Formas secretas!'] }],
  ['8_card', 7, { pt_BR: ['Cada partida, um monstro', 'Compartilhe o seu!'], en_US: ['Every run, a new monster', 'Share yours!'], es_419: ['Cada partida, un monstruo', '¡Comparte el tuyo!'] }],
];

const R = 'rgba(200,170,255,.10)';
const SCENES = [
  { sky: ['#1b0f3a', '#5a2d82'], title: ['#fff6dc', '#ffb23f'], rays: R, glow: '#ffcf6b' },
  { sky: ['#0f1a3a', '#2d5a82'], title: ['#fff6dc', '#7fd6ff'], rays: R, glow: '#9fe3ff' },
  { sky: ['#0d2a2a', '#2d7a6a'], title: ['#fff6dc', '#7ce05c'], rays: R, glow: '#b6ff9c' },
  { sky: ['#2a0f2a', '#8a2d6a'], title: ['#fff6dc', '#ff9ad1'], rays: R, glow: '#ffc1e3' },
  { sky: ['#2a0d12', '#8a2d2d'], title: ['#fff6dc', '#ff6b3d'], rays: R, glow: '#ffb38a' },
  { sky: ['#1d0d33', '#6a2d9a'], title: ['#fff6dc', '#c38bff'], rays: R, glow: '#e0c2ff' },
  { sky: ['#140b2e', '#3d1f7a'], title: ['#f5e3ff', '#b25cff'], rays: R, glow: '#d7a6ff' },
  { sky: ['#1a1030', '#704a2d'], title: ['#fff6dc', '#ffc93c'], rays: R, glow: '#ffe08a' },
];

const BONE = '#f3e6c8';
function bone(s) {
  return `<svg width="${s}" height="${s / 2.6}" viewBox="0 0 130 50">
    <g fill="${BONE}" stroke="#8a7350" stroke-width="4">
      <circle cx="16" cy="14" r="12"/><circle cx="16" cy="36" r="12"/><circle cx="114" cy="14" r="12"/><circle cx="114" cy="36" r="12"/>
      <rect x="16" y="15" width="98" height="20" stroke="none"/></g>
    <path d="M18 15 H112 M18 35 H112" stroke="#8a7350" stroke-width="4"/></svg>`;
}
function skull(s, mood = 0) {
  return `<svg width="${s}" height="${s}" viewBox="0 0 100 100">
    <path d="M50 6 C78 6 92 26 92 48 C92 62 84 70 76 74 L76 86 C76 92 70 96 64 96 L36 96 C30 96 24 92 24 86 L24 74 C16 70 8 62 8 48 C8 26 22 6 50 6 Z" fill="${BONE}" stroke="#8a7350" stroke-width="4"/>
    <ellipse cx="33" cy="50" rx="12" ry="${mood ? 10 : 13}" fill="#231430"/><ellipse cx="67" cy="50" rx="12" ry="${mood ? 10 : 13}" fill="#231430"/>
    <circle cx="36" cy="46" r="4" fill="#fff"/><circle cx="70" cy="46" r="4" fill="#fff"/>
    <path d="M44 66 L50 58 L56 66 Z" fill="#231430"/>
    <path d="M36 80 V92 M46 80 V94 M54 80 V94 M64 80 V92" stroke="#8a7350" stroke-width="3"/>
    <path d="M30 26 Q40 16 52 16" stroke="#fff" stroke-width="5" fill="none" opacity=".6" stroke-linecap="round"/></svg>`;
}
// Mascote: caveirinha (Ossinho) com sorriso
function ossinho(s) {
  return `<svg width="${s}" height="${s}" viewBox="0 0 200 200">
    <ellipse cx="100" cy="192" rx="70" ry="8" fill="#000" opacity=".35"/>
    <path d="M100 14 C152 14 180 50 180 92 C180 118 166 132 150 140 L150 164 C150 178 140 186 126 186 L74 186 C60 186 50 178 50 164 L50 140 C34 132 20 118 20 92 C20 50 48 14 100 14 Z" fill="${BONE}" stroke="#8a7350" stroke-width="6"/>
    <ellipse cx="68" cy="98" rx="24" ry="26" fill="#231430"/><ellipse cx="132" cy="98" rx="24" ry="26" fill="#231430"/>
    <circle cx="74" cy="90" r="9" fill="#ffe28a"/><circle cx="138" cy="90" r="9" fill="#ffe28a"/>
    <circle cx="66" cy="106" r="4" fill="#fff" opacity=".7"/><circle cx="130" cy="106" r="4" fill="#fff" opacity=".7"/>
    <path d="M92 126 L100 114 L108 126 Z" fill="#231430"/>
    <path d="M70 146 Q100 168 130 146" stroke="#231430" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="M84 152 V164 M100 156 V168 M116 152 V164" stroke="#8a7350" stroke-width="4"/>
    <ellipse cx="44" cy="128" rx="10" ry="6" fill="#ff8aa8" opacity=".5"/><ellipse cx="156" cy="128" rx="10" ry="6" fill="#ff8aa8" opacity=".5"/>
    <path d="M56 44 Q76 26 100 26" stroke="#fff" stroke-width="8" fill="none" opacity=".6" stroke-linecap="round"/></svg>`;
}
// Mascote: Lumi, a vela fantasma
function lumi(s) {
  return `<svg width="${s}" height="${s * 1.25}" viewBox="0 0 160 200">
    <defs><radialGradient id="fl"><stop offset="0" stop-color="#fff6b0"/><stop offset=".5" stop-color="#ffb23f" stop-opacity=".6"/><stop offset="1" stop-color="#ffb23f" stop-opacity="0"/></radialGradient></defs>
    <circle cx="80" cy="26" r="34" fill="url(#fl)"/>
    <path d="M80 6 C90 20 92 30 80 42 C68 30 70 20 80 6 Z" fill="#ffd54a"/><path d="M80 20 C85 28 85 34 80 40 C75 34 75 28 80 20 Z" fill="#fff6b0"/>
    <path d="M80 44 C124 44 140 82 140 120 L140 180 L124 166 L110 184 L94 166 L80 184 L66 166 L50 184 L36 166 L20 180 L20 120 C20 82 36 44 80 44 Z" fill="#e9f3ff" stroke="#9fb6d8" stroke-width="5" opacity=".95"/>
    <ellipse cx="62" cy="110" rx="10" ry="14" fill="#231430"/><ellipse cx="98" cy="110" rx="10" ry="14" fill="#231430"/>
    <circle cx="65" cy="105" r="4" fill="#fff"/><circle cx="101" cy="105" r="4" fill="#fff"/>
    <ellipse cx="80" cy="138" rx="9" ry="7" fill="#231430"/>
    <ellipse cx="46" cy="130" rx="9" ry="5" fill="#ff8aa8" opacity=".5"/><ellipse cx="114" cy="130" rx="9" ry="5" fill="#ff8aa8" opacity=".5"/></svg>`;
}
function bat(s) {
  return `<svg width="${s}" height="${s / 2}" viewBox="0 0 100 50"><path d="M50 18 C46 10 40 8 34 12 C26 4 12 4 2 14 C12 16 16 22 18 30 C24 24 32 26 36 32 C40 26 46 28 50 36 C54 28 60 26 64 32 C68 26 76 24 82 30 C84 22 88 16 98 14 C88 4 74 4 66 12 C60 8 54 10 50 18 Z" fill="#0b0614" opacity=".85"/></svg>`;
}
function tomb(x, y, w, cross) {
  const h = w * 1.3;
  return cross
    ? `<g fill="#2a1d3a" stroke="#120a1c" stroke-width="5"><rect x="${x + w * 0.4}" y="${y - h}" width="${w * 0.2}" height="${h}"/><rect x="${x + w * 0.15}" y="${y - h * 0.75}" width="${w * 0.7}" height="${w * 0.2}"/></g>`
    : `<path d="M${x} ${y} V${y - h + w / 2} A${w / 2} ${w / 2} 0 0 1 ${x + w} ${y - h + w / 2} V${y} Z" fill="#3a2d4a" stroke="#120a1c" stroke-width="5"/><path d="M${x + w * 0.3} ${y - h * 0.55} H${x + w * 0.7} M${x + w * 0.5} ${y - h * 0.7} V${y - h * 0.3}" stroke="#1d1428" stroke-width="5"/>`;
}
function candle(x, y, h, glow) {
  return `<g><circle cx="${x + 12}" cy="${y - h - 14}" r="42" fill="${glow}" opacity=".25"/><rect x="${x}" y="${y - h}" width="24" height="${h}" rx="5" fill="#f3e6c8" stroke="#8a7350" stroke-width="3"/>
    <path d="M${x + 12} ${y - h - 30} C${x + 20} ${y - h - 18} ${x + 20} ${y - h - 8} ${x + 12} ${y - h - 4} C${x + 4} ${y - h - 8} ${x + 4} ${y - h - 18} ${x + 12} ${y - h - 30}Z" fill="#ffd54a"/></g>`;
}

function DECOR(idx, sc) {
  let stars = '';
  for (let i = 0; i < 70; i++) {
    const x = (i * 157 + idx * 61) % 1080, y = (i * 97 + idx * 29) % 1400, r = 1 + ((i * 7) % 3);
    stars += `<circle cx="${x}" cy="${y}" r="${r}" fill="#fff" opacity="${0.3 + ((i * 13) % 6) / 10}"/>`;
  }
  const moon = `<circle cx="975" cy="470" r="140" fill="${sc.glow}" opacity=".18"/><circle cx="975" cy="470" r="80" fill="#fff4d6"/><circle cx="950" cy="450" r="14" fill="#e8d8b0"/><circle cx="1000" cy="495" r="10" fill="#e8d8b0"/>`;
  // arcos góticos atrás do celular
  const arches = [[30, 1180, 230], [820, 1150, 240]].map(([x, y, w]) => `<path d="M${x} 1920 V${y} Q${x + w / 2} ${y - w * 0.9} ${x + w} ${y} V1920 Z" fill="#000" opacity=".22"/>`).join('');
  const hill = `<path d="M0 1500 C200 1430 360 1490 540 1460 C740 1420 880 1480 1080 1440 L1080 1920 L0 1920 Z" fill="#1a1028" opacity=".9"/>`;
  const tombs = tomb(40, 1520, 90) + tomb(150, 1500, 60, true) + tomb(930, 1500, 100) + tomb(860, 1490, 55, true);
  const back = `<svg class="abs" style="left:0;top:0" width="1080" height="1920">${stars}${moon}${arches}${hill}${tombs}</svg>
    ${[[100, 420, 110], [780, 540, 80], [880, 760, 120]].map(([x, y, s]) => `<div class="abs" style="left:${x}px;top:${y}px">${bat(s)}</div>`).join('')}
    ${[[70, 640, 150, -25], [960, 1000, 130, 30], [30, 1180, 120, 60]].map(([x, y, s, r]) => `<div class="fl" style="left:${x - s / 2}px;top:${y}px;transform:rotate(${r}deg)">${bone(s)}</div>`).join('')}
    ${[[70, 880, 100, -12], [1000, 650, 90, 14], [990, 1250, 80, -8]].map(([x, y, s, r], i) => `<div class="fl" style="left:${x - s / 2}px;top:${y}px;transform:rotate(${r}deg)">${skull(s, i % 2)}</div>`).join('')}`;
  const front = `<svg class="abs" style="left:0;top:0" width="1080" height="1920">
      <path d="M0 1780 C200 1750 400 1790 540 1770 C700 1750 880 1790 1080 1760 L1080 1920 L0 1920 Z" fill="#120a1c"/>
      ${candle(270, 1905, 60, sc.glow)}${candle(305, 1910, 40, sc.glow)}${candle(740, 1908, 52, sc.glow)}</svg>
    <div class="fl" style="left:440px;top:1830px;transform:rotate(-10deg)">${bone(120)}</div>
    <div class="fl" style="left:-10px;top:1640px">${ossinho(260)}</div>
    <div class="fl" style="right:0px;top:1610px;filter:drop-shadow(0 0 30px ${sc.glow})">${lumi(200)}</div>`;
  return { back, front };
}

// ---------------------------------------------------------------------------
// Montagem (igual para todos os jogos): cenário, título e celular com a captura
// ---------------------------------------------------------------------------
function page(lang, [shot, sceneIdx, texts]) {
  const [small, big] = texts[lang];
  const img = b64(SHOT(lang, shot));
  const sc = SCENES[sceneIdx];
  const { back, front } = DECOR(sceneIdx, sc);
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  ${FONTS_CSS}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:Body;background:linear-gradient(180deg,${sc.sky[0]} 0%,${sc.sky[1]} 62%)}
  .rays{position:absolute;left:50%;top:330px;width:2600px;height:2600px;margin:-1300px 0 0 -1300px;
    background:repeating-conic-gradient(${sc.rays ?? 'rgba(255,255,255,.16)'} 0 7deg,rgba(255,255,255,0) 7deg 18deg);
    -webkit-mask:radial-gradient(circle,#000 0,#000 25%,transparent 55%);mask:radial-gradient(circle,#000 0,#000 25%,transparent 55%)}
  .abs{position:absolute}
  .fl{position:absolute;filter:drop-shadow(0 10px 12px rgba(0,0,0,.3))}
  .title{position:absolute;top:70px;left:40px;right:40px;text-align:center;z-index:5}
  .t1,.t2{display:block;white-space:nowrap;line-height:1.08;letter-spacing:1px}
  .t1{font-family:Body;font-weight:700;font-size:96px;color:#fff;-webkit-text-stroke:14px ${TITLE.ink};paint-order:stroke fill;text-shadow:0 8px 0 ${TITLE.ink}}
  .t2{font-family:Title;font-weight:${TITLE.weight};font-size:${TITLE.size}px;margin-top:6px;position:relative}
  .t2 .s{position:absolute;inset:0;color:${TITLE.ink};-webkit-text-stroke:22px ${TITLE.ink};transform:translateY(10px)}
  .t2 .o{position:absolute;inset:0;color:${TITLE.outline};-webkit-text-stroke:22px ${TITLE.outline}}
  .t2 .f{position:relative;background:linear-gradient(180deg,${sc.title[0]} 15%,${sc.title[1]} 85%);-webkit-background-clip:text;background-clip:text;color:transparent}
  .phone{position:absolute;left:50%;top:445px;width:732px;height:1340px;margin-left:-366px;border-radius:92px;z-index:4;
    background:linear-gradient(145deg,#4a4f60,#15171f 40%,#2b2f3b);padding:22px;
    box-shadow:0 40px 80px rgba(5,10,30,.5),inset 0 0 0 3px rgba(255,255,255,.18)}
  .screen{width:100%;height:100%;border-radius:72px;overflow:hidden;background:#111;position:relative}
  .screen img{display:block;width:100%;height:100%;object-fit:cover}
  .btn{position:absolute;right:-8px;width:8px;border-radius:0 6px 6px 0;background:#2a2e3a}
  .front{position:absolute;inset:0;z-index:6;pointer-events:none}
  </style></head><body>
  <div class="rays"></div>
  ${back}
  <div class="title"><span class="t1" id="t1">${small}</span><span class="t2" id="t2"><span class="s">${big}</span><span class="o">${big}</span><span class="f">${big}</span></span></div>
  <div class="phone"><div class="btn" style="top:260px;height:120px"></div><div class="btn" style="top:420px;height:200px"></div>
    <div class="screen"><img src="data:image/png;base64,${img}"></div></div>
  <div class="front">${front}</div>
  <script>
    // Reduz a fonte se o texto não couber na largura
    for (const id of ['t1','t2']) { const el = document.getElementById(id); let fs = parseFloat(getComputedStyle(el).fontSize);
      const inner = id === 't2' ? el.querySelector('.f') : el;
      while (inner.getBoundingClientRect().width > 960 && fs > 40) { fs -= 2; el.style.fontSize = fs + 'px'; } }
  </script>
  </body></html>`;
}

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const pg = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
for (const lang of LANGS) {
  mkdirSync(`${root}${OUT}/${lang}`, { recursive: true });
  for (const s of SLIDES) {
    await pg.setContent(page(lang, s));
    await pg.evaluate(() => document.fonts.ready);
    await pg.screenshot({ path: `${root}${OUT}/${lang}/${s[0]}.png` });
    console.log(lang, s[0]);
  }
}
await browser.close();
