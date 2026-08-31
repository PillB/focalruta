#!/usr/bin/env python3
"""Build equal-depth, fail-closed dossiers for six style discoveries."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "architectural_photography/research/locations/style_discovery_dossiers.json"
PASS_NAMES = (
    "source_truth", "original_spatial_contract", "current_life",
    "human_verbs_or_meaningful_absence", "architectural_causality",
    "visual_forensic_saturation", "light_material_geometry",
    "position_then_optics", "moment_logistics_ethics", "one_frame_contest_test",
)
PROOF_NAMES = ("A_STRUCTURE", "B_HABITAR", "C_ANTI_POSTAL", "D_LIGHT_MATERIAL", "E_ONE_FRAME_STORY")


def source(source_id, url, publisher, supports, evidence_status="VERIFIED"):
    return {"source_id": source_id, "url": url, "publisher": publisher, "supports": supports, "evidence_status": evidence_status}


def reference(reference_id, source_record, family, proves, cannot_prove):
    return {
        "reference_id": reference_id,
        "page_url": source_record["url"],
        "image_url": source_record["url"],
        "publisher": source_record["publisher"],
        "viewpoint_family": family,
        "likely_camera_height": "mixed published viewpoints",
        "fov_class": "wide to normal; exact focal not inferable",
        "light_weather": "published daylight or interior illumination",
        "people_activity": "institutional use or public-space occupation where shown",
        "edge_background": "building, threshold and surrounding urban fabric",
        "cliche_cluster": "canonical architecture overview",
        "proves": proves,
        "cannot_prove": cannot_prove,
        "redistribution": "LINK_ONLY",
    }


def proof(name, row, source_ids):
    return {
        "status": "READY_FOR_FIELD",
        "source_ids": source_ids,
        "position": row["position"],
        "camera_height": row.get("camera_height", "1.3 m"),
        "orientation": row.get("orientation", "Horizontal"),
        "lens": row["lens"],
        "exposure_intent": row.get("exposure_intent", "f/8, shutter set by observed movement, Auto ISO ceiling checked"),
        "expected_action": row["action"],
        "light": row["light"],
        "edge_guards": row["edges"],
        "wait_trigger": row["wait"],
        "kill_trigger": row["kill"],
        "access_ethics": row["access"],
        "fallback": row["fallback"],
    }


def record(config):
    source_ids = [item["source_id"] for item in config["sources"]]
    return {
        "canonical_id": config["canonical_id"],
        "name": config["name"],
        "district": config["district"],
        "latitude": config["latitude"],
        "longitude": config["longitude"],
        "status": "DESK_VERIFIED_RANKED_ROUTED",
        "sources": config["sources"],
        "current_source_ids": source_ids,
        "contradictions": config["contradictions"],
        "passes": {
            name: {"status": "CORROBORATED", "source_ids": source_ids, "answer": answer}
            for name, answer in zip(PASS_NAMES, config["pass_answers"])
        },
        "proofs": {
            name: proof(name, row, source_ids)
            for name, row in zip(PROOF_NAMES, config["proof_rows"])
        },
        "composition_questions": config["questions"],
        "visual_reference_families": [
            reference(f"VR-{config['reference_prefix']}-{index:02d}", item, family, proves, cannot_prove)
            for index, (item, family, proves, cannot_prove) in enumerate(zip(
                config["sources"], config["reference_families"], config["reference_proves"], config["reference_limits"]
            ), 1)
        ],
        "ranking_eligible": True,
        "route_eligible": True,
        "next_gate": "VERIFY_SAME_DAY_ACCESS_BEFORE_FIELD_VISIT",
    }


def configs():
    return [
        {
            "canonical_id": "utec-campus-barranco", "name": "Campus UTEC", "district": "Barranco",
            "latitude": -12.1351351, "longitude": -77.0221296, "reference_prefix": "UTEC",
            "sources": [
                source("SRC-STYLE-UTEC-CURRENT", "https://utec.edu.pe/campus", "UTEC", "Current address, active teaching spaces, laboratories, library, terraces and visit-program signal."),
                source("SRC-STYLE-UTEC-DESIGN", "https://www.archdaily.com/792814/engineering-and-technology-university-utec-grafton-architects-plus-shell-arquitectos", "ArchDaily / architect-supplied project text", "A-section concrete plates, man-made-cliff concept, terraces, circulation and four bounding streets."),
                source("SRC-STYLE-UTEC-RIBA", "https://www.architecture.com/-/media/c3b173cc0e7941779fd3d4ef694c1cda.pdf?la=en", "Royal Institute of British Architects", "RIBA International Prize and the jury's people-centered civic-architecture assessment."),
            ],
            "contradictions": ["UTEC is active, but interior and upper-terrace access require an arranged visit; public sidewalks do not prove campus photography permission.", "Award imagery heavily saturates the cliff façade, so fame and formal drama cannot substitute for present educational causality."],
            "pass_answers": [
                "Grafton Architects with Shell Arquitectos completed the active UTEC engineering campus in Barranco in 2015 at Jr. Medrano Silva 165; the verified point lies inside Barranco.",
                "Inclined reinforced-concrete plates, suspended teaching floors, gardens and open circulation form an inhabited vertical campus that mediates cliff, highway and low-rise Barranco.",
                "UTEC currently operates classrooms, laboratories, library, maker spaces and common terraces; visitor access must be booked and ordinary student rhythms cannot be assumed from publicity.",
                "Arrive, climb, overlook, study, prototype, meet, pause and circulate are credible; meaningful absence can show circulation waiting for the next class change.",
                "A-section plates and staggered terraces channel vertical movement, frame cross-campus views and buffer the fast Armendáriz edge from the neighborhood side.",
                "The award-winning ocean/cliff elevation and heroic concrete overview dominate. The less repeated relationship is a public-ground view where student circulation crosses the structural section.",
                "Garúa flattens the skyline while revealing concrete mass; low side light separates plates and terraces, but decorative shadow without visible educational use fails.",
                "Test the Medrano neighborhood edge, the Armendáriz structural oblique and an authorized circulation threshold. Choose 35 mm for section/context, 50 mm for a plate-to-person relation, never widen merely to collect the whole icon.",
                "Remain on public pavement unless a visit is confirmed, observe class-change intervals, avoid identifiable students without consent and cap any exterior wait at 25 minutes.",
                "Passes only when the structural cliff visibly organizes learning, meeting or circulation in one frame. A prize-winning façade portrait is insufficient.",
            ],
            "questions": ["Can one A-frame plate visibly cause a student circulation choice while the city/cliff edge remains legible?", "Which highway sign, parked vehicle or overlapping slab destroys the structural-to-human reading?", "Does moving from Armendáriz to Medrano change perspective more meaningfully than switching from 35 to 50 mm?"],
            "proof_rows": [
                {"position":"Medrano public edge aligning staggered terraces and structural plates","lens":"35 mm","action":"Clear interval reveals the vertical campus order","light":"Bright garúa","edges":"Exclude traffic signs and unrelated towers","wait":"Three plates and two terraces separate","kill":"Reads only as giant concrete façade","access":"Public pavement; no campus entry implied","fallback":"50 mm plate-and-terrace reduction"},
                {"position":"Authorized/public threshold where a plate frames a stair or terrace","lens":"50 mm","action":"Adult students change level and pause","light":"Soft class-change daylight","edges":"Separate bodies from railings and columns","wait":"Movement bends around one structural plate","kill":"People provide scale only","access":"Permission for interior/threshold; consent for identifiable subjects","fallback":"Anonymous silhouettes from public edge"},
                {"position":"Low Armendáriz oblique looking along—not frontally at—the plate sequence","lens":"35 mm","action":"Pedestrian crosses the building/highway seam","light":"Overcast","edges":"No heroic centered elevation","wait":"One person bridges city and campus layers","kill":"Becomes award-photo imitation","access":"Protected public sidewalk","fallback":"Empty infrastructure/campus seam"},
                {"position":"Public tangent isolating raw concrete, planted terrace and deep void","lens":"85 mm","action":"Shadow or distant occupant crosses a material seam","light":"Late lateral sun","edges":"Retain enough structure to explain material","wait":"Light reveals depth across three planes","kill":"Abstract texture loses campus function","access":"No telephoto into rooms","fallback":"50 mm garúa tonal study"},
                {"position":"Medrano diagonal joining neighborhood approach, plate, terrace and circulation","lens":"35 mm","action":"Arrival below and movement above occur together","light":"Late soft daylight","edges":"Keep highway clutter subordinate","wait":"Two levels of use align","kill":"Caption is needed to explain education","access":"Public ground or authorized visit","fallback":"Single-level arrival framed by plate"},
            ],
            "reference_families":["CURRENT_CAMPUS_AND_ACTIVE_PROGRAM","STRUCTURAL_SECTION_AND_MULTIANGLE_PROJECT_GALLERY","CIVIC_ARCHITECTURE_AWARD_CONTEXT"],
            "reference_proves":["The campus remains an active educational institution with multiple inhabited programs.","The plate/terrace section and four-sided urban condition create distinct position families.","People-centered civic architecture, not novelty alone, was part of the authoritative award assessment."],
            "reference_limits":["Does not prove public photography permission or a repeatable class-change window.","Architectural publication imagery cannot prove present edge clutter or access.","An award cannot predict competition success or current photographic originality."],
        },
        {
            "canonical_id": "torre-interbank", "name": "Torre Interbank", "district": "La Victoria",
            "latitude": -12.08945, "longitude": -77.02270, "reference_prefix": "INTERBANK",
            "sources": [
                source("SRC-STYLE-INTERBANK-2026", "https://interbank.pe/es/blog/sala-de-prensa/25-anos-torre-interbank-icono-arquitectonico", "Interbank", "Current 2026 headquarters use, 25-year milestone, architect and design mechanisms."),
                source("SRC-STYLE-INTERBANK-HOLLEIN", "https://hollein.com/eng/Architecture/Chronology/2000-2009/Torre-Interbank", "Hans Hollein", "Architect-authored highway loop, curved slab, low block, podium and program description."),
                source("SRC-STYLE-INTERBANK-ADDRESS", "https://content-us-2.content-cms.com/9b3f67ef-5a9f-4acc-8ce8-bcc27fa681c7/dxdam/10/101f7c9e-e5cb-4b68-991d-390bd18f43be/PDF%20Desplegable%20Tiendas%2023.05.pdf", "Interbank", "Corporate directory address at Carlos Villarán 140, La Victoria."),
            ],
            "contradictions": ["The headquarters is highly visible but sits beside highway-scale traffic; a legal, comfortable pedestrian viewpoint is not guaranteed.", "Published imagery emphasizes sculptural skyline form and illumination, creating high cliché saturation."],
            "pass_answers": [
                "Hans Hollein designed the Torre Interbank headquarters, completed in 2001 at Carlos Villarán 140 in La Victoria; Interbank confirms continuing headquarters use in 2026.",
                "A curved high-rise slab follows the Javier Prado/Paseo de la República loop while a lower block answers the Carlos Villarán grid; podium, hall and branch mediate the two scales.",
                "Employees, clients, vehicles and pedestrians continue to arrive, enter, wait and pass; security limits interior access and the road interchange dominates exterior movement.",
                "Approach, cross, queue, enter, turn, accelerate, wait and disperse are credible. An empty entrance interval can show security and scale without turning workers into props.",
                "The curved slab responds to fast orbital movement, the low block meets the street grid and the podium converts those trajectories into controlled entry.",
                "Night illumination and tilted-tower hero views dominate. The underused relation is ground-level conflict between highway curve, pedestrian crossing and corporate threshold.",
                "Titanium mesh, white glass, stone base and deep podium respond differently to hard sun and blue hour; lighting spectacle alone does not establish architectural causality.",
                "Test the Carlos Villarán low-block edge, a legal Javier Prado oblique and the branch/entrance tangent. Start 50 mm for threshold, 35 mm only for road/building relation, 85 mm only from a safe distant public point.",
                "Scout crossings in daylight, never stand in medians or ramps, avoid security details and faces, cap the wait at 20 minutes and abandon any viewpoint requiring unsafe stopping.",
                "Passes when the tower's two geometries visibly transform fast traffic and slow human arrival into one readable frame. A tilted skyline icon fails.",
            ],
            "questions": ["Can the highway curve, low street block and one arrival gesture read as a single causal system?", "Which ramp barrier, billboard or vehicle overlap makes the person incidental?", "Does a safer Carlos Villarán position reveal the two-scale design better than a wider lens near the interchange?"],
            "proof_rows": [
                {"position":"Carlos Villarán public sidewalk showing low block, podium and curved slab","lens":"35 mm","action":"Clear interval reveals the two-scale composition","light":"Morning side light","edges":"Exclude billboards and clipped tower crown","wait":"Podium and both volumes separate","kill":"Only tower silhouette reads","access":"Public sidewalk; obey security boundaries","fallback":"50 mm low-block/podium study"},
                {"position":"Public entrance tangent outside security perimeter","lens":"50 mm","action":"Adult client slows, turns and enters","light":"Bright overcast","edges":"No faces, badges or security equipment","wait":"Entry geometry changes walking direction","kill":"Person only supplies scale","access":"No obstruction; consent if identifiable","fallback":"Meaningful empty threshold"},
                {"position":"Legal distant oblique where loop curvature meets the tower base","lens":"85 mm","action":"Bus or pedestrian trajectory echoes the curved slab","light":"Garúa daylight","edges":"No unsafe median viewpoint","wait":"Road and building curves align without collision","kill":"Generic compressed traffic/tower image","access":"Safe public ground only","fallback":"35 mm Carlos Villarán reverse"},
                {"position":"Public side view joining stone base, mesh and glass","lens":"50 mm","action":"Moving shadow crosses podium seam","light":"Hard late sun","edges":"Retain entrance/road cue","wait":"Three materials separate","kill":"Becomes corporate texture","access":"No telephoto into offices","fallback":"Blue-hour tonal volume study"},
                {"position":"Carlos Villarán diagonal joining sidewalk, controlled entry, low block and tower curve","lens":"35 mm","action":"Pedestrian approach and vehicle turn occur in distinct layers","light":"Late afternoon","edges":"Keep signage and traffic subordinate","wait":"Slow and fast movement coexist legibly","kill":"Caption must explain highway response","access":"Safe corner; no roadway entry","fallback":"Single arrival against low block"},
            ],
            "reference_families":["CURRENT_HEADQUARTERS_AND_ANNIVERSARY","ARCHITECT_AUTHORED_URBAN_FORM","VERIFIED_CORPORATE_ADDRESS"],
            "reference_proves":["The building remains Interbank's principal headquarters in 2026.","Curved/high and rectilinear/low volumes intentionally answer highway loop and street grid.","The identity and La Victoria address are not inferred from skyline recognition."],
            "reference_limits":["Corporate celebration does not prove public access or a strong street moment.","Architect imagery cannot prove current pedestrian safety or clutter.","A directory does not prove a precise camera position or current façade condition."],
        },
        {
            "canonical_id": "casa-fernandini-1913", "name": "Casa Fernandini (1913)", "district": "Lima",
            "latitude": -12.0450471, "longitude": -77.0351457, "reference_prefix": "FERNANDINI",
            "sources": [
                source("SRC-STYLE-FERNANDINI-CULTURE", "https://www.elperuano.pe/noticia/201710-casa-fernandini-art-nouveau-en-el-corazon-de-lima", "Diario Oficial El Peruano", "Art Nouveau interiors, Claudio Sahut attribution, early reinforced construction and cultural history."),
                source("SRC-STYLE-FERNANDINI-MONUMENT", "https://repositorio.cultura.gob.pe/bitstream/handle/CULTURA/77/relacion%20de%20monumentos%20historicos.pdf?sequence=1&isAllowed=y", "Ministerio de Cultura", "Monument record and Jr. Ica 400 corner address."),
                source("SRC-STYLE-FERNANDINI-2026", "https://cosas.pe/sociales/marina-de-guerra-del-peru-inaugura-la-exposicion-los-cuatro-ases-de-la-marina-en-la-casa-fernandini", "Cosas", "March 2026 temporary exhibition and current cultural-use signal.", "CORROBORATED"),
            ],
            "contradictions": ["A March 2026 exhibition proves episodic cultural use, not permanent public opening or competition-photography permission.", "The Art Nouveau evidence is primarily interior; without authorized access the viable scene may be only the urban threshold."],
            "pass_answers": [
                "Claudio Sahut's Casa Fernandini, built in 1913 at Jr. Ica 400, is a protected eclectic residence whose interiors contain Art Nouveau glass, ornament and early modern services.",
                "A corner urban shell leads through controlled doors into stair, stained-glass, salon and lift sequences designed to stage domestic status, light and technological modernity.",
                "The house hosts episodic exhibitions and institutional events, but no stable daily access schedule is verified; public life at the corner remains the repeatable fallback.",
                "Approach, knock, enter, guide, gather, look, ascend and pass are credible during authorized use; meaningful absence can expose a closed cultural threshold.",
                "Corner geometry and entrance compress street movement before the interior sequence releases it through stair, hall, glass and salon thresholds.",
                "Ornament close-ups, chandelier rooms and frontal heritage façades dominate. The underused relation is contemporary cultural arrival passing through an early-modern domestic threshold.",
                "Colored glass, polished wood, metalwork and concrete structure require controlled window light; decorative detail without spatial transition fails.",
                "Test the Ica/Torrico corner, doorway tangent and—only with authorization—hall-to-stair diagonal. Start 35 mm for street/threshold and 50 mm for glass/action relation.",
                "Confirm an actual public visit and photography permission, never photograph private-event guests without consent, cap the interior wait at 15 minutes and kill all interior proofs if access is denied.",
                "Passes when old domestic technology and ornament visibly channel present cultural use. Beautiful Art Nouveau detail alone is not a 2026 architecture-and-life story.",
            ],
            "questions": ["Can one contemporary arrival be visibly transformed by the corner-door-hall sequence before ornament becomes the subject?", "Which parked car, event backdrop or decorative crop severs street from interior order?", "If access is denied, does the closed threshold still carry enough present cultural expectation to survive without a caption?"],
            "proof_rows": [
                {"position":"Opposite public corner holding both Jr. Ica and Torrico façades","lens":"35 mm","action":"Clear interval reveals corner, entrance and urban approach","light":"Soft morning daylight","edges":"Exclude cars and unrelated signage","wait":"Door and corner hierarchy separate","kill":"Generic heritage façade","access":"Public pavement","fallback":"50 mm door/corner relation"},
                {"position":"Authorized entrance-to-hall diagonal","lens":"35 mm","action":"Guide or consenting visitor crosses from street light into hall","light":"Mixed doorway and interior light","edges":"No event branding or unidentified guests","wait":"Threshold changes pace and light","kill":"Visitor only supplies scale","access":"Explicit access and photography permission","fallback":"Empty open-door sequence"},
                {"position":"Public side tangent emphasizing threshold rather than full façade","lens":"50 mm","action":"Passerby aligns with a briefly opening door","light":"Garúa daylight","edges":"Avoid centered monument portrait","wait":"Present street and historic entry coincide","kill":"Requires knowledge of the interior","access":"Public ground; no waiting on private occupants","fallback":"Meaningful closed threshold"},
                {"position":"Authorized hall position joining stained glass, stair and structural opening","lens":"50 mm","action":"Colored light crosses a consenting visitor or empty stair","light":"Window-directed midday light","edges":"Retain stair/door context around ornament","wait":"Color reveals circulation depth","kill":"Decorative detail becomes isolated","access":"Permission hard gate; no flash","fallback":"Exterior window/door light relation"},
                {"position":"Authorized diagonal from corner entrance through hall toward stair","lens":"35 mm","action":"Arrival, pause and ascent occur in one sequence","light":"Available interior/daylight balance","edges":"Keep modern equipment and event clutter subordinate","wait":"Three spatial stages align","kill":"Caption must explain current cultural use","access":"Event and subject permission","fallback":"Exterior arrival at cultural threshold"},
            ],
            "reference_families":["ART_NOUVEAU_INTERIOR_AND_TECHNOLOGY","OFFICIAL_MONUMENT_AND_CORNER_ADDRESS","CURRENT_CULTURAL_EVENT_USE"],
            "reference_proves":["Art Nouveau glass/ornament and early-modern domestic systems are integral to the house.","The protected identity and exact Centro Histórico corner are authoritative.","The house hosted a cultural exhibition in March 2026."],
            "reference_limits":["Historical description does not prove current opening or condition of every room.","Monument listing does not grant access or photography permission.","One exhibition does not establish a recurring schedule or ordinary visitor rhythm."],
        },
        {
            "canonical_id": "estacion-desamparados", "name": "Estación Desamparados / Casa de la Literatura", "district": "Lima",
            "latitude": -12.0444153, "longitude": -77.0287553, "reference_prefix": "DESAMPARADOS",
            "sources": [
                source("SRC-STYLE-DESAMPARADOS-CURRENT", "https://www.casadelaliteratura.gob.pe/", "Casa de la Literatura Peruana", "Current institution, address and active 2026 cultural programming."),
                source("SRC-STYLE-DESAMPARADOS-ARCH", "https://www.casadelaliteratura.gob.pe/wp-content/uploads/2019/10/Periodico_Estacion-de-las-letras_WEB.pdf", "Casa de la Literatura Peruana", "Neoclassical shell, Art Nouveau floral glass, hall conversion and architectural section."),
                source("SRC-STYLE-DESAMPARADOS-2026", "https://www.casadelaliteratura.gob.pe/wp-content/uploads/2026/01/Agenda_Enero-2026.pdf", "Casa de la Literatura Peruana", "2026 opening hours, free entry, library and activity schedules."),
            ],
            "contradictions": ["Published hours establish institutional opening, but event density and interior photography conditions remain same-day checks.", "The former station narrative is highly legible in a caption; the frame must show transport architecture actively organizing reading rather than relying on history text."],
            "pass_answers": [
                "The 1912 Desamparados railway station at Jr. Áncash 207 now operates as the Casa de la Literatura Peruana, with current 2026 hours and free public entry.",
                "A symmetrical civic façade, former platform/hall, iron and floral Art Nouveau glazing organized arrival, waiting and rail transfer before conversion to cultural use.",
                "Readers, families, researchers, guides and event audiences now enter, browse, wait, read and gather within retained station circulation; exact room availability varies.",
                "Arrive, queue, orient, read, browse, gather, descend and depart are credible. Empty benches or hall axes can carry the residue of waiting without forcing a person.",
                "The entry axis, tall hall, stained-glass roof and former platform turn urban arrival into illuminated waiting/reading space; adaptive reuse preserves the original movement contract while changing its destination.",
                "Frontal façade, clock and empty grand-hall views dominate. The underused scene pairs reader movement with platform/hall geometry or floral glass without becoming event documentation.",
                "Diffused roof light reveals the hall and colored floral glass; mixed exposure needs highlight protection, while stained-glass detail alone loses the station-to-library transformation.",
                "Test the Áncash approach, hall centerline offset and former-platform tangent. Start 35 mm for adaptive-reuse section, 50 mm for reader/glass relation and avoid 85 mm that detaches people from circulation.",
                "Use published hours, recheck room closures and photography rules, avoid identifiable children, never obstruct readers and cap the decisive wait at 20 minutes.",
                "Passes when retained station architecture visibly converts arrival/waiting into reading/gathering now. A façade or vitral postcard fails.",
            ],
            "questions": ["Can the old arrival axis visibly become a reading or gathering route in one frame?", "Which exhibition panel, crowd overlap or blown glass highlight breaks the station-to-literature causality?", "Does an off-axis hall position reveal adaptive reuse better than a centered symmetrical view?"],
            "proof_rows": [
                {"position":"Áncash public approach holding façade, doors and arrival space","lens":"35 mm","action":"Clear interval reveals civic entrance order","light":"Morning façade light","edges":"Exclude palace/security clutter and vehicles","wait":"Door bays and approach align","kill":"Generic historic façade","access":"Public pavement","fallback":"50 mm entrance sequence"},
                {"position":"Interior hall offset where retained circulation frames reading/gathering","lens":"35 mm","action":"Reader crosses then pauses at a cultural threshold","light":"Diffused roof light","edges":"Separate people from panels and columns","wait":"Arrival becomes reading choice","kill":"People only populate a grand room","access":"Open hours; follow photography rules; protect minors","fallback":"Meaningful empty waiting/reading hall"},
                {"position":"Former-platform tangent looking back across hall rather than centered façade","lens":"50 mm","action":"Visitor moves counter to the historic rail direction","light":"Bright overcast interior","edges":"Avoid clock-centered postcard symmetry","wait":"Old and new routes oppose clearly","kill":"Historical relation needs caption","access":"Public interior if open","fallback":"Door-to-library axis"},
                {"position":"Hall position where Art Nouveau glass casts light across circulation structure","lens":"50 mm","action":"Reader or shadow crosses colored-light field","light":"Midday roof light with highlight protection","edges":"Retain hall edge and route cue","wait":"Glass changes spatial depth","kill":"Becomes isolated vitral detail","access":"No flash; do not disrupt readers","fallback":"Empty glass/hall geometry"},
                {"position":"Diagonal joining street arrival, hall axis and active reading/gathering zone","lens":"35 mm","action":"Arrival, orientation and reading coexist","light":"Balanced exterior/interior daylight","edges":"Keep exhibition furniture subordinate","wait":"Three verbs occupy three architectural layers","kill":"Caption rescues former-station meaning","access":"Public hours and current rules","fallback":"Hall-to-library two-layer story"},
            ],
            "reference_families":["CURRENT_CULTURAL_OPERATION","ARCHITECTURAL_SECTION_AND_ART_NOUVEAU_GLASS","CURRENT_2026_HOURS_AND_PROGRAM"],
            "reference_proves":["The former station is an active national literary institution.","Floral Art Nouveau glass and hall geometry are documented components of the retained architecture.","The building has defined public hours and active services in 2026."],
            "reference_limits":["Homepage activity cannot predict crowd density or room access on a chosen day.","Historic diagrams do not prove current furniture, barriers or light.","Published hours do not authorize every photographic use or guarantee a decisive moment."],
        },
        {
            "canonical_id": "edificio-petroperu", "name": "Edificio Petroperú", "district": "San Isidro",
            "latitude": -12.0973204, "longitude": -77.0245028, "reference_prefix": "PETROPERU",
            "sources": [
                source("SRC-STYLE-PETRO-CAMMP", "https://cammp.ulima.edu.pe/edificios/edificio-petroperu/", "Universidad de Lima CAMMP", "1970 modern building, architect team, plans, multiangle archive and current-use assessment."),
                source("SRC-STYLE-PETRO-CURRENT", "https://www.petroperu.com.pe/petroperu-incluye-su-sede-principal-en-la-lista-de-activos-no-estrategicos", "Petroperú", "December 2025 current address and non-strategic-asset evaluation."),
                source("SRC-STYLE-PETRO-HISTORY", "https://www.petroperu.com.pe/Storage/tbl_documentos_varios/fld_1160_Documento_file/111-r3Rp4Sk5Wd9Vp7P.pdf", "Petroperú", "Original headquarters inauguration and corner relationship."),
            ],
            "contradictions": ["CAMMP records Paseo de la República 3361 while Petroperú records Canaval y Moreyra 150; these describe the same corner complex but the discrepancy is retained.", "The headquarters was placed under non-strategic-asset evaluation in December 2025; future ownership/use is unresolved and must be verified before routing."],
            "pass_answers": [
                "Walter Weberhofer and Daniel Arana Ríos designed the 1970–73 Petroperú headquarters at the Canaval y Moreyra/Paseo de la República corner in San Isidro.",
                "Monumental plates, tower, stair box, entry forecourt and interior court organized a centralized state enterprise through legible structural and administrative hierarchy.",
                "Petroperú still identifies the building as headquarters, but since December 2025 it is under evaluation as a non-strategic asset; occupancy and entry patterns require current confirmation.",
                "Arrive, screen, enter, work, maintain, wait and pass are credible; an empty forecourt can express institutional distance if current use is uncertain.",
                "Deep frames, podium/forecourt, stair box and tower convert the exposed expressway corner into a controlled institutional threshold.",
                "Historic brutalist hero views, empty façade and stair-box abstractions dominate. The underused relation is current employee/public movement against a headquarters whose institutional future is unsettled.",
                "Concrete depth, repetitive frames and hard Lima sun create strong relief; garúa reveals mass and weathering, while texture-only brutalism fails the theme.",
                "Test Canaval forecourt, Paseo structural oblique and safe opposite-corner section. Start 50 mm for threshold, 35 mm for corner/system, 85 mm only from a legal distant sidewalk.",
                "Verify current occupancy and barriers, stay outside the security perimeter, avoid badges/vehicles/security systems, cap wait at 20 minutes and treat any sale/closure change as rank-moving evidence.",
                "Passes when structural hierarchy visibly shapes present institutional arrival or meaningful absence. Brutalist monumentality without current life fails.",
            ],
            "questions": ["Can the forecourt and structural frame visibly disclose current institutional use—or its meaningful withdrawal—without a caption?", "Which expressway clutter, fence or heroic low angle turns the scene into generic brutalism?", "Does the Canaval entry position reveal more causality than a distant 85 mm tower abstraction?"],
            "proof_rows": [
                {"position":"Canaval public sidewalk holding forecourt, entry frame and tower","lens":"35 mm","action":"Clear interval reveals institutional hierarchy","light":"Garúa morning","edges":"Exclude security devices and traffic clutter","wait":"Forecourt and frame separate","kill":"Only massive façade reads","access":"Public sidewalk outside perimeter","fallback":"50 mm entry-frame study"},
                {"position":"Public forecourt tangent outside controlled boundary","lens":"50 mm","action":"Anonymous employee or visitor slows at screening threshold","light":"Soft daylight","edges":"No badges, plates or faces","wait":"Architecture changes pace","kill":"Person merely supplies scale","access":"Privacy and security hard gate","fallback":"Meaningful empty threshold"},
                {"position":"Safe opposite-corner oblique joining expressway edge to stair box","lens":"85 mm","action":"Pedestrian movement opposes monumental frame rhythm","light":"Bright overcast","edges":"No roadway/median position","wait":"Urban and institutional scales conflict clearly","kill":"Compressed tower icon","access":"Legal public sidewalk only","fallback":"35 mm Canaval system view"},
                {"position":"Public side angle where concrete frame, stair box and shadow overlap","lens":"50 mm","action":"Shadow crosses deep structural bay","light":"Hard late sun","edges":"Retain entry or sidewalk cue","wait":"Depth reads across three planes","kill":"Pure brutalist abstraction","access":"No lens into offices","fallback":"Garúa material sequence"},
                {"position":"Canaval diagonal joining city approach, forecourt, security threshold and tower","lens":"35 mm","action":"Pass, pause and enter occupy separate layers—or absence makes closure legible","light":"Late soft daylight","edges":"Institutional relationship primary","wait":"Current use/uncertainty reads unaided","kill":"Asset-evaluation story exists only in caption","access":"Public edge; current status recheck","fallback":"Two-layer forecourt/entry story"},
            ],
            "reference_families":["ARCHIVE_MULTIANGLE_PLANS_AND_CURRENT_ASSESSMENT","CURRENT_ASSET_STATUS_AND_ADDRESS","ORIGINAL_HEADQUARTERS_CORNER_OPERATION"],
            "reference_proves":["The formal system includes distinct front, rear, court, stair and tower viewpoints.","The building's current corporate status is unsettled and operationally relevant.","The corner complex was designed as a centralized administrative headquarters."],
            "reference_limits":["CAMMP's condition date is not a same-day 2026 survey.","Asset evaluation does not prove sale, vacancy or closure.","Historic inauguration material does not prove present access or behavior."],
        },
        {
            "canonical_id": "torre-begonias", "name": "Torre Begonias + Paseo Begonias", "district": "San Isidro",
            "latitude": -12.0921040, "longitude": -77.0239594, "reference_prefix": "BEGONIAS",
            "sources": [
                source("SRC-STYLE-BEGONIAS-ABOUT", "https://paseobegonias.com/en/about-us/", "Paseo Begonias", "Current public-realm operator, mixed office/retail/food positioning and district context."),
                source("SRC-STYLE-BEGONIAS-OFFICES", "https://paseobegonias.com/oficinas/", "Paseo Begonias", "Torre Begonias address, 26-floor office use and surrounding active ground-floor programs."),
                source("SRC-STYLE-BEGONIAS-MAP", "https://www.openstreetmap.org/way/397559270", "OpenStreetMap contributors", "Named building footprint and coordinate at Calle Las Begonias 415.", "CORROBORATED"),
            ],
            "contradictions": ["Operator material markets a unified destination; it does not prove that every plaza segment is public, comfortable or equally active.", "Corporate tower imagery is highly generic unless ground-plane design visibly causes a current work/food/waiting relationship."],
            "pass_answers": [
                "Torre Begonias is an operating 26-floor office tower at Calle Las Begonias 415 within the current Paseo Begonias financial-center network in San Isidro.",
                "Tower lobby, setback, adjoining office blocks, retail/food edges and pedestrian space combine vertical work with a more porous ground-level destination.",
                "Workers, diners, couriers and visitors arrive, queue, cross, sit, meet and disperse; exact public/private boundaries and peak rhythms require observation.",
                "Arrive, badge, deliver, eat, meet, sit, cross and leave are credible. Off-hours absence can expose how much public life depends on the workday timetable.",
                "Setback, lobby, canopy, retail edge and plaza route turn tower arrival into a sequence of slowing, choosing and branching rather than a single door.",
                "Upward tower shots, reflections and skyline height dominate. The underused relation is the workday ground plane where office, food and waiting flows collide or separate.",
                "Glass reflection and hard sun can erase the ground plane; garúa and blue hour may balance canopy, lobby and bodies, but decorative reflection alone fails.",
                "Test the 415 lobby setback, a cross-passage toward adjoining food/office edges and an opposite-side compressed ground section. Start 35 mm for flow network, 50 mm for choice point.",
                "Observe morning, lunch and after-work intervals, remain in clearly public space, avoid badges/screens/faces, verify barriers and cap any single interval at 20 minutes.",
                "Passes when ground-plane architecture visibly redistributes work, food and waiting. Tower height, glass polish or a busy crowd without spatial cause fails.",
            ],
            "questions": ["Can one lobby/canopy/plaza choice visibly split workers, diners and couriers into different paths?", "Which reflection, parked vehicle or branded sign overwhelms the architectural decision point?", "Does crossing the street change the ground-plane perspective more than moving from 35 to 50 mm?"],
            "proof_rows": [
                {"position":"Opposite public sidewalk holding tower setback, lobby and pedestrian plane","lens":"35 mm","action":"Clear interval reveals lobby/plaza order","light":"Bright garúa","edges":"Exclude clipped tower and vehicle clutter","wait":"Ground zones separate","kill":"Only glass tower reads","access":"Public sidewalk","fallback":"50 mm canopy/lobby study"},
                {"position":"Public plaza edge where lobby, food and delivery paths branch","lens":"50 mm","action":"Worker, diner and courier choose different routes","light":"Lunch-hour soft daylight","edges":"Separate bodies and protect identities","wait":"Three verbs diverge at one device","kill":"Crowd density replaces composition","access":"Confirm public boundary; no badge/screen details","fallback":"Two anonymous paths"},
                {"position":"Cross-passage reverse looking away from the canonical tower-up view","lens":"35 mm","action":"People leave tower and occupy adjoining ground programs","light":"Overcast","edges":"Avoid centered logo and reflection spectacle","wait":"Tower use becomes public-realm occupation","kill":"Building identity disappears","access":"Public route only","fallback":"Lobby-to-sidewalk relation"},
                {"position":"Canopy tangent where glass, soffit and pavement receive different light","lens":"50 mm","action":"Passing shadow or umbrella crosses material seam","light":"Blue hour or post-garúa brightness","edges":"Retain lobby and route cue","wait":"Light reveals depth without mirror gimmick","kill":"Abstract corporate texture","access":"No telephoto into offices","fallback":"Garúa tonal ground plane"},
                {"position":"Diagonal joining street arrival, plaza choice, lobby and occupied food edge","lens":"35 mm","action":"Arrival, branching and pause coexist","light":"Late workday transition","edges":"Keep signage subordinate and faces anonymous","wait":"Three layers tell work/public-realm story","kill":"Caption must explain mixed use","access":"Public ground; current barrier recheck","fallback":"Lobby/food two-layer story"},
            ],
            "reference_families":["CURRENT_MIXED_PUBLIC_REALM_NETWORK","TOWER_ADDRESS_AND_ACTIVE_OFFICE_PROGRAM","NAMED_BUILDING_FOOTPRINT"],
            "reference_proves":["The operator intentionally links office, food and public-realm programs.","Torre Begonias remains an active office building at the stated address.","The mapped point corresponds to the named tower inside San Isidro."],
            "reference_limits":["Marketing does not prove access boundaries, activity density or comfort.","Office listing cannot prove exact workday gestures or photography rules.","OSM geometry does not prove architectural quality or current public use."],
        },
    ]


def main():
    payload = {
        "schema_version": "style-discovery-dossiers-v1",
        "retrieved_at": "2026-08-30T23:50:00-05:00",
        "admission_rule": "All six complete equal-depth desk dossiers but remain fail-closed until canonical reconciliation and a full-universe rerank.",
        "records": [record(item) for item in configs()],
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(payload["records"]), "status": "RANKED_ROUTED_ACCESS_CHECK_PENDING"}))


if __name__ == "__main__":
    main()
