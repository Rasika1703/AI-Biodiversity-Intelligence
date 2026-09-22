import { HeroArt, Scene } from '../illustrations.jsx';

const CHIPS = [
  { icon: '🌾', label: 'Monoculture on degraded soil', prompt: 'I farm 40 ha of monoculture wheat on degraded soil. Soil organic carbon is about 0.3% and pH is 8.4. What should I do to bring biodiversity back?' },
  { icon: '🌊', label: 'Wetland species are declining', prompt: 'Species around the wetland on my land are declining — frogs and waders have mostly disappeared. There is cropland right up to the water edge and fertiliser runoff from upstream.' },
  { icon: '🏜️', label: 'Semi-arid land with low rainfall', prompt: 'My land is in a semi-arid region with roughly 420 mm of erratic rainfall a year. Soil moisture is low and I have almost no tree cover. How do I improve biodiversity here?' },
  { icon: '🌳', label: 'Forest fragmentation concern', prompt: 'The forest patch next to my farm has been broken into small fragments by roads and clearing. Tree cover is down to about 22%. What interventions actually help?' },
  { icon: '🐝', label: 'Pollinator populations falling', prompt: 'Bee and butterfly numbers on my farm have dropped sharply over three seasons. I apply pesticide on a calendar schedule and there is very little natural habitat left nearby.' },
  { icon: '💧', label: 'Water stress affecting habitat', prompt: 'Water stress is affecting habitat on my land — the seasonal stream now dries by March and irrigation is borehole-only. Soil is sandy and moisture is low.' },
];

const STRIP = [
  { scene: 'soil', title: 'Soil health', sub: 'SOC, pH, moisture' },
  { scene: 'pollinator', title: 'Biodiversity', sub: 'richness, pollinators' },
  { scene: 'water', title: 'Water', sub: 'rainfall, quality' },
  { scene: 'forest', title: 'Land use', sub: 'cover, fragmentation' },
];

export default function Hero({ onPick, busy }) {
  return (
    <div className="hero">
      <div className="hero-art">
        <HeroArt />
      </div>
      <h1>
        Ask an <em>AI Environmental Scientist</em>
      </h1>
      <p>
        Describe your land, ecosystem, or environmental concern. Get evidence-backed,
        multi-variable biodiversity recommendations grounded in FAO, IPCC, and IUCN research.
      </p>

      <div className="chip-grid">
        {CHIPS.map((c) => (
          <button key={c.label} className="chip" disabled={busy} onClick={() => onPick(c.prompt)}>
            <span>{c.icon}</span>
            <span>{c.label}</span>
          </button>
        ))}
      </div>

      <div className="hero-strip">
        {STRIP.map((s) => (
          <figure className="strip-card" key={s.title}>
            <Scene name={s.scene} />
            <figcaption>
              <b>{s.title}</b>
              <small>{s.sub}</small>
            </figcaption>
          </figure>
        ))}
      </div>
    </div>
  );
}
