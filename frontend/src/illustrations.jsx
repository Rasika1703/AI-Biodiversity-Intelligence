/**
 * All imagery is drawn as inline SVG rather than loaded from a CDN.
 * Reason: the app has to render identically offline, on a locked-down demo
 * machine and behind a strict content policy — a broken photo placeholder in a
 * scientific report reads as a broken product.
 */

export function Logo({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" role="img" aria-label="Darukaa.Earth">
      <circle cx="24" cy="24" r="23" fill="#eaf7f0" />
      <path d="M24 9c6 4.4 9.4 9.4 9.4 14.4 0 5.6-4.2 9.6-9.4 9.6s-9.4-4-9.4-9.6C14.6 18.4 18 13.4 24 9Z" fill="#23a96c" />
      <path d="M24 9c6 4.4 9.4 9.4 9.4 14.4 0 5.6-4.2 9.6-9.4 9.6V9Z" fill="#137048" />
      <rect x="22.7" y="27" width="2.6" height="13" rx="1.3" fill="#8a6a45" />
      <path d="M12 40c4-2.6 8-3.9 12-3.9s8 1.3 12 3.9" stroke="#8fd9b6" strokeWidth="2.4" strokeLinecap="round" fill="none" />
    </svg>
  );
}

export function HeroArt() {
  return (
    <svg viewBox="0 0 200 200" width="100%" height="100%" role="img" aria-label="A tree beside water under the sun">
      <defs>
        <linearGradient id="hg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f3fbf7" />
          <stop offset="100%" stopColor="#e2f4ea" />
        </linearGradient>
        <linearGradient id="canopy" x1="0.2" y1="0" x2="0.9" y2="1">
          <stop offset="0%" stopColor="#3cc084" />
          <stop offset="100%" stopColor="#137048" />
        </linearGradient>
      </defs>
      <circle cx="100" cy="100" r="96" fill="url(#hg)" stroke="#c9ead9" strokeWidth="2" />
      <circle cx="146" cy="56" r="10" fill="#f2c97a" />
      <path d="M40 74c5-5 11-5 16 0" stroke="#9fd9bd" strokeWidth="2.6" strokeLinecap="round" fill="none" />
      <path d="M100 52c21 16 32 32 32 47 0 19-14 31-32 31S68 118 68 99c0-15 11-31 32-47Z" fill="url(#canopy)" />
      <path d="M86 78c7 6 11 13 12 21" stroke="#8fd9b6" strokeWidth="2" strokeLinecap="round" fill="none" opacity="0.75" />
      <rect x="96" y="124" width="8" height="34" rx="4" fill="#8a6a45" />
      <path d="M100 138c-7-4-12-5-18-5M100 146c7-4 12-5 18-5" stroke="#8a6a45" strokeWidth="3" strokeLinecap="round" fill="none" />
      <ellipse cx="100" cy="160" rx="62" ry="12" fill="#d5efe2" />
      <path d="M52 160c8-4 16-4 24 0M124 162c8-4 16-4 24 0" stroke="#8fd9b6" strokeWidth="2.6" strokeLinecap="round" fill="none" />
      <circle cx="66" cy="150" r="3.4" fill="#23a96c" />
      <circle cx="138" cy="152" r="3" fill="#2d7fa8" />
      <path d="M60 128c2-6 6-9 12-10" stroke="#23a96c" strokeWidth="2.4" strokeLinecap="round" fill="none" />
    </svg>
  );
}

const base = { width: '100%', height: '100%', preserveAspectRatio: 'xMidYMid slice' };

const SCENES = {
  semiarid: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Semi-arid cropland with scattered trees">
      <rect width="160" height="110" fill="#fdf6e8" />
      <circle cx="132" cy="24" r="12" fill="#f2c97a" />
      <path d="M0 74h160v36H0z" fill="#e8d7b4" />
      <path d="M0 74c22-8 46-8 68 0s58 8 92 0v10H0z" fill="#d9c294" />
      <g stroke="#b79a63" strokeWidth="1.6" strokeLinecap="round">
        <path d="M12 96h136M8 104h144" />
      </g>
      <path d="M44 74c0-14 7-23 16-23s16 9 16 23z" fill="#3f8f63" />
      <rect x="58" y="70" width="4" height="14" rx="2" fill="#8a6a45" />
      <path d="M104 74c0-9 5-15 11-15s11 6 11 15z" fill="#4f9e72" />
      <rect x="113" y="71" width="3" height="11" rx="1.5" fill="#8a6a45" />
      <g fill="#c7a86d">
        <rect x="18" y="62" width="2" height="12" rx="1" />
        <rect x="26" y="60" width="2" height="14" rx="1" />
        <rect x="34" y="63" width="2" height="11" rx="1" />
        <rect x="88" y="61" width="2" height="13" rx="1" />
        <rect x="96" y="64" width="2" height="10" rx="1" />
      </g>
    </svg>
  ),
  wetland: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Wetland with reeds and open water">
      <rect width="160" height="110" fill="#eaf5f9" />
      <circle cx="34" cy="24" r="11" fill="#f5dfa6" />
      <path d="M0 62h160v48H0z" fill="#bfe0ef" />
      <path d="M0 62c26 6 52-6 80 0s54 6 80-2v12H0z" fill="#a4d3e8" />
      <g stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" opacity="0.8">
        <path d="M18 80h26M60 88h30M104 76h24M30 96h40" />
      </g>
      <g stroke="#3f8f63" strokeWidth="2.2" strokeLinecap="round" fill="none">
        <path d="M14 62V38M22 62V44M30 62V34M124 62V40M132 62V46M140 62V36" />
      </g>
      <g fill="#7a5c3a">
        <rect x="12.5" y="34" width="3" height="8" rx="1.5" />
        <rect x="28.5" y="30" width="3" height="8" rx="1.5" />
        <rect x="122.5" y="36" width="3" height="8" rx="1.5" />
        <rect x="138.5" y="32" width="3" height="8" rx="1.5" />
      </g>
      <path d="M72 58c4-3 9-3 12 0-3 4-9 4-12 0Z" fill="#2d7fa8" />
      <path d="M92 66c3-2 7-2 9 0-2 3-7 3-9 0Z" fill="#2d7fa8" opacity="0.7" />
    </svg>
  ),
  forest: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Forest canopy layers">
      <rect width="160" height="110" fill="#eef8f2" />
      <path d="M0 80h160v30H0z" fill="#cfe9da" />
      <g fill="#2f7d55">
        <path d="M24 80 40 36l16 44z" />
        <path d="M96 80 112 30l16 50z" />
      </g>
      <g fill="#46a06f">
        <path d="M4 80 18 46l14 34z" />
        <path d="M60 80 76 42l16 38z" />
        <path d="M128 80l14-32 14 32z" />
      </g>
      <g fill="#8a6a45">
        <rect x="38" y="76" width="4" height="12" rx="2" />
        <rect x="110" y="76" width="4" height="12" rx="2" />
        <rect x="74" y="78" width="3" height="10" rx="1.5" />
      </g>
      <g stroke="#8fd9b6" strokeWidth="2" strokeLinecap="round" fill="none">
        <path d="M10 96c10-4 20-4 30 0M60 100c12-5 24-5 36 0M112 94c10-4 20-4 30 0" />
      </g>
    </svg>
  ),
  grassland: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Grassland with grazing animals">
      <rect width="160" height="110" fill="#f4faf0" />
      <circle cx="136" cy="22" r="10" fill="#f2c97a" />
      <path d="M0 68c30-10 60-10 90-2s46 8 70 0v44H0z" fill="#cfe6b8" />
      <path d="M0 84c34-8 62-6 90 2s46 6 70-2v26H0z" fill="#b6d99a" />
      <g stroke="#7fae63" strokeWidth="1.6" strokeLinecap="round" fill="none">
        <path d="M14 84v-9M20 85v-12M26 84v-8M120 82v-10M126 83v-13M132 82v-9" />
      </g>
      <g fill="#6b5744">
        <ellipse cx="68" cy="72" rx="11" ry="6" />
        <rect x="60" y="74" width="2.6" height="8" rx="1.3" />
        <rect x="74" y="74" width="2.6" height="8" rx="1.3" />
        <circle cx="80" cy="67" r="4.4" />
      </g>
      <g fill="#8a7460">
        <ellipse cx="102" cy="78" rx="8" ry="4.4" />
        <rect x="97" y="80" width="2" height="6" rx="1" />
        <rect x="106" y="80" width="2" height="6" rx="1" />
        <circle cx="110" cy="75" r="3.2" />
      </g>
    </svg>
  ),
  pollinator: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Flowering strip with bees">
      <rect width="160" height="110" fill="#fdf7ec" />
      <path d="M0 78h160v32H0z" fill="#d9ecc9" />
      <g stroke="#5b9e5f" strokeWidth="2" strokeLinecap="round" fill="none">
        <path d="M24 78V54M48 78V48M72 78V58M96 78V50M120 78V56M140 78V60" />
      </g>
      <circle cx="24" cy="50" r="6" fill="#e8a0b8" />
      <circle cx="48" cy="44" r="7" fill="#f0c25c" />
      <circle cx="72" cy="54" r="5.5" fill="#b49ad8" />
      <circle cx="96" cy="46" r="6.5" fill="#f0c25c" />
      <circle cx="120" cy="52" r="6" fill="#e8a0b8" />
      <circle cx="140" cy="56" r="5" fill="#9fd0e8" />
      <g>
        <ellipse cx="62" cy="28" rx="5.4" ry="3.6" fill="#e0a83c" />
        <path d="M59 28h6" stroke="#4a3618" strokeWidth="1.6" />
        <ellipse cx="60" cy="24" rx="4" ry="2.2" fill="#ffffff" opacity="0.85" />
      </g>
      <g>
        <ellipse cx="110" cy="22" rx="4.4" ry="3" fill="#e0a83c" />
        <path d="M107.6 22h4.8" stroke="#4a3618" strokeWidth="1.4" />
        <ellipse cx="108.4" cy="19" rx="3.2" ry="1.8" fill="#ffffff" opacity="0.85" />
      </g>
      <path d="M40 22c6-5 12-5 18 0" stroke="#cbb79a" strokeWidth="1.4" strokeDasharray="3 4" fill="none" />
    </svg>
  ),
  soil: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Soil profile with roots and organic matter">
      <rect width="160" height="110" fill="#f7f3ea" />
      <path d="M0 30h160v22H0z" fill="#8c6a46" />
      <path d="M0 52h160v26H0z" fill="#a98a63" />
      <path d="M0 78h160v32H0z" fill="#c2a985" />
      <path d="M0 22h160v10H0z" fill="#4e9a6b" />
      <g stroke="#e8dcc6" strokeWidth="1.6" strokeLinecap="round" fill="none">
        <path d="M30 32v22c0 8-6 10-6 18M30 40c6 2 9 6 10 12M30 48c-6 2-9 6-10 12" />
        <path d="M96 32v20c0 8 6 11 6 20M96 42c-6 2-9 6-10 12M96 50c6 2 9 6 10 12" />
      </g>
      <g fill="#6b4f34" opacity="0.6">
        <circle cx="52" cy="62" r="2.4" />
        <circle cx="70" cy="70" r="2" />
        <circle cx="120" cy="60" r="2.6" />
        <circle cx="138" cy="72" r="2" />
      </g>
      <path d="M58 86c8-4 14-1 14 5s-8 8-14 4" stroke="#d9b7a0" strokeWidth="3" strokeLinecap="round" fill="none" />
      <g stroke="#3f8f63" strokeWidth="2.4" strokeLinecap="round" fill="none">
        <path d="M30 22V10M96 22V12" />
      </g>
      <circle cx="30" cy="9" r="4" fill="#4e9a6b" />
      <circle cx="96" cy="11" r="3.4" fill="#4e9a6b" />
    </svg>
  ),
  water: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Contour bunds holding water on a slope">
      <rect width="160" height="110" fill="#f2f9fb" />
      <path d="M0 40c40-14 80-14 120 0s40 10 40 10v60H0z" fill="#d7e9d2" />
      <g stroke="#7fae63" strokeWidth="2.6" strokeLinecap="round" fill="none">
        <path d="M6 58c36-12 72-12 108 0M2 76c40-13 80-13 120 0M0 94c44-14 88-14 132 0" />
      </g>
      <g stroke="#6fb6d8" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.85">
        <path d="M18 62c30-9 60-9 90 0M14 80c34-10 68-10 102 0" />
      </g>
      <circle cx="132" cy="24" r="10" fill="#f2c97a" />
      <g fill="#6fb6d8">
        <path d="M44 20c2 3 3.4 5 3.4 6.6a3.4 3.4 0 1 1-6.8 0C40.6 25 42 23 44 20Z" />
        <path d="M62 14c2 3 3.4 5 3.4 6.6a3.4 3.4 0 1 1-6.8 0C58.6 19 60 17 62 14Z" opacity="0.7" />
      </g>
    </svg>
  ),
  landscape: (
    <svg viewBox="0 0 160 110" {...base} role="img" aria-label="Mosaic landscape of fields, hedges and woodland">
      <rect width="160" height="110" fill="#f4f9f3" />
      <path d="M0 46h160v64H0z" fill="#dcecd0" />
      <path d="M0 46h64v28H0z" fill="#c8e2b8" />
      <path d="M64 46h96v20H64z" fill="#d6ead0" />
      <path d="M0 74h94v36H0z" fill="#cde6c0" />
      <path d="M94 66h66v44H94z" fill="#c2e0b4" />
      <g stroke="#3f8f63" strokeWidth="3" strokeLinecap="round" fill="none">
        <path d="M0 74h94M94 66v44M64 46v28" />
      </g>
      <g fill="#2f7d55">
        <circle cx="20" cy="88" r="7" />
        <circle cx="34" cy="92" r="5" />
        <circle cx="120" cy="80" r="8" />
        <circle cx="134" cy="86" r="5.5" />
      </g>
      <path d="M0 34c24-8 48-8 72 0s64 6 88-2" stroke="#9fd0e8" strokeWidth="3" fill="none" strokeLinecap="round" />
    </svg>
  ),
};

export function Scene({ name = 'landscape', className = '' }) {
  return <div className={className}>{SCENES[name] || SCENES.landscape}</div>;
}

/** Map a recommendation's tags to the most fitting scene. */
export function sceneForTags(tags = []) {
  const t = tags.join(' ');
  if (t.includes('wetland') || t.includes('hydrology')) return 'wetland';
  if (t.includes('water quality')) return 'water';
  if (t.includes('pollinator')) return 'pollinator';
  if (t.includes('forest') || t.includes('restoration')) return 'forest';
  if (t.includes('grass') || t.includes('graz')) return 'grassland';
  if (t.includes('landscape') || t.includes('connectivity') || t.includes('habitat')) return 'landscape';
  if (t.includes('water')) return 'water';
  if (t.includes('soil') || t.includes('carbon') || t.includes('chemistry')) return 'soil';
  return 'semiarid';
}
