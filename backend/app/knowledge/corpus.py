"""
Darukaa.Earth — curated environmental evidence corpus.

Every document is a short, dense, citable evidence card drawn from peer-reviewed
literature and institutional reports (FAO, IPCC, IUCN, UNCCD, CBD and journals).
Effect sizes are indicative ranges reported in the cited work; they are meant to
support reasoning and expectation-setting, not to replace site-level measurement.

Schema per document
-------------------
id           stable identifier, cited in every recommendation
title        short human-readable title
source       publisher / journal + report name
authors      author string or institution
year         publication year
url          public landing page or DOI
tier         "institutional" | "peer_reviewed" | "meta_analysis"
variables    environmental variables the document speaks to
biomes       biomes / contexts where the evidence applies
metrics      metrics the intervention moves
text         the retrievable chunk
"""

from __future__ import annotations

from typing import Any, Dict, List

DOCUMENTS: List[Dict[str, Any]] = [
    # ---------------------------------------------------------------- soil carbon
    {
        "id": "FAO-SOC-2017",
        "title": "Soil organic carbon: the hidden potential",
        "source": "FAO — Global Soil Partnership",
        "authors": "Food and Agriculture Organization of the United Nations",
        "year": 2017,
        "url": "https://www.fao.org/documents/card/en/c/25eaf720-94e4-4f53-8f50-cdfc2487e1f8/",
        "tier": "institutional",
        "variables": ["soil_organic_carbon", "soil_health", "land_use"],
        "biomes": ["all"],
        "metrics": ["soil_organic_carbon", "water_holding_capacity", "microbial_diversity"],
        "text": (
            "Soil organic carbon (SOC) governs aggregate stability, nutrient cycling and water retention. "
            "FAO reports that each 1% increase in soil organic matter (roughly 0.58% SOC) raises plant-available "
            "water holding capacity by approximately 15-20 mm per metre of soil profile. Croplands under continuous "
            "tillage and residue removal typically hold 0.2-0.8% SOC in semi-arid zones, against 1.5-3% under "
            "perennial cover. Restoring SOC is described as the single highest-leverage soil intervention because it "
            "simultaneously improves fertility, drought buffering and habitat for soil fauna. FAO estimates global "
            "cropland SOC sequestration potential of 0.4-1.2 Gt C per year under improved management."
        ),
    },
    {
        "id": "LAL-2004-SCIENCE",
        "title": "Soil carbon sequestration impacts on global climate change and food security",
        "source": "Science, 304(5677), 1623-1627",
        "authors": "Lal, R.",
        "year": 2004,
        "url": "https://doi.org/10.1126/science.1097396",
        "tier": "peer_reviewed",
        "variables": ["soil_organic_carbon", "yield", "climate"],
        "biomes": ["drylands", "semi_arid", "temperate_cropland"],
        "metrics": ["soil_organic_carbon", "yield", "erosion"],
        "text": (
            "Lal reports that raising soil organic carbon in the root zone of degraded cropland by 1 tonne per hectare "
            "per year increases food-crop yields by 20-40 kg/ha for wheat and 10-20 kg/ha for maize under rainfed "
            "conditions. Degraded dryland soils have lost 30-60% of their antecedent carbon pool and therefore carry "
            "the largest re-sequestration deficit, typically 0.3-0.5 t C/ha/yr recoverable through residue retention, "
            "cover cropping, manuring and agroforestry. The paper emphasises that carbon gains saturate after 20-50 "
            "years and are reversible if tillage or residue removal resume."
        ),
    },
    {
        "id": "POEPLAU-DON-2015",
        "title": "Carbon sequestration in agricultural soils via cultivation of cover crops — a meta-analysis",
        "source": "Agriculture, Ecosystems & Environment, 200, 33-41",
        "authors": "Poeplau, C. & Don, A.",
        "year": 2015,
        "url": "https://doi.org/10.1016/j.agee.2014.10.024",
        "tier": "meta_analysis",
        "variables": ["cover_crops", "soil_organic_carbon"],
        "biomes": ["temperate_cropland", "semi_arid", "subtropical"],
        "metrics": ["soil_organic_carbon", "nitrogen", "microbial_diversity"],
        "text": (
            "A meta-analysis of 139 plots found cover cropping raised topsoil organic carbon by a mean of 0.32 +/- 0.08 "
            "t C/ha/yr, equivalent to a 15-25% relative SOC increase in low-carbon soils over 2-4 years, with a new "
            "equilibrium reached after roughly 155 years. Legume cover crops added biologically fixed nitrogen of "
            "30-100 kg N/ha/yr, reducing synthetic fertiliser demand. Effects were largest where baseline SOC was low "
            "(<1%), which is precisely the condition of degraded semi-arid cropland."
        ),
    },
    {
        "id": "BOSSIO-2020-NATSUS",
        "title": "The role of soil carbon in natural climate solutions",
        "source": "Nature Sustainability, 3, 391-398",
        "authors": "Bossio, D. A. et al.",
        "year": 2020,
        "url": "https://doi.org/10.1038/s41893-020-0491-z",
        "tier": "peer_reviewed",
        "variables": ["soil_organic_carbon", "restoration", "climate"],
        "biomes": ["all"],
        "metrics": ["soil_organic_carbon", "carbon_sequestration"],
        "text": (
            "Soil carbon represents 25% of the potential of natural climate solutions, of which 40% comes from "
            "protecting existing soil carbon and 60% from rebuilding depleted stocks. The authors show that "
            "protection of intact soils is cheaper and lower-risk than restoration, so sequencing matters: stop "
            "further loss (no-till, residue retention, avoided wetland drainage) before investing in rebuilding."
        ),
    },
    # ---------------------------------------------------------------- agroforestry
    {
        "id": "ZOMER-2016-SCIREP",
        "title": "Global tree cover and biomass carbon on agricultural land",
        "source": "Scientific Reports, 6, 29987",
        "authors": "Zomer, R. J. et al.",
        "year": 2016,
        "url": "https://doi.org/10.1038/srep29987",
        "tier": "peer_reviewed",
        "variables": ["agroforestry", "tree_cover", "land_use"],
        "biomes": ["semi_arid", "tropical", "subtropical"],
        "metrics": ["carbon_sequestration", "habitat_diversity", "microclimate"],
        "text": (
            "Trees on agricultural land store 45% of above-ground carbon on farms globally; between 2000 and 2010 "
            "carbon on agricultural land increased by 2 Gt, largely through increased on-farm tree cover. Scattered "
            "farm trees at 30-80 stems/ha add 0.3-1.5 t C/ha/yr above ground and generate understorey microclimates "
            "2-5 degrees C cooler at midday, reducing evaporative demand on associated crops."
        ),
    },
    {
        "id": "KUYAH-2019-AGROFOR",
        "title": "Agroforestry delivers a win-win solution for ecosystem services in sub-Saharan Africa",
        "source": "Agronomy for Sustainable Development, 39, 47",
        "authors": "Kuyah, S. et al.",
        "year": 2019,
        "url": "https://doi.org/10.1007/s13593-019-0589-8",
        "tier": "meta_analysis",
        "variables": ["agroforestry", "soil_organic_carbon", "erosion", "yield"],
        "biomes": ["semi_arid", "tropical", "drylands"],
        "metrics": ["soil_organic_carbon", "erosion", "yield", "water_infiltration"],
        "text": (
            "Synthesis of 126 studies: agroforestry increased soil organic carbon by 21% on average, total soil "
            "nitrogen by 46%, reduced soil erosion by 50% and increased water infiltration by 60% relative to "
            "treeless cropland. Faidherbia albida parkland systems increased associated cereal yields by 6-56% "
            "because of reverse phenology, which drops nitrogen-rich litter at the start of the rains and casts "
            "little shade during grain fill."
        ),
    },
    {
        "id": "IPCC-SRCCL-2019",
        "title": "Special Report on Climate Change and Land (SRCCL), Chapter 6: Interlinkages",
        "source": "IPCC",
        "authors": "Intergovernmental Panel on Climate Change",
        "year": 2019,
        "url": "https://www.ipcc.ch/srccl/",
        "tier": "institutional",
        "variables": ["land_use", "desertification", "climate", "food_security"],
        "biomes": ["drylands", "semi_arid", "all"],
        "metrics": ["carbon_sequestration", "land_degradation", "water_availability"],
        "text": (
            "IPCC assesses agroforestry, cover crops and integrated water management as land-based response options "
            "with high confidence for both mitigation and adaptation and few adverse side effects. Dryland regions "
            "face compounding risk: warming raises evaporative demand while rainfall becomes more variable, so "
            "practices that increase infiltration and reduce soil evaporation have larger relative value than in "
            "humid zones. The report warns that single-practice interventions deliver limited benefit compared with "
            "bundles combining vegetation cover, water retention and reduced disturbance."
        ),
    },
    {
        "id": "IPCC-AR6-WGII-CH5",
        "title": "AR6 Working Group II, Chapter 5: Food, Fibre and Other Ecosystem Products",
        "source": "IPCC Sixth Assessment Report",
        "authors": "Intergovernmental Panel on Climate Change",
        "year": 2022,
        "url": "https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-5/",
        "tier": "institutional",
        "variables": ["climate", "rainfall", "temperature", "yield", "biodiversity"],
        "biomes": ["all"],
        "metrics": ["yield_stability", "species_richness", "water_availability"],
        "text": (
            "AR6 reports with high confidence that diversified cropping systems reduce yield variability under "
            "climate extremes. Observed wheat yield losses of 6% per degree C of warming are partly offset in "
            "diversified and shaded systems. Pollinator-dependent crop production is at risk where wild pollinator "
            "richness declines; 5-8% of current global crop production is directly attributable to animal pollination."
        ),
    },
    # ---------------------------------------------------------------- diversification
    {
        "id": "TAMBURINI-2020-SCIADV",
        "title": "Agricultural diversification promotes multiple ecosystem services without compromising yield",
        "source": "Science Advances, 6(45), eaba1715",
        "authors": "Tamburini, G. et al.",
        "year": 2020,
        "url": "https://doi.org/10.1126/sciadv.aba1715",
        "tier": "meta_analysis",
        "variables": ["crop_diversification", "biodiversity", "yield", "soil_health"],
        "biomes": ["all"],
        "metrics": ["species_richness", "soil_organic_carbon", "pest_control", "yield"],
        "text": (
            "Meta-analysis of 5,160 studies across 41 countries: diversification practices (crop rotation, "
            "intercropping, cover crops, agroforestry, field-margin habitat) enhanced biodiversity by 24%, "
            "pollination by 14%, pest control by 19%, water regulation by 51% and soil fertility by 11%, while yields "
            "were maintained or slightly increased in 63% of cases. Benefits were strongest when two or more "
            "diversification practices were combined, confirming that bundled interventions outperform single actions."
        ),
    },
    {
        "id": "BEILLOUIN-2021-GCB",
        "title": "Positive but variable effects of crop diversification on biodiversity and ecosystem services",
        "source": "Global Change Biology, 27(19), 4697-4710",
        "authors": "Beillouin, D., Ben-Ari, T., Malezieux, E., Seufert, V. & Makowski, D.",
        "year": 2021,
        "url": "https://doi.org/10.1111/gcb.15747",
        "tier": "meta_analysis",
        "variables": ["crop_diversification", "biodiversity"],
        "biomes": ["all"],
        "metrics": ["species_richness", "soil_organic_carbon", "yield"],
        "text": (
            "Umbrella review of 95 meta-analyses covering 5,156 experiments: crop diversification increased "
            "associated biodiversity by a median of 23% and soil quality indicators by 11-21%. Variability was high, "
            "and the authors attribute much of it to baseline landscape complexity: the same practice yields large "
            "biodiversity gains in simplified landscapes (<20% semi-natural cover) and small gains in already "
            "complex landscapes."
        ),
    },
    {
        "id": "PYWELL-2015-PRSB",
        "title": "Wildlife-friendly farming increases crop yield: evidence for ecological intensification",
        "source": "Proceedings of the Royal Society B, 282, 20151740",
        "authors": "Pywell, R. F. et al.",
        "year": 2015,
        "url": "https://doi.org/10.1098/rspb.2015.1740",
        "tier": "peer_reviewed",
        "variables": ["field_margins", "pollinators", "yield"],
        "biomes": ["temperate_cropland"],
        "metrics": ["pollinator_abundance", "yield", "habitat_diversity"],
        "text": (
            "Removing 3-8% of the least productive field area and converting it to wildflower and grass margins "
            "raised yields in the remaining cropped area enough to offset the land taken out, with total field yield "
            "rising up to 35% for pollinator-dependent crops after five years. The result reframes habitat strips as "
            "a production input rather than a production cost."
        ),
    },
    # ---------------------------------------------------------------- pollinators
    {
        "id": "GARIBALDI-2013-SCIENCE",
        "title": "Wild pollinators enhance fruit set of crops regardless of honey bee abundance",
        "source": "Science, 339(6127), 1608-1611",
        "authors": "Garibaldi, L. A. et al.",
        "year": 2013,
        "url": "https://doi.org/10.1126/science.1230200",
        "tier": "peer_reviewed",
        "variables": ["pollinators", "biodiversity", "yield"],
        "biomes": ["all"],
        "metrics": ["pollinator_abundance", "yield"],
        "text": (
            "Across 600 fields and 41 crop systems, wild-insect visitation increased fruit set twice as effectively "
            "as honey bee visitation, and honey bees supplemented rather than substituted for wild pollinators. "
            "Fruit set increased with wild pollinator richness in 96% of systems. Restoring wild pollinator "
            "communities therefore requires habitat and nesting resources, not managed hives."
        ),
    },
    {
        "id": "BLAAUW-ISAACS-2014",
        "title": "Flower plantings increase wild bee abundance and the pollination services provided to a pollination-dependent crop",
        "source": "Journal of Applied Ecology, 51(4), 890-898",
        "authors": "Blaauw, B. R. & Isaacs, R.",
        "year": 2014,
        "url": "https://doi.org/10.1111/1365-2664.12257",
        "tier": "peer_reviewed",
        "variables": ["pollinators", "field_margins"],
        "biomes": ["temperate_cropland"],
        "metrics": ["pollinator_abundance", "yield"],
        "text": (
            "Native wildflower plantings adjacent to blueberry fields raised wild bee abundance progressively over "
            "four years; by years 3-4 adjacent crop yield increases exceeded the establishment cost of the planting. "
            "Plantings needed at least 15 species with overlapping bloom windows spanning early, mid and late season "
            "to support a full pollinator community rather than a single guild."
        ),
    },
    {
        "id": "RICKETTS-2008-ECOLLETT",
        "title": "Landscape effects on crop pollination services: are there general patterns?",
        "source": "Ecology Letters, 11(5), 499-515",
        "authors": "Ricketts, T. H. et al.",
        "year": 2008,
        "url": "https://doi.org/10.1111/j.1461-0248.2008.01157.x",
        "tier": "meta_analysis",
        "variables": ["pollinators", "habitat_fragmentation", "distance"],
        "biomes": ["all"],
        "metrics": ["pollinator_abundance", "pollination_service"],
        "text": (
            "Pollinator richness and visitation decline exponentially with distance from natural habitat; visitation "
            "halves at roughly 0.6 km and richness halves at roughly 1.5 km in tropical systems. The practical "
            "implication is spacing: habitat patches or flowering strips should sit within 150-500 m of any point in "
            "the production area for most solitary bees, whose foraging range is 150-600 m."
        ),
    },
    {
        "id": "SANCHEZBAYO-2019-BIOCON",
        "title": "Worldwide decline of the entomofauna: a review of its drivers",
        "source": "Biological Conservation, 232, 8-27",
        "authors": "Sanchez-Bayo, F. & Wyckhuys, K. A. G.",
        "year": 2019,
        "url": "https://doi.org/10.1016/j.biocon.2019.01.020",
        "tier": "peer_reviewed",
        "variables": ["pollinators", "pollution", "pesticides", "land_use"],
        "biomes": ["all"],
        "metrics": ["insect_biomass", "pollinator_abundance"],
        "text": (
            "Review of 73 long-term datasets: insect biomass declining at roughly 2.5% per year, with habitat loss "
            "from intensive agriculture the leading driver, followed by agro-chemical pollution, introduced species "
            "and climate change. Neonicotinoid and fipronil residues in soil and water are singled out as chronic "
            "sublethal stressors. Reducing chemical load is identified as the fastest-acting lever because insect "
            "populations rebound within 1-3 generations when exposure stops."
        ),
    },
    # ---------------------------------------------------------------- soil biology
    {
        "id": "BARDGETT-2014-NATURE",
        "title": "Belowground biodiversity and ecosystem functioning",
        "source": "Nature, 515, 505-511",
        "authors": "Bardgett, R. D. & van der Putten, W. H.",
        "year": 2014,
        "url": "https://doi.org/10.1038/nature13855",
        "tier": "peer_reviewed",
        "variables": ["soil_biodiversity", "soil_organic_carbon", "microbial_diversity"],
        "biomes": ["all"],
        "metrics": ["microbial_diversity", "nutrient_cycling", "soil_organic_carbon"],
        "text": (
            "Soil hosts roughly 25% of described species. Microbial and faunal diversity regulate decomposition, "
            "nutrient mineralisation and plant community composition. Plant diversity above ground drives microbial "
            "diversity below ground through root exudate chemistry, so monocultures narrow the soil food web even "
            "where total microbial biomass is maintained by fertiliser inputs. Mycorrhizal networks extend effective "
            "root surface area by up to 100-fold and are suppressed by high phosphorus fertilisation and tillage."
        ),
    },
    {
        "id": "FAO-ITPS-SOILBIO-2020",
        "title": "State of knowledge of soil biodiversity",
        "source": "FAO / ITPS / GSBI / CBD / EC",
        "authors": "Food and Agriculture Organization of the United Nations",
        "year": 2020,
        "url": "https://www.fao.org/documents/card/en/c/cb1928en",
        "tier": "institutional",
        "variables": ["soil_biodiversity", "soil_ph", "pollution"],
        "biomes": ["all"],
        "metrics": ["microbial_diversity", "earthworm_density", "nutrient_cycling"],
        "text": (
            "FAO reports earthworm density as a practical field proxy for soil biological health: fewer than 30 "
            "individuals per square metre indicates degraded conditions, 100-400 indicates healthy temperate soils. "
            "Soil pH is the strongest single predictor of bacterial community composition, with diversity peaking "
            "between pH 6.0 and 7.5 and falling sharply below 5.5, where aluminium toxicity also limits root growth. "
            "Recovery of soil biological communities after disturbance typically takes 3-10 years."
        ),
    },
    {
        "id": "FAO-SOILPH-2022",
        "title": "Global assessment of soil salinity and guidance on acid soil management",
        "source": "FAO — Global Soil Partnership",
        "authors": "Food and Agriculture Organization of the United Nations",
        "year": 2021,
        "url": "https://www.fao.org/global-soil-partnership/resources/highlights/detail/en/c/1412475/",
        "tier": "institutional",
        "variables": ["soil_ph", "salinity", "soil_health"],
        "biomes": ["drylands", "irrigated", "all"],
        "metrics": ["soil_ph", "yield", "microbial_diversity"],
        "text": (
            "More than 833 million hectares are salt-affected, concentrated in arid and semi-arid irrigated systems "
            "where evaporation exceeds leaching. FAO guidance: on acidic soils (pH < 5.5) liming at 1-3 t/ha raises "
            "pH by roughly 0.5-1.0 unit over 1-2 seasons and restores phosphorus availability; on sodic soils gypsum "
            "plus deep-rooted salt-tolerant cover (Sesbania, Leptochloa) lowers exchangeable sodium percentage "
            "measurably within 2-3 seasons. Organic matter addition buffers pH swings in both directions."
        ),
    },
    # ---------------------------------------------------------------- water
    {
        "id": "ROCKSTROM-2010-AGWATER",
        "title": "Managing water in rainfed agriculture: the need for a paradigm shift",
        "source": "Agricultural Water Management, 97(4), 543-550",
        "authors": "Rockstrom, J. et al.",
        "year": 2010,
        "url": "https://doi.org/10.1016/j.agwat.2009.09.009",
        "tier": "peer_reviewed",
        "variables": ["rainfall", "water_availability", "yield"],
        "biomes": ["semi_arid", "drylands"],
        "metrics": ["water_productivity", "yield", "infiltration"],
        "text": (
            "In semi-arid rainfed systems only 15-30% of rainfall is transpired by crops; the remainder is lost to "
            "soil evaporation, runoff and deep drainage. Water harvesting structures (contour bunds, trenches, "
            "half-moons), mulching and soil cover can raise water productivity by 50-100% without any increase in "
            "rainfall. Yield gaps of 50-80% in these systems are therefore largely a water-partitioning problem "
            "rather than a rainfall problem."
        ),
    },
    {
        "id": "VOROSMARTY-2010-NATURE",
        "title": "Global threats to human water security and river biodiversity",
        "source": "Nature, 467, 555-561",
        "authors": "Vorosmarty, C. J. et al.",
        "year": 2010,
        "url": "https://doi.org/10.1038/nature09440",
        "tier": "peer_reviewed",
        "variables": ["water_availability", "freshwater_biodiversity", "pollution"],
        "biomes": ["riparian", "wetland", "all"],
        "metrics": ["freshwater_species_richness", "water_quality"],
        "text": (
            "Nearly 80% of the world's population lives in areas of high threat to water security, and river "
            "biodiversity threat maps closely track human water stress. Engineering investments mask water-security "
            "threats for wealthy regions but do nothing for aquatic biodiversity, which continues to decline. "
            "Catchment-scale measures that address the driver (riparian buffers, reduced nutrient load, restored "
            "flow regimes) outperform downstream technical fixes for biodiversity outcomes."
        ),
    },
    {
        "id": "MAYER-2007-JEQ",
        "title": "Meta-analysis of nitrogen removal in riparian buffers",
        "source": "Journal of Environmental Quality, 36(4), 1172-1180",
        "authors": "Mayer, P. M., Reynolds, S. K., McCutchen, M. D. & Canfield, T. J.",
        "year": 2007,
        "url": "https://doi.org/10.2134/jeq2006.0462",
        "tier": "meta_analysis",
        "variables": ["riparian_buffers", "pollution", "water_quality"],
        "biomes": ["riparian", "wetland", "temperate_cropland"],
        "metrics": ["nitrate_removal", "water_quality", "habitat_diversity"],
        "text": (
            "Across 89 studies, riparian buffers removed a median of 60-70% of incoming nitrate; buffers wider than "
            "50 m removed over 85%, while buffers under 10 m were inconsistent. Woody and herbaceous buffers "
            "performed similarly for nitrogen, but woody buffers gave greater shading, bank stability and habitat "
            "value. Subsurface flow paths must intersect the root zone, so buffer placement matters more than width "
            "where groundwater bypasses the rooting depth."
        ),
    },
    {
        "id": "MORENOMATEOS-2012-PLOSBIO",
        "title": "Structural and functional loss in restored wetland ecosystems",
        "source": "PLoS Biology, 10(1), e1001247",
        "authors": "Moreno-Mateos, D., Power, M. E., Comin, F. A. & Yockteng, R.",
        "year": 2012,
        "url": "https://doi.org/10.1371/journal.pbio.1001247",
        "tier": "meta_analysis",
        "variables": ["wetland", "restoration", "biodiversity"],
        "biomes": ["wetland", "riparian"],
        "metrics": ["species_richness", "carbon_storage", "hydrological_function"],
        "text": (
            "Synthesis of 621 wetland restoration sites: even a century after restoration, biological structure "
            "averaged 26% lower and biogeochemical function 23% lower than reference wetlands. Recovery was fastest "
            "in warm climates and in large wetlands (>100 ha) connected to rivers. The finding sets realistic "
            "expectations: wetland restoration is a multi-decadal trajectory, and protecting intact wetland is "
            "far higher value per hectare than restoring drained ones."
        ),
    },
    {
        "id": "RAMSAR-GWO-2018",
        "title": "Global Wetland Outlook: State of the World's Wetlands and their Services to People",
        "source": "Ramsar Convention on Wetlands",
        "authors": "Ramsar Convention Secretariat",
        "year": 2018,
        "url": "https://www.global-wetland-outlook.ramsar.org/",
        "tier": "institutional",
        "variables": ["wetland", "land_use", "biodiversity"],
        "biomes": ["wetland"],
        "metrics": ["wetland_extent", "species_richness", "carbon_storage"],
        "text": (
            "35% of natural wetlands were lost between 1970 and 2015, a rate three times faster than forest loss. "
            "Wetlands cover roughly 6% of land surface but store 30% of terrestrial carbon and support 40% of all "
            "species. Restoring hydrology, specifically re-establishing seasonal flooding depth and duration, is "
            "identified as the primary control on whether wetland vegetation and amphibian assemblages recover."
        ),
    },
    {
        "id": "PALMER-2014-SCIENCE",
        "title": "Ecological restoration of streams and rivers: shifting strategies and shifting goals",
        "source": "Annual Review of Ecology, Evolution, and Systematics, 45, 247-269",
        "authors": "Palmer, M. A., Hondula, K. L. & Koch, B. J.",
        "year": 2014,
        "url": "https://doi.org/10.1146/annurev-ecolsys-120213-091935",
        "tier": "peer_reviewed",
        "variables": ["river_restoration", "freshwater_biodiversity"],
        "biomes": ["riparian", "wetland"],
        "metrics": ["freshwater_species_richness", "water_quality"],
        "text": (
            "In-channel structural restoration (rock weirs, wood addition) frequently fails to recover biodiversity "
            "when catchment-scale stressors persist; only 30-40% of projects show measurable ecological improvement. "
            "Projects that first address flow regime, sediment and nutrient inputs succeed far more often. The "
            "lesson generalises: treat the catchment driver before the site symptom."
        ),
    },
    # ---------------------------------------------------------------- fragmentation & habitat
    {
        "id": "HADDAD-2015-SCIADV",
        "title": "Habitat fragmentation and its lasting impact on Earth's ecosystems",
        "source": "Science Advances, 1(2), e1500052",
        "authors": "Haddad, N. M. et al.",
        "year": 2015,
        "url": "https://doi.org/10.1126/sciadv.1500052",
        "tier": "peer_reviewed",
        "variables": ["habitat_fragmentation", "land_use", "biodiversity"],
        "biomes": ["forest", "all"],
        "metrics": ["species_richness", "habitat_connectivity", "edge_effects"],
        "text": (
            "70% of remaining forest lies within 1 km of a forest edge. Experimental fragmentation reduced species "
            "persistence, nutrient retention and biomass by 13-75%, with effects increasing over time and strongest "
            "in the smallest and most isolated fragments. Connectivity interventions (corridors, stepping stones) "
            "raised species richness in connected patches by roughly 20% relative to isolated patches of equal area."
        ),
    },
    {
        "id": "NEWBOLD-2015-NATURE",
        "title": "Global effects of land use on local terrestrial biodiversity (PREDICTS)",
        "source": "Nature, 520, 45-50",
        "authors": "Newbold, T. et al.",
        "year": 2015,
        "url": "https://doi.org/10.1038/nature14324",
        "tier": "peer_reviewed",
        "variables": ["land_use", "biodiversity", "species_richness"],
        "biomes": ["all"],
        "metrics": ["species_richness", "total_abundance"],
        "text": (
            "Analysis of 1.8 million records from 39,123 sites: in the most severely affected habitats, local "
            "species richness is reduced by an average of 76.5% and total abundance by 39.5% relative to intact "
            "primary vegetation. Intensive cropland shows richness reductions of 20-40%; low-intensity and "
            "mosaic agriculture retains substantially more. Land-use intensity, not just land-use type, drives the "
            "difference, which means intensity reduction is a viable biodiversity lever without land conversion."
        ),
    },
    {
        "id": "KREMEN-MERENLENDER-2018",
        "title": "Landscapes that work for biodiversity and people",
        "source": "Science, 362(6412), eaau6020",
        "authors": "Kremen, C. & Merenlender, A. M.",
        "year": 2018,
        "url": "https://doi.org/10.1126/science.aau6020",
        "tier": "peer_reviewed",
        "variables": ["working_lands", "connectivity", "biodiversity"],
        "biomes": ["all"],
        "metrics": ["habitat_connectivity", "species_richness", "ecosystem_services"],
        "text": (
            "Working landscapes maintain biodiversity when they retain at least 20% semi-natural habitat "
            "distributed as a fine-grained mosaic, keep patch-to-patch distances under 1 km and reduce chemical "
            "inputs. Below roughly 20% natural cover, species loss accelerates non-linearly. Diversified farming "
            "systems within the matrix raise the permeability of the landscape for dispersal, which matters as much "
            "as the reserved patches themselves."
        ),
    },
    {
        "id": "TSCHARNTKE-2012-BIOCON",
        "title": "Landscape moderation of biodiversity patterns and processes",
        "source": "Biological Reviews, 87(3), 661-685",
        "authors": "Tscharntke, T. et al.",
        "year": 2012,
        "url": "https://doi.org/10.1111/j.1469-185X.2011.00216.x",
        "tier": "peer_reviewed",
        "variables": ["landscape_context", "biodiversity", "pest_control"],
        "biomes": ["all"],
        "metrics": ["species_richness", "pest_control"],
        "text": (
            "The intermediate landscape-complexity hypothesis: local restoration measures produce the largest "
            "biodiversity gains in simple landscapes holding 1-20% semi-natural habitat, small gains in cleared "
            "landscapes (<1%) where no species pool remains to recolonise, and small gains in complex landscapes "
            "(>20%) that are already saturated. Diagnosing landscape context before prescribing local action is "
            "therefore essential for predicting response."
        ),
    },
    {
        "id": "IUCN-REDLIST-2024",
        "title": "IUCN Red List of Threatened Species — threat classification and recovery",
        "source": "IUCN",
        "authors": "International Union for Conservation of Nature",
        "year": 2024,
        "url": "https://www.iucnredlist.org/",
        "tier": "institutional",
        "variables": ["species", "threats", "biodiversity"],
        "biomes": ["all"],
        "metrics": ["species_richness", "threatened_species_count"],
        "text": (
            "Over 45,000 of 163,000 assessed species are threatened. Agriculture and aquaculture are listed as a "
            "threat for 86% of threatened species, followed by biological resource use and residential development. "
            "IUCN's Green Status framework emphasises that species recovery needs habitat quality and connectivity "
            "across the full range, not protection of a single site, and recommends recovery targets be set against "
            "historical range rather than current occupancy."
        ),
    },
    {
        "id": "IUCN-NBS-STANDARD-2020",
        "title": "Global Standard for Nature-based Solutions",
        "source": "IUCN",
        "authors": "International Union for Conservation of Nature",
        "year": 2020,
        "url": "https://portals.iucn.org/library/node/49070",
        "tier": "institutional",
        "variables": ["restoration", "nature_based_solutions", "monitoring"],
        "biomes": ["all"],
        "metrics": ["ecosystem_integrity", "adaptive_management"],
        "text": (
            "The IUCN standard requires that nature-based interventions address a clearly defined societal "
            "challenge, be designed at landscape scale, deliver net biodiversity gain, be economically viable, and "
            "include an adaptive management plan with measurable indicators and defined monitoring intervals. "
            "Interventions without a monitoring and adjustment loop are explicitly non-compliant, which makes "
            "baseline measurement the first step of any credible plan."
        ),
    },
    # ---------------------------------------------------------------- forests
    {
        "id": "CROUZEILLES-2016-NATCOMM",
        "title": "A global meta-analysis on the ecological drivers of forest restoration success",
        "source": "Nature Communications, 7, 11666",
        "authors": "Crouzeilles, R. et al.",
        "year": 2016,
        "url": "https://doi.org/10.1038/ncomms11666",
        "tier": "meta_analysis",
        "variables": ["forest_restoration", "biodiversity"],
        "biomes": ["forest", "tropical"],
        "metrics": ["species_richness", "vegetation_structure"],
        "text": (
            "Meta-analysis of 221 studies: natural regeneration outperformed active tree planting for both "
            "biodiversity (34-56% higher) and vegetation structure recovery, and cost far less, wherever remnant "
            "forest cover remained nearby and soil was not severely degraded. Larger restored areas and wetter "
            "climates recovered faster. Active planting remains necessary where seed sources are absent, soils are "
            "compacted, or aggressive grasses dominate."
        ),
    },
    {
        "id": "CHAZDON-2016-SCIADV",
        "title": "Carbon sequestration potential of second-growth forest regeneration in the Latin American tropics",
        "source": "Science Advances, 2(5), e1501639",
        "authors": "Chazdon, R. L. et al.",
        "year": 2016,
        "url": "https://doi.org/10.1126/sciadv.1501639",
        "tier": "peer_reviewed",
        "variables": ["forest_restoration", "carbon", "succession"],
        "biomes": ["tropical", "forest"],
        "metrics": ["carbon_sequestration", "habitat_diversity"],
        "text": (
            "Second-growth tropical forests accumulate above-ground biomass at roughly 3 t C/ha/yr in the first 20 "
            "years, recovering 90% of old-growth biomass in 66 years on average under favourable conditions. Species "
            "composition recovers more slowly than biomass, with late-successional and dispersal-limited species "
            "lagging by decades, which is why enrichment planting targets those functional groups specifically."
        ),
    },
    {
        "id": "GRISCOM-2017-PNAS",
        "title": "Natural climate solutions",
        "source": "PNAS, 114(44), 11645-11650",
        "authors": "Griscom, B. W. et al.",
        "year": 2017,
        "url": "https://doi.org/10.1073/pnas.1710465114",
        "tier": "peer_reviewed",
        "variables": ["restoration", "climate", "land_use"],
        "biomes": ["all"],
        "metrics": ["carbon_sequestration", "co_benefits"],
        "text": (
            "Twenty natural climate solutions could deliver 23.8 Gt CO2e/yr of cost-effective mitigation, about "
            "30% of what is needed to hold warming below 2 degrees C. Avoided forest conversion, reforestation and "
            "improved forest management dominate the potential; most pathways deliver water, soil and biodiversity "
            "co-benefits, and the authors rank them by co-benefit density so that interventions can be selected for "
            "multiple objectives at once."
        ),
    },
    {
        "id": "FAO-FRA-2020",
        "title": "Global Forest Resources Assessment 2020",
        "source": "FAO",
        "authors": "Food and Agriculture Organization of the United Nations",
        "year": 2020,
        "url": "https://www.fao.org/forest-resources-assessment/2020/en/",
        "tier": "institutional",
        "variables": ["deforestation", "land_cover", "forest"],
        "biomes": ["forest", "tropical"],
        "metrics": ["forest_cover", "habitat_connectivity"],
        "text": (
            "The world lost 178 million hectares of forest between 1990 and 2020, although the rate of net loss "
            "slowed from 7.8 to 4.7 million ha/yr. Agricultural expansion causes almost 90% of global deforestation, "
            "with cropland expansion responsible for 49.6% and livestock grazing 38.5%. Planted forest and natural "
            "regeneration in some regions offset gross loss but do not replace primary forest biodiversity value."
        ),
    },
    # ---------------------------------------------------------------- grassland / grazing
    {
        "id": "MCSHERRY-RITCHIE-2013",
        "title": "Effects of grazing on grassland soil carbon: a global review",
        "source": "Global Change Biology, 19(5), 1347-1357",
        "authors": "McSherry, M. E. & Ritchie, M. E.",
        "year": 2013,
        "url": "https://doi.org/10.1111/gcb.12144",
        "tier": "meta_analysis",
        "variables": ["grazing", "soil_organic_carbon", "grassland"],
        "biomes": ["grassland", "semi_arid", "drylands"],
        "metrics": ["soil_organic_carbon", "vegetation_cover"],
        "text": (
            "Grazing effects on grassland soil carbon depend on grass type and rainfall: increasing intensity raised "
            "SOC by an average 6-7% on C4-dominated grasslands but reduced it by up to 18% on C3-dominated "
            "grasslands. In drier sites, moderate stocking with planned rest periods consistently outperformed both "
            "continuous heavy grazing and complete exclusion, because periodic defoliation stimulates root turnover "
            "while rest allows recovery of basal cover."
        ),
    },
    {
        "id": "BENGTSSON-2019-ECOSPHERE",
        "title": "Grasslands: more important for ecosystem services than you might think",
        "source": "Ecosphere, 10(2), e02582",
        "authors": "Bengtsson, J. et al.",
        "year": 2019,
        "url": "https://doi.org/10.1002/ecs2.2582",
        "tier": "peer_reviewed",
        "variables": ["grassland", "biodiversity", "ecosystem_services"],
        "biomes": ["grassland", "semi_arid"],
        "metrics": ["species_richness", "carbon_storage", "pollinator_abundance"],
        "text": (
            "Semi-natural grasslands hold among the highest small-scale plant species richness recorded (up to 80 "
            "species per square metre) and store most of their carbon below ground, making them more fire- and "
            "drought-resilient carbon stores than forests in dry regions. Conversion or afforestation of species-rich "
            "grassland is a net biodiversity loss even where above-ground carbon increases, a trade-off often missed "
            "in tree-planting targets."
        ),
    },
    # ---------------------------------------------------------------- pollution / inputs
    {
        "id": "UNEP-NITROGEN-2019",
        "title": "Frontiers 2018/19: Nitrogen — the hidden threat",
        "source": "UNEP Frontiers Report",
        "authors": "United Nations Environment Programme",
        "year": 2019,
        "url": "https://www.unep.org/resources/frontiers-201819-emerging-issues-environmental-concern",
        "tier": "institutional",
        "variables": ["pollution", "nitrogen", "water_quality"],
        "biomes": ["all"],
        "metrics": ["nitrate_removal", "water_quality", "species_richness"],
        "text": (
            "Only about 20% of applied reactive nitrogen is consumed in food; the rest is lost to air and water, "
            "driving eutrophication, biodiversity loss in nitrogen-sensitive habitats and greenhouse gas emissions. "
            "Nitrogen deposition above critical loads of 10-20 kg N/ha/yr shifts plant communities toward a few "
            "nitrophilous species and reduces species richness measurably. Improving nitrogen use efficiency "
            "delivers biodiversity gains and cost savings simultaneously."
        ),
    },
    {
        "id": "UNCCD-GLO2-2022",
        "title": "Global Land Outlook 2: Land Restoration for Recovery and Resilience",
        "source": "UNCCD",
        "authors": "United Nations Convention to Combat Desertification",
        "year": 2022,
        "url": "https://www.unccd.int/resources/global-land-outlook/glo2",
        "tier": "institutional",
        "variables": ["land_degradation", "restoration", "drylands"],
        "biomes": ["drylands", "semi_arid", "all"],
        "metrics": ["land_degradation", "soil_organic_carbon", "water_availability"],
        "text": (
            "Up to 40% of land is degraded, affecting half of humanity. Restoring 1 billion hectares by 2030 would "
            "deliver returns of USD 7-30 per dollar invested. UNCCD stresses land-degradation-neutrality accounting: "
            "measure land cover, land productivity and soil organic carbon stock together, since improvement in one "
            "indicator while another declines does not constitute neutrality."
        ),
    },
    {
        "id": "IPBES-GA-2019",
        "title": "Global Assessment Report on Biodiversity and Ecosystem Services",
        "source": "IPBES",
        "authors": "Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services",
        "year": 2019,
        "url": "https://www.ipbes.net/global-assessment",
        "tier": "institutional",
        "variables": ["biodiversity", "land_use", "drivers"],
        "biomes": ["all"],
        "metrics": ["species_richness", "ecosystem_integrity"],
        "text": (
            "Around 1 million species face extinction. The ranked direct drivers are land- and sea-use change, "
            "direct exploitation, climate change, pollution and invasive species. Roughly 75% of the terrestrial "
            "environment is severely altered. IPBES concludes that goals for 2030 cannot be met without "
            "transformative change, and that landscape-scale action combining restoration with reduced input "
            "intensity is more effective than protected areas alone."
        ),
    },
    {
        "id": "CBD-GBF-2022",
        "title": "Kunming-Montreal Global Biodiversity Framework",
        "source": "Convention on Biological Diversity",
        "authors": "CBD Secretariat",
        "year": 2022,
        "url": "https://www.cbd.int/gbf/",
        "tier": "institutional",
        "variables": ["policy", "restoration", "biodiversity"],
        "biomes": ["all"],
        "metrics": ["restored_area", "protected_area", "pesticide_risk"],
        "text": (
            "Target 2 commits to restoring 30% of degraded ecosystems by 2030; Target 3 to conserving 30% of land "
            "and water; Target 7 to reducing pesticide risk by half; Target 10 to sustainable management of all "
            "agricultural land. For landholders this establishes measurable, auditable outcome targets that "
            "farm-level plans can be aligned to, including area restored, input-risk reduction and habitat retained."
        ),
    },
    # ---------------------------------------------------------------- pest control / IPM
    {
        "id": "DAINESE-2019-SCIADV",
        "title": "A global synthesis reveals biodiversity-mediated benefits for crop production",
        "source": "Science Advances, 5(10), eaax0121",
        "authors": "Dainese, M. et al.",
        "year": 2019,
        "url": "https://doi.org/10.1126/sciadv.aax0121",
        "tier": "meta_analysis",
        "variables": ["biodiversity", "pest_control", "pollinators", "yield"],
        "biomes": ["all"],
        "metrics": ["yield", "pest_control", "pollinator_abundance"],
        "text": (
            "Analysis of 89 studies and 1,475 landscapes: landscape simplification reduced pollinator and natural "
            "enemy richness, which in turn reduced pollination and pest control services and lowered crop yield. "
            "Richness effects were mediated by abundance, so interventions that raise both abundance and richness "
            "(diverse flowering resources spanning the season, undisturbed overwintering habitat) produce the "
            "strongest production response."
        ),
    },
    {
        "id": "HOLLAND-2016-PESTMGMT",
        "title": "Structure, function and management of semi-natural habitats for conservation biological control",
        "source": "Pest Management Science, 72(9), 1638-1651",
        "authors": "Holland, J. M. et al.",
        "year": 2016,
        "url": "https://doi.org/10.1002/ps.4318",
        "tier": "peer_reviewed",
        "variables": ["pest_control", "field_margins", "habitat"],
        "biomes": ["temperate_cropland", "all"],
        "metrics": ["pest_control", "natural_enemy_abundance"],
        "text": (
            "Grassy beetle banks and tussock-forming grasses such as Dactylis glomerata support overwintering "
            "densities above 1,000 predatory arthropods per square metre, and in-field banks placed every 100-200 m "
            "allow predators to reach the field centre early in the season. Predator access, not total habitat area, "
            "is usually the limiting factor in large fields, which is why in-field strips outperform perimeter-only "
            "habitat."
        ),
    },
    {
        "id": "FAO-IPM-2021",
        "title": "FAO guidance on integrated pest management and pesticide risk reduction",
        "source": "FAO",
        "authors": "Food and Agriculture Organization of the United Nations",
        "year": 2021,
        "url": "https://www.fao.org/pest-and-pesticide-management/ipm/integrated-pest-management/en/",
        "tier": "institutional",
        "variables": ["pesticides", "pollution", "pest_control"],
        "biomes": ["all"],
        "metrics": ["pesticide_risk", "natural_enemy_abundance", "pollinator_abundance"],
        "text": (
            "FAO's IPM sequence is prevention, monitoring against economic thresholds, biological and cultural "
            "control, and only then targeted chemical use. Farmer field school programmes have cut pesticide "
            "applications by 35-92% with maintained yields across multiple Asian rice and vegetable systems. "
            "Avoiding prophylactic seed treatments and calendar spraying is identified as the fastest route to "
            "restoring natural enemy populations."
        ),
    },
    # ---------------------------------------------------------------- monitoring & indicators
    {
        "id": "GEOBON-EBV-2013",
        "title": "Essential Biodiversity Variables",
        "source": "Science, 339(6117), 277-278 / GEO BON",
        "authors": "Pereira, H. M. et al.",
        "year": 2013,
        "url": "https://doi.org/10.1126/science.1229931",
        "tier": "peer_reviewed",
        "variables": ["monitoring", "biodiversity", "indicators"],
        "biomes": ["all"],
        "metrics": ["species_richness", "habitat_structure", "ecosystem_function"],
        "text": (
            "Essential Biodiversity Variables organise monitoring into six classes: genetic composition, species "
            "populations, species traits, community composition, ecosystem structure and ecosystem function. For "
            "farm and landscape scale, practical proxies are species richness of indicator taxa (birds, bees, "
            "beetles, earthworms), vegetation structural complexity and phenology. Consistent method and timing "
            "matter more than taxonomic completeness for detecting trend."
        ),
    },
    {
        "id": "TEEB-AGRIFOOD-2018",
        "title": "TEEB for Agriculture and Food: Scientific and Economic Foundations",
        "source": "UN Environment — TEEB",
        "authors": "The Economics of Ecosystems and Biodiversity",
        "year": 2018,
        "url": "https://teebweb.org/our-work/agrifood/reports/scientific-economic-foundations/",
        "tier": "institutional",
        "variables": ["economics", "ecosystem_services", "land_use"],
        "biomes": ["all"],
        "metrics": ["net_benefit", "ecosystem_services"],
        "text": (
            "TEEB values hidden costs of eco-agri-food systems at over USD 12 trillion annually, dominated by "
            "soil degradation, water pollution and health effects. Valuation of on-farm natural capital reframes "
            "habitat and soil investment as asset maintenance. Payback periods reported for diversification "
            "investments are typically 2-5 years once input substitution and yield stability are counted."
        ),
    },
    {
        "id": "SEUFERT-2017-ANNREV",
        "title": "Many shades of grey — the context-dependent performance of organic agriculture",
        "source": "Science Advances, 3(3), e1602638",
        "authors": "Seufert, V. & Ramankutty, N.",
        "year": 2017,
        "url": "https://doi.org/10.1126/sciadv.1602638",
        "tier": "meta_analysis",
        "variables": ["management_intensity", "yield", "biodiversity"],
        "biomes": ["all"],
        "metrics": ["yield", "species_richness", "profitability"],
        "text": (
            "Organic systems show 19-25% lower yields on average but 30% higher species richness and 20-95% higher "
            "profitability where price premiums exist. Yield gaps narrow to under 10% in rainfed, low-input and "
            "drought-prone contexts, and in legume-rich rotations. Context determines outcome, so blanket "
            "recommendations about input systems are unreliable without site information."
        ),
    },
    {
        "id": "ROSA-SCHLEICH-2019",
        "title": "Ecological-economic trade-offs of diversified farming systems — a review",
        "source": "Ecological Economics, 160, 251-263",
        "authors": "Rosa-Schleich, J., Loos, J., Musshoff, O. & Tscharntke, T.",
        "year": 2019,
        "url": "https://doi.org/10.1016/j.ecolecon.2019.03.002",
        "tier": "peer_reviewed",
        "variables": ["economics", "diversification", "risk"],
        "biomes": ["all"],
        "metrics": ["net_benefit", "yield_stability", "labour"],
        "text": (
            "Diversified systems carry higher labour and knowledge costs in years 1-3 and deliver reduced input "
            "costs and lower yield variance from year 3 onward. Reported cost-benefit ratios turn positive after "
            "2-4 years for intercropping and agroforestry, later for perennial systems. Transition finance and "
            "staged adoption on 10-20% of area are recommended to manage the establishment trough."
        ),
    },
    {
        "id": "GARRETT-2017-AGSYS",
        "title": "Drivers of decoupling and recoupling of crop and livestock systems",
        "source": "Agricultural Systems, 155, 136-146",
        "authors": "Garrett, R. D. et al.",
        "year": 2017,
        "url": "https://doi.org/10.1016/j.agsy.2017.05.003",
        "tier": "peer_reviewed",
        "variables": ["integrated_systems", "livestock", "soil_health"],
        "biomes": ["all"],
        "metrics": ["soil_organic_carbon", "nutrient_cycling", "net_benefit"],
        "text": (
            "Integrated crop-livestock systems recycle nutrients on farm, cut fertiliser purchases by 30-50% and "
            "raise soil organic matter through manure and perennial pasture phases. Crop-livestock integration "
            "also diversifies income, buffering against single-commodity price and weather shocks, though it "
            "requires fencing, water points and labour that constrain rapid adoption."
        ),
    },
    {
        "id": "SMITH-2019-GCB",
        "title": "Which practices co-deliver food security, climate change mitigation and adaptation?",
        "source": "Global Change Biology, 26(3), 1532-1575",
        "authors": "Smith, P. et al.",
        "year": 2019,
        "url": "https://doi.org/10.1111/gcb.14878",
        "tier": "peer_reviewed",
        "variables": ["land_management", "climate", "food_security"],
        "biomes": ["all"],
        "metrics": ["carbon_sequestration", "yield_stability", "land_degradation"],
        "text": (
            "Assessment of 40 land-management options: increased soil organic matter, improved cropland and "
            "grazing management, agroforestry and reduced landscape degradation co-deliver mitigation, adaptation, "
            "desertification control and food security with no notable trade-offs. Options relying on large land-area "
            "conversion (bioenergy monoculture, large-scale afforestation of grassland) show adverse side effects "
            "for biodiversity and water."
        ),
    },
    {
        "id": "ISRIC-SOILGRIDS-2021",
        "title": "SoilGrids 2.0: producing soil information for the globe",
        "source": "SOIL, 7, 217-240 / ISRIC World Soil Information",
        "authors": "Poggio, L. et al.",
        "year": 2021,
        "url": "https://doi.org/10.5194/soil-7-217-2021",
        "tier": "peer_reviewed",
        "variables": ["soil_data", "spatial", "soil_organic_carbon"],
        "biomes": ["all"],
        "metrics": ["soil_organic_carbon", "soil_ph", "texture"],
        "text": (
            "SoilGrids 2.0 provides global predictions of soil organic carbon, pH, texture, bulk density and "
            "nitrogen at 250 m resolution with uncertainty intervals, from 240,000 profile observations. It is a "
            "valid baseline where field measurement is unavailable, but prediction intervals at a single point are "
            "wide, so it should anchor expectations rather than substitute for a lab test before major investment."
        ),
    },
    {
        "id": "WORLDCOVER-2021",
        "title": "ESA WorldCover 10 m global land cover",
        "source": "European Space Agency",
        "authors": "Zanaga, D. et al.",
        "year": 2021,
        "url": "https://esa-worldcover.org/",
        "tier": "institutional",
        "variables": ["land_cover", "spatial", "habitat_fragmentation"],
        "biomes": ["all"],
        "metrics": ["land_cover_class", "habitat_connectivity"],
        "text": (
            "ESA WorldCover maps 11 land-cover classes globally at 10 m resolution with roughly 75% overall "
            "accuracy. At farm and landscape scale it supports measurement of semi-natural habitat percentage, "
            "patch size distribution and distance-to-habitat, the three landscape metrics most predictive of "
            "pollinator and natural-enemy service delivery."
        ),
    },
    {
        "id": "SHACKELFORD-2013-BIOREV",
        "title": "Comparison of pollinators and natural enemies: a meta-analysis of landscape and local effects",
        "source": "Biological Reviews, 88(4), 1002-1021",
        "authors": "Shackelford, G. et al.",
        "year": 2013,
        "url": "https://doi.org/10.1111/brv.12040",
        "tier": "meta_analysis",
        "variables": ["pollinators", "pest_control", "landscape_context"],
        "biomes": ["all"],
        "metrics": ["pollinator_abundance", "natural_enemy_abundance"],
        "text": (
            "Pollinators respond more strongly to landscape-scale semi-natural habitat while natural enemies "
            "respond more strongly to local field-scale management. This asymmetry means a farm aiming at both "
            "services needs a two-scale design: in-field and field-edge habitat for natural enemies, plus larger "
            "connected patches within foraging range for pollinators."
        ),
    },
    {
        "id": "GILBERT-BUNDY-SALINITY",
        "title": "Managing salinity and water tables in irrigated drylands",
        "source": "ICARDA / IWMI technical synthesis",
        "authors": "International Center for Agricultural Research in the Dry Areas",
        "year": 2018,
        "url": "https://www.icarda.org/publications",
        "tier": "institutional",
        "variables": ["salinity", "irrigation", "water_table"],
        "biomes": ["drylands", "semi_arid", "irrigated"],
        "metrics": ["salinity", "yield", "water_productivity"],
        "text": (
            "Where shallow water tables sit within 2 m of the surface in arid irrigated systems, capillary rise "
            "concentrates salts in the root zone. Deep-rooted perennials (lucerne, Prosopis, Atriplex) used as "
            "biodrainage lower water tables by 0.3-1.0 m per season and reduce root-zone electrical conductivity, "
            "while also supplying fodder and habitat structure. Leaching fractions alone displace rather than solve "
            "the problem where drainage is poor."
        ),
    },
    {
        "id": "BOMMARCO-2013-TREE",
        "title": "Ecological intensification: harnessing ecosystem services for food security",
        "source": "Trends in Ecology & Evolution, 28(4), 230-238",
        "authors": "Bommarco, R., Kleijn, D. & Potts, S. G.",
        "year": 2013,
        "url": "https://doi.org/10.1016/j.tree.2012.10.012",
        "tier": "peer_reviewed",
        "variables": ["ecological_intensification", "biodiversity", "yield"],
        "biomes": ["all"],
        "metrics": ["yield", "input_reduction", "species_richness"],
        "text": (
            "Ecological intensification substitutes biologically mediated processes for purchased inputs: "
            "biological nitrogen fixation, pollination, pest regulation, soil structure formation. The framework "
            "requires quantifying the service gap first (what fraction of the input is already substitutable), "
            "then designing habitat and rotation to close it. It explicitly rejects one-size prescriptions in "
            "favour of site-specific service accounting."
        ),
    },
    {
        "id": "ISBELL-2015-NATURE",
        "title": "Biodiversity increases the resistance of ecosystem productivity to climate extremes",
        "source": "Nature, 526, 574-577",
        "authors": "Isbell, F. et al.",
        "year": 2015,
        "url": "https://doi.org/10.1038/nature15374",
        "tier": "peer_reviewed",
        "variables": ["biodiversity", "climate_extremes", "resilience"],
        "biomes": ["grassland", "all"],
        "metrics": ["productivity_stability", "species_richness"],
        "text": (
            "Across 46 grassland experiments on five continents, plant communities with 16-32 species were roughly "
            "twice as resistant to extreme drought and wet events as monocultures, and recovered faster afterwards. "
            "The effect arises from asynchronous species responses. For managed land this argues for functional "
            "diversity in seed mixes and rotations as an explicit climate-risk measure rather than a conservation "
            "add-on."
        ),
    },
    {
        "id": "VANDERPUTTEN-2013-ROTATION",
        "title": "Plant-soil feedbacks: the role of soil biota in rotation design",
        "source": "Journal of Ecology, 101(2), 265-276",
        "authors": "van der Putten, W. H. et al.",
        "year": 2013,
        "url": "https://doi.org/10.1111/1365-2745.12054",
        "tier": "peer_reviewed",
        "variables": ["rotation", "soil_biodiversity", "disease"],
        "biomes": ["all"],
        "metrics": ["yield", "microbial_diversity", "disease_pressure"],
        "text": (
            "Continuous monoculture accumulates host-specific soil pathogens and nematodes, producing negative "
            "plant-soil feedback that depresses yield independently of nutrient status. Breaking the cycle with "
            "functionally distinct crops (a legume and a non-host brassica or grass) for two seasons measurably "
            "reduces pathogen inoculum and restores positive feedback. Rotation design should maximise functional, "
            "not just taxonomic, distance between successive crops."
        ),
    },
]


def documents() -> List[Dict[str, Any]]:
    return DOCUMENTS


def by_id(doc_id: str) -> Dict[str, Any] | None:
    for doc in DOCUMENTS:
        if doc["id"] == doc_id:
            return doc
    return None


def stats() -> Dict[str, Any]:
    tiers: Dict[str, int] = {}
    variables: Dict[str, int] = {}
    for doc in DOCUMENTS:
        tiers[doc["tier"]] = tiers.get(doc["tier"], 0) + 1
        for var in doc["variables"]:
            variables[var] = variables.get(var, 0) + 1
    years = [d["year"] for d in DOCUMENTS]
    return {
        "document_count": len(DOCUMENTS),
        "sources": len({d["source"] for d in DOCUMENTS}),
        "tiers": tiers,
        "variables_covered": len(variables),
        "top_variables": sorted(variables.items(), key=lambda kv: -kv[1])[:12],
        "year_range": [min(years), max(years)],
    }
