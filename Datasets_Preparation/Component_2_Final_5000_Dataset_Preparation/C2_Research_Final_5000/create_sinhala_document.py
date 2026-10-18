from pathlib import Path
import csv,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_BREAK
P=Path(__file__).parent
R=json.loads((P/'C2_Independent_QA_and_Baseline.json').read_text())
M=json.loads((P/'C2_Method_Provenance_and_Parameters.json').read_text())
with (P/'C2_Master_5000_ZoneDays.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
ex=rows[0]
with np.load(P/'C2_STGCN_Model_Ready_43_Windows.npz') as z:
   y=z['y_suitability']; nodes=z['node_ids']; a=z['normalized_adjacency']; X=z['X']

def font_of(run,size=None,bold=None,color=None):
    run.font.name='Noto Sans Sinhala'
    rPr=run._element.get_or_add_rPr()
    rfonts=rPr.rFonts
    if rfonts is None:
        rfonts=OxmlElement('w:rFonts');rPr.insert(0,rfonts)
    for key in ('ascii','hAnsi','eastAsia','cs'):
        rfonts.set(qn('w:'+key),'Noto Sans Sinhala')
    if size:run.font.size=Pt(size)
    if bold is not None:run.bold=bold
    if color:run.font.color.rgb=RGBColor(*color)
    return run

def set_cell_shading(cell,fill):
    tcpr=cell._tc.get_or_add_tcPr();shd=OxmlElement('w:shd');shd.set(qn('w:fill'),fill);tcpr.append(shd)

def para(text='',size=None,bold=None,color=None,space_after=5,style=None):
    p=doc.add_paragraph(style=style)
    p.paragraph_format.space_after=Pt(space_after)
    p.paragraph_format.line_spacing=1.20
    font_of(p.add_run(text),size,bold,color)
    return p

def heading(text,level=1):
    p=doc.add_paragraph(style=f'Heading {level}')
    p.paragraph_format.space_before=Pt(12 if level==1 else 7)
    p.paragraph_format.space_after=Pt(6)
    font_of(p.add_run(text),13 if level==1 else 10.5,True,(19,71,89) if level==1 else (36,92,102))

def bullets(items):
    for item in items:
        p=doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after=Pt(3)
        p.paragraph_format.line_spacing=1.15
        font_of(p.add_run(item),9)

def table(headers,values,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.style='Light Shading Accent 1';t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for c,h in zip(t.rows[0].cells,headers):
       c.text='';set_cell_shading(c,'164859')
       c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
       font_of(c.paragraphs[0].add_run(h),8,True,(255,255,255))
    for ri,values_row in enumerate(values):
       cells=t.add_row().cells
       for c,tx in zip(cells,values_row):
          c.text='';c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
          font_of(c.paragraphs[0].add_run(str(tx)),7.7)
          if ri%2==1:set_cell_shading(c,'F0F7F8')
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

# Charts informative only. No navigation map intended.
Mdata=np.array([[float(r['yft_habitat_suitability_index']) for r in rows[-100:]]]).reshape(10,10)
fig,ax=plt.subplots(figsize=(7.6,3.7));im=ax.imshow(Mdata,origin='lower',aspect='auto',cmap='viridis')
ax.set(xlabel='Synthetic grid column (west -> east)',ylabel='Synthetic grid row (south -> north)',title='Yellowfin habitat suitability proxy - 2025-02-19')
fig.colorbar(im,ax=ax,label='Synthetic index [0,1]');fig.tight_layout();fig.savefig(P/'C2_Simulated_Suitability_Heatmap.png',dpi=170);plt.close(fig)
all_sst=np.array([float(r['sst_c']) for r in rows]).reshape(50,100).mean(axis=1)
all_chl=np.array([float(r['chlorophyll_a_mg_m3']) for r in rows]).reshape(50,100).mean(axis=1)
fig,ax=plt.subplots(figsize=(7.6,3.2));ax.plot(range(1,51),all_sst,linewidth=2,label='Mean SST (°C)');ax2=ax.twinx();ax2.plot(range(1,51),all_chl,linewidth=2,linestyle='--',label='Mean chlorophyll-a')
ax.set(xlabel='Synthetic day index',ylabel='SST (°C)');ax2.set_ylabel('Chlorophyll-a (mg/m³)');ax.grid(True,alpha=.2);ax.set_title('Scenario time series: spatially averaged SST and chlorophyll-a');fig.tight_layout();fig.savefig(P/'C2_Simulated_TimeSeries.png',dpi=170);plt.close(fig)

NAVY=RGBColor(16,55,69)
TEAL=RGBColor(14,104,103)
doc=Document();section=doc.sections[0]
section.top_margin=Inches(.77);section.bottom_margin=Inches(.75)
section.left_margin=Inches(.82);section.right_margin=Inches(.80)
styles=doc.styles
normal=styles['Normal'];normal.font.name='Noto Sans Sinhala';normal.font.size=Pt(9)
normal.paragraph_format.space_after=Pt(5)
for st in ['Normal','List Bullet']:
    styles[st].font.name='Noto Sans Sinhala'
for n in [1,2]:
    styles[f'Heading {n}'].font.name='Noto Sans Sinhala'
header=section.header.paragraphs[0]
header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
font_of(header.add_run('COMPONENT 02  /  DATASET JUSTIFICATION  /  RESEARCH PROTOTYPE'),7,True,(63,110,116))
foot=section.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
font_of(foot.add_run('C2 • Physics-constrained synthetic scenario • Research use only • 2026-10-16'),7,None,(92,112,121))

p=doc.add_paragraph();p.paragraph_format.space_before=Pt(15)
font_of(p.add_run('RESEARCH DATASET REPORT  |  COMPONENT 02'),9,True,(14,104,103))
p=doc.add_paragraph();p.paragraph_format.space_after=Pt(12)
font_of(p.add_run('ශ්‍රී ලංකාවේ ධීවර කලාප නිර්දේශ සඳහා\nSpatiotemporal AI Dataset'),19,True,(16,55,69))
p=doc.add_paragraph()
font_of(p.add_run('Multi-Objective Spatial Fishing Ground Recommendation & Catch Opportunity Engine'),10,True,(20,95,101))
para('සම්පූර්ණ සිංහල විද්‍යාත්මක සාධාරණීකරණ ලේඛනය | දත්ත පරිමාව: 5,000 Zone-Day Records | අනුවාදය: 1.0 (Synthetic Prototype)',9,None,(87,102,108))
para('වැදගත් නිවේදනය: මෙම දත්තවල කිසිදු සැබෑ Catch Observation එකක් හෝ Copernicus/NASA වෙතින් බාගත කළ සජීවී/ඓතිහාසික Measurement එකක් අඩංගු නොවේ. මෙහි suitability score හා pseudo-probability යනු simulation එකක අගයන්ය. ඒවා සැබෑ මසුන් අල්ලාගැනීමේ සම්භාවිතාවක් හෝ යාත්‍රා ගමන් කිරීමට අවසරයක් නොවේ.',9,True,(157,57,57))

table(['ඇගයීම','විස්තර'],[
('Primary dataset','5,000 = 100 sea-grid nodes × 50 days'),
('Time period','2025-01-01 සිට 2025-02-19 (simulation dates)'),
('Species','Yellowfin tuna සහ Skipjack tuna'),
('Graph','100 nodes, 360 directed 4-neighbour edges'),
('ST-GCN tensors','X: (43, 7, 100, 5); y: (43, 100, 2)'),
('Internal QA',f"{R['QA_passed']}/{R['QA_total']} පරීක්ෂණ සමත්; සැබෑ-field validation නොවේ")])

heading('1. පර්යේෂණයේ පසුබිම සහ අරමුණ')
para('උඩුගත කළ මුල් Research Component Specification එකට අනුව Component 02 හි අරමුණ වන්නේ මසුන් සිටිය හැකි කලාප පමණක් සොයා දීම නොව, මසුන් අල්ලාගැනීමේ අවස්ථාව, ගමන් දුර සහ ඉන්ධන වියදම එකට සලකා ධීවර කලාප තෝරාගැනීමට සහාය වීමයි. යෝජිත ආකෘතිය ST-GCN + Spatial Attention වන අතර Pareto-optimal multi-objective optimization එක අවසන් decision layer එක ලෙස යොදාගනී.')
para('මෙම වාර්තාව සකස් කරන ලද 5,000-record data package එකේ භෞතික-ගණිතමය consistency, biological heuristics, data provenance, preprocessing, quality tests සහ පර්යේෂණ සීමාවන් පැහැදිලි කරයි. එය “සැබෑ දත්තවලින් ඉහළ නිරවද්‍යතාවක් ලැබුණා” යන ප්‍රකාශය නොකරයි.')

heading('2. Data Provenance: සැබෑ මූලාශ්‍ර සහ නිර්මාණය කළ අගයන්')
table(['දත්ත අංගය','පර්යේෂණ මූලාශ්‍රය','මෙම CSV තුළ තත්ත්වය'],[
('SST / surface current','Copernicus Marine [1]','Synthetic numerical field'),
('Chlorophyll-a','NASA MODIS [3]; Copernicus [2]','Synthetic positive field'),
('Species ecology','NOAA/FAO [4], [5], [9]','Assumed heuristic parameters'),
('Fishing catches / CPUE','PFZ validation study [6]','Actual observations = 0'),
('Route / fuel cost','IHO nautical mile [8]','Scenario physical units + assumptions'),
('Pareto set','Deb et al. [7]','Computed non-dominated alternatives')])
para('Copernicus Marine [1] මඟින් දෛනික ocean temperature සහ eastward/northward currents ලබාගත හැක. NASA [3] සහ Copernicus Ocean Colour [2] මඟින් Chlorophyll-a ආශ්‍රිත තොරතුරු ලබාගත හැක. මෙම බාහිර මූලාශ්‍ර මෙහි variable definitions සහ future replacement plan සඳහා උපුටා දක්වා ඇති අතර, ඔවුන්ගේ මිනුම් කිසිවක් මෙම dataset එකට import කර නොමැත.')

heading('3. Spatial–Temporal Dataset Architecture')
para('5.22°N–5.76°N සහ 79.78°E–80.77°E ලෙස නිර්මාණය කළ දකුණු මුහුදේ schematic 10 × 10 grid එකට දින 50ක දත්ත අදාළ කර ඇත. දිනය × Zone ID යන යුගලය unique primary key වේ. මෙම spatial domain සමුද්‍රීය නීති සීමා, coral reefs, maritime hazards, bathymetry හෝ fishing permissions අනුව නිවැරදිව verify කර නැත.')
para('Graph එකේ එක් cell එකට උතුරු, දකුණු, නැගෙනහිර සහ බටහිර අසල්වැසි cells සම්බන්ධ කර ඇත. සම්බන්ධතා 180ක් bidirectional ලෙස 360 directed edges බවට පරිවර්තනය කර ඇත. Edge weight = 1/(1 + d_km). Self-loop එකක් ඇතුළත් කර row normalization කළ adjacency matrix එක tensor file එකේ ඇත.')
para('C1 Component එක සමඟ මුල් spatial crosswalk එක සඳහා C1 dataset හි දැනට ඇති schematic Z01–Z10 offshore centroids අතර ආසන්නතම centroid ID එක ඇතුළත් කර ඇත. එය C1 safety decision එකක් නොවේ.')

heading('4. භෞතික විද්‍යාව: සාගර ධාරා ගණනය')
para('දත්ත generator එකේ ප්‍රධාන physics-based කොටස වන්නේ ද්විමාන, idealized incompressible horizontal velocity field එකකි. ඉදිරියට යා හැකි හා පෙරළා පැමිණිය හැකි තත්ත්වයට සංකේතවත් කර ඇති streamfunction ψ එකක් භාවිත කරයි:')
para('ψ(x,y,t) = A(t) sin(kx x + 0.14t) sin(ky y − 0.12t)',10,True,(18,82,91))
para('u(x,y,t) = u_bg(t) − ∂ψ/∂y     ;     v(x,y,t) = v_bg(t) + ∂ψ/∂x',9,True)
para('∂u/∂x + ∂v/∂y = 0',10,True,(18,82,91))
para('මෙහි x සහ y meter ඒකකවල local tangent-plane distances; ψ ඒකකය m²/s; u සහ v ඒකකය m/s. A(t) = 2300 + 280 sin(2πt/29) m²/s; kx = 2π/145000 m⁻¹; ky = 2π/105000 m⁻¹. ඉහත derivative cross terms එකිනෙක අවලංගු වන නිසා තෝරාගත් idealized two-dimensional flow එකේ divergence = 0 යන්න algebraic වශයෙන් සත්‍ය වේ. මෙය සැබෑ Indian Ocean circulation model එකක් නොවෙයි. Bathymetry, Coriolis forcing, friction හා 3D circulation ඇතුළත් කර නැත.')
para('Current speed: V = √(u² + v²). අදාල generated range එක 0.003–0.245 m/s වේ. Current vectors බාහිර ocean datasets වලින් සත්‍ය තත්ව පරීක්ෂා කිරීමට අවශ්‍යයි.')

heading('5. SST, Chlorophyll-a සහ Thermal Fronts')
para('Sea Surface Temperature (SST) සඳහා seasonal terms, smooth spatial patterns, local cool-water patch එකක් සහ autocorrelated random perturbations එකතු කර ඇත. මෙය shallow ocean temperature field එකක් සංකේතවත් කරන smooth scenario එකකි. 26.992–29.045 °C පරාසය යනු මෙහි simulation output එක පමණක් බව සලකන්න.')
para('Chlorophyll-a සඳහා ln(CHL) = −1.77 + 0.75 B(x,y,t) + spatial periodic terms + correlated noise ලෙස log-link එකක් භාවිත කර ඇත. එවිට CHL = exp( … ) > 0 mg/m³. Generated interval = 0.080–0.762 mg/m³. Chlorophyll-a මනින ඒකකය හා satellite concept එක NASA [3] මඟින් තහවුරු වේ; නමුත් මෙම expression එක ocean ecosystem එකක සත්‍ය growth model එකක් නොවේ.')
para('Thermal-front strength = G = √[(∂SST/∂x_km)² + (∂SST/∂y_km)²], ඒකකය °C/km. Grid එකේ neighbours අතර finite-difference derivative ගණනය කර ඇත. Research literature [6] මඟින් fronts සහ chlorophyll patches Potential Fishing Zones සමඟ සම්බන්ධ විය හැකි බවත්, ඒවා catch records භාවිත කර සනාථ කළ යුතු බවත් පෙන්වයි.')

doc.add_picture(str(P/'C2_Simulated_TimeSeries.png'),width=Inches(6.5))
para('රූපය 1. Synthetic SST සහ chlorophyll-a දෛනිකව වෙනස් වන ආකාරය. සැබෑ චන්ද්‍රිකා දත්ත නොවේ.',8,None,(90,102,111))

heading('6. ජීව විද්‍යාත්මක Habitat-Suitability Response')
para('NOAA [4], [9] සහ FAO [5] මඟින් tuna වර්ගවල උෂ්ණත්වය, ආහාර ජාලය සහ fronts/upwelling වැනි habitat features සම්බන්ධ තොරතුරු දක්වා ඇත. නමුත් ශ්‍රී ලංකා මුහුදු කලාපයට අදාල එකම “හොඳම SST” හෝ “catch probability” threshold එකක් එම මූලාශ්‍රවලින් ලැබෙන්නේ නැත. එබැවින් පහත parameters නිදර්ශන simulation assumptions ලෙස තෝරා ඇත.')
para('Temperature response: R_T = exp[−0.5 × ((T − T_opt)/σ_T)²]',9,True)
para('Chlorophyll response: R_CHL = CHL / (CHL + K_CHL)',9,True)
para('Front response: R_F = 1 − exp(−G / 0.026)',9,True)
para('Current response: R_V = exp[−0.5 × ((V − 0.22)/0.23)²]',9,True)
para('Habitat Index: H = wT·R_T + wCHL·R_CHL + wF·R_F + wV·R_V',9,True)
para('මෙහි සියලු response 0 හා 1 අතර වන අතර species-specific weights එකතුව 1 වේ. Temperature සඳහා Gaussian response හා CHL සඳහා saturating response තෝරා ඇත්තේ monotonic සහ bounded heuristic හැසිරීම ලබාගැනීමටයි. ඉදිරි empirical research එකකින් coefficients fit කිරීමට අවශ්‍යයි.')

table(['Parameter / weight','Yellowfin','Skipjack'],[
('Assumed T_opt','28.0 °C','28.6 °C'),('Assumed σ_T','2.2 °C','1.8 °C'),
('Assumed K_CHL','0.17 mg/m³','0.20 mg/m³'),
('Temperature weight','0.42','0.37'),('Food (CHL) weight','0.33','0.29'),
('Front weight','0.17','0.22'),('Current weight','0.08','0.12')])
para('CSV එකේ “synthetic_uncalibrated_probability” යන අගය ගණනය කළේ sigmoid(a + bH) ලෙස monotonic rescaling එකකිනි. Yellowfin: sigmoid(−2.80 + 4.40H); Skipjack: sigmoid(−2.65 + 4.25H). මෙය observed catches මත fit කළ probability model එකක් නොවන නිසා කිසිවිටෙක 70% catch chance වැනි operational ප්‍රකාශ සඳහා යොදාගන්න එපා.')

doc.add_picture(str(P/'C2_Simulated_Suitability_Heatmap.png'),width=Inches(6.3))
para('රූපය 2. Synthetic yellowfin habitat index — සිතියම්-තොරතුරු දක්වන demonstration එකක් පමණි; මෙය නාවික මාර්ගයක් හෝ සුරක්ෂිතතාව තහවුරුවක් නොවේ.',8,None,(90,102,111))

heading('7. ගමන් දුර, කාලය සහ Fuel-Cost Scenario')
para('Straight-line great-circle distance සඳහා Haversine formula භාවිත කර ඇත. මෙහි R = 6371.0088 km; ලක්ෂ්‍ය දෙක අතර latitude/longitude radians වලට පරිවර්තනය කළ යුතුයි.')
para('a = sin²(Δφ/2) + cos(φ1)cos(φ2)sin²(Δλ/2); d = 2R·asin(√a)',9,True)
para('Estimated one-way distance = 1.15 × d; round trip = 2 × estimated one-way distance. 1 nautical mile = 1.852 km යන්න IHO [8] මඟින් සනාථ කර ඇත. Assumed speed = 8 knots = 14.816 km/h; fuel rate = 6 L/h; fuel price = LKR 300/L (මිල ගවේෂණයකින් ලබාගත් වර්තමාන මිලක් නොවේ).')
para('Transit hours = roundtrip_km / (8 × 1.852); transit_fuel_L = hours × 6.',9,True)
para('On-site scenario: fishing_hours = 4; site_fuel_L = 4 × [2 + 8×current_speed(m/s)].',9,True)
para('Total scenario fuel = transit fuel + site fuel; estimated cost = total liters × 300 LKR.',9,True)
para('On-site current sensitivity (8 L/h per m/s) සහ base idling 2 L/h යන coefficients දත්තෙන් fit කර නැති engineering assumptions වේ. එම නිසා C2 fuel estimate එක final fuel planning එකක් නොවේ; Component 04 හි PINN model එක boat-specific estimate එකක් ලබාදුන් පසු ඒකෙන් ප්‍රතිස්ථාපනය කළ යුතුයි. Port coordinatesද approximate values වේ; obstacle-free marine route ලෙස මෙය සැලකිය නොහැක.')

heading('8. තොරතුරු සහිත ගණනයක්: පළමු Record එක')
row0=ex
T=float(row0['sst_c']);chl=float(row0['chlorophyll_a_mg_m3']);G=float(row0['sst_front_gradient_c_per_km']);V=float(row0['ocean_current_speed_ms'])
p=M['species_parameters_are_assumptions_not_established_thresholds']['yellowfin']; rt=math.exp(-.5*((T-p['temperature_optimum_c'])/p['temperature_sigma_c'])**2)
rc=chl/(chl+p['food_half_saturation_mg_m3']); rf=1-math.exp(-G/.026);rv=math.exp(-.5*((V-.22)/.23)**2)
w=p['score_weights'];H=w['temp']*rt+w['food']*rc+w['front']*rf+w['current']*rv
para(f"Record {row0['record_id']} ({row0['date_utc']}, {row0['zone_id']}) : T={T:.5f} °C, CHL={chl:.6f} mg/m³, G={G:.6f} °C/km, V={V:.6f} m/s.")
para(f'Yellowfin temperature response R_T={rt:.5f}; food response R_CHL={rc:.5f}; front response R_F={rf:.5f}; current response R_V={rv:.5f}.')
para(f'H = 0.42({rt:.5f}) + 0.33({rc:.5f}) + 0.17({rf:.5f}) + 0.08({rv:.5f}) = {H:.5f}. CSV H={float(row0["yft_habitat_suitability_index"]):.5f} (rounding නිසා සුළු වෙනසක් තිබිය හැක).')
para(f"Galle distance={float(row0['galle_great_circle_km']):.3f} km; factor-adjusted route={float(row0['galle_estimated_oneway_route_km']):.3f} km; roundtrip={float(row0['galle_roundtrip_km']):.3f} km; transit fuel={float(row0['galle_scenario_transit_fuel_l']):.3f} L; site fuel={float(row0['galle_scenario_site_fuel_l']):.3f} L; total scenario fuel={float(row0['galle_scenario_fuel_l']):.3f} L; estimated cost=Rs. {float(row0['galle_scenario_fuel_cost_lkr']):,.2f}.")

heading('9. Pareto Multi-Objective Optimization')
para('තෝරාගන්නා කලාප z සඳහා අරමුණු තුනක් නිරූපණය කර ඇත: (i) habitat suitability H(z) වැඩි කිරීම, (ii) one-way travel distance d(z) අවම කිරීම, (iii) estimated fuel cost C(z) අවම කිරීම. මෙහි H යනු සැබෑ catch probability නොව proxy index එකකි.')
para('Zone B එක Zone A එක dominate කරන්නේ H_B ≥ H_A, d_B ≤ d_A, C_B ≤ C_A සහ මේ තුනෙන් එකක් වත් strict improvement පෙන්වන අවස්ථාවක පමණි. Dominated නොවන zones එකතුව Pareto frontier එකයි. Dataset package එකේ දින 2025-02-19 සඳහා species 2 × illustrative ports 3 යන අවස්ථා 6ට, non-dominated sets හඳුනාගෙන වෙනම CSV එකක් ඇත.')
para('Fuel cost එකට site-activity terms එකතු කර ඇති නිසා distance සහ cost අරමුණු නිවැරදිව එකම linear function එකක් නොවේ. නමුත් එහි coefficients උපකල්පිත නිසා තෙවන අරමුණේ සැබෑ භෞතික විවිධත්වය සනාථ කිරීමට C4 fuel model එක සමඟ real-vessel calibration අවශ්‍යයි. Pareto frontier එකෙන් එකම “best zone” එකක් නියත නොවේ; decision-maker ගේ priorities අනුව තෝරාගත යුතුයි. [7]')
para('වැදගත් සීමාව: C1 safety gate, maritime boundaries සහ C4 fuel sufficiency ගණනය කර නොමැති අවස්ථාවල මෙම Pareto results ක්‍රියාත්මක කළ හැකි navigation waypoints ලෙස පෙන්විය නොහැක.')

heading('10. ST-GCN + Spatial Attention සඳහා Input / Target')
para('Source arrays: දින 50 × zones 100 × features 5. Features = [SST, Chlorophyll-a, current_u, current_v, SST-front strength]. 7-day history මඟින් ඊළඟ දිනයේ yellowfin සහ skipjack habitat index දෙක predict කරන supervised proxy target සකස් කර ඇත.')
para('X shape = (43 windows, 7 days, 100 nodes, 5 input features). y shape = (43, 100, 2 species). Adjacency shape = (100, 100), graph edges = 360 directed neighbour links + tensor adjacency තුළ self-loops. Spatial Attention ක්‍රමය model architecture අදියරේදී nodes අතර relative importance ඉගෙනගැනීමට භාවිත කළ හැකි අතර dataset එක මඟින් එය දැනට train කර නැහැ.')
para('Time-based split: Train = 29 target dates; Validation = 7; Test = 7. පළමු දින 7 context-only. Normalization mean/std train windows වලින් පමණක් ගණනය කරලා අනෙක් splits වලට යොදා ඇත. Test target දින training හෝ validation target දින සමඟ overlap නොවේ. පෙර දින input history එක භාවිත කිරීම forecasting සඳහා සාමාන්‍යයි.')
para('මෙහි target එක ගණනය කළේම input environmental variables වලින් නිසා test error අවම වුණත් එය සැබෑ මසුන් පුරෝකථනය කිරීමට හැකි බවට සාක්ෂියක් නොවේ. සියලු සැබෑ evaluations සඳහා independent catch logbooks / CPUE / vessel trips අවශ්‍යයි.')

heading('11. Internal Validation සහ Benchmark')
para(f"40/40 internal QA checks සමත්: Record uniqueness, exact 100×50 Cartesian grid, bidirectional edges, current divergence algebraic test, nonnegative chlorophyll/front, correct distance and fuel units, bounded indices, train-only standardization, chrono split, adjacency row sums, Pareto dominance checks සහ 0 observed catch provenance තහවුරු කිරීම ඇතුළත්ය.")
para(f"Next-day persistence benchmark එකේ simulation holdout MAE: Yellowfin = {R['baseline_metrics']['yellowfin']['persistence_baseline_test_MAE']:.5f}; Skipjack = {R['baseline_metrics']['skipjack']['persistence_baseline_test_MAE']:.5f}. මෙය generated heuristic index එක ඊළඟ දිනයේ කොතරම් smooth ද යන්නට සාක්ෂියක් පමණක් වන අතර real-world catch accuracy ලෙස වාර්තා කරන්න බැහැ.")
para('Independent QA සැලකිය යුතු දේ දෙකක්: (1) Galle route distance 35.2–125.8 km ඇස්තමේන්තු පරාසයක් ලැබී ඇත; (2) assumed fuel-cost range LKR 11,070–34,512 වේ. මේවා කිසිදු සත්‍ය ධීවරයාගේ fuel bill එකක් හෝ travel safety envelope එකක් නිරූපණය නොකරයි.')

heading('12. Research-Grade Finalization සඳහා අවශ්‍ය Empirical Validation')
bullets([
 'Copernicus Marine [1] වෙතින් 2025-01-01 සිට 2025-02-19 SST/current observations ලබාගෙන, grid coordinate/day අනුව spatial-temporal interpolation සහ missing-data flags සකස් කිරීම.',
 'Copernicus Ocean Colour [2] හෝ NASA Ocean Color [3] වෙතින් Chlorophyll-a observations ලබාගෙන cloud coverage, retrieval quality flags සහ observation gaps සුරක්ෂිත ලෙස සලකා බැලීම.',
 'ශ්‍රී ලංකාව තුළ අදාළ අවසර ඇති logbooks/cooperative data මඟින් species, weight, fishing date, gear, effort hours, location සහ zero-catch trips එකතු කිරීම. Catch Per Unit Effort (CPUE) = catch_kg / fishing_effort_hours.',
 'Species-specific coefficients මිනුම් කළ CPUE මත fit කර location/time-block CV සමඟ external tests කිරීම; unequal sampling effort, seasonality සහ fishing gear bias සලකා බැලීම.',
 'Actual calibrated catch-event probability අවශ්‍ය නම් observed catch/no-catch labels මත probabilistic model එක fit කර Brier score, reliability plot/calibration curve සහ log-loss භාවිත කිරීම.',
 'C1 safety decision gate, C4 engine-specific fuel estimate, actual harbour locations, licensed fishing areas, restricted zones, land/bathymetry masking සහ Coast Guard / fisheries constraints එක් කිරීම.',
 'Fishing sustainability: protected areas, seasonal closures, sensitive habitats සහ species stock conservation policies යටතේ recommendation feasibility filter එකක් ක්‍රියාත්මක කිරීම.'
])

heading('13. සීමාවන් සහ නිගමනය')
para('මෙම 5,000-record version එක dataset schema, graph creation, ST-GCN pipeline, reproducible data generation, Pareto optimization සහ mathematics QA සඳහා සම්පූර්ණ synthetic prototype package එකකි. එය satellite-grounded empirical research dataset එකක් ලෙස “finalized” නොවේ. ව්‍යාජ catch probabilities හෝ observations ලෙස භාවිත කළහොත් පර්යේෂණයේ විශ්වාසනීයත්වයට හානි වේ.')
para('එසේ වුවත් physics-constrained synthetic currents, positivity-preserving pigment field, biological response proxies, transparent operational scenarios සහ explicit provenance fields මඟින් later empirical data replacement එක පහසු කර ඇත. Research Panel එකට synthetic සහ observational සාක්ෂි වෙන වෙනම පෙන්වීම, සත්‍ය Accuracy එක පිළිබඳ ඉක්මන් ප්‍රකාශයකට වඩා විද්‍යාත්මකව නිවැරදියි.')

heading('14. References / මූලාශ්‍ර (සත්‍යයෙන් පරීක්ෂා කළ)',1)
refs=[
 '[1] Copernicus Marine Service. Global Ocean Physics Analysis and Forecast (GLOBAL_ANALYSISFORECAST_PHY_001_024). https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description',
 '[2] Copernicus Marine Service. Global Ocean Colour (L4) product, daily satellite chlorophyll. https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/services',
 '[3] NASA GSFC. MODIS Chlorophyll-a Concentration, algorithms and units. https://modis.gsfc.nasa.gov/data/dataprod/chlor_a.php',
 '[4] NOAA Fisheries. Pacific Yellowfin Tuna: species and habitat background. https://www.fisheries.noaa.gov/species/pacific-yellowfin-tuna',
 '[5] FAO. Resources, Fishing and Biology of the Tropical Tunas of the Eastern Central Atlantic: Skipjack biology / SST ranges. https://www.fao.org/4/t0081e/T0081E18.htm',
 '[6] Multiple ocean parameter-based potential fishing zone (PFZ) location generation and validation in the Western Bay of Bengal (2023). https://pubmed.ncbi.nlm.nih.gov/38153544/',
 '[7] Deb, K. et al. (2002). A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II. IEEE Trans. Evol. Comput. https://doi.org/10.1109/4235.996017',
 '[8] International Hydrographic Organization. Nautical Miles (definition: 1,852 metres). https://registry.iho.int/fdd/view5.do?idx=824&type=5&valueType=0',
 '[9] NOAA Fisheries. Atlantic Skipjack Tuna: pelagic habitat and upwelling information. https://www.fisheries.noaa.gov/species/atlantic-skipjack-tuna',
 '[10] Client-supplied research scope. AI-Driven Offline-First Safety and Rescue System for Artisanal Fishing Vessels (6-page proposal document). Unpublished.'
]
for ref in refs:para(ref,7.9,space_after=4)
para('මෙම reference list එක සංකල්ප, මූලාශ්‍ර සහ scientific background සඳහායි. CSV සඳහා ප්‍රායෝගික observational input data source ලෙස සලකන්න එපා.',8,True,(157,57,57))

out=P/'C2_Dataset_Justification_Sinhala.docx';doc.save(out)
print('DOCX',out,'bytes',out.stat().st_size)
