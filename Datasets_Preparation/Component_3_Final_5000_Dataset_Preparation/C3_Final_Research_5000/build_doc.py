from __future__ import annotations
import csv,math,json
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches,Pt,RGBColor,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent

def load(name):
 with (ROOT/name).open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
M=load('C3_Master_5000_Daily_Market_Prices.csv'); S=load('C3_Lot_Decision_Scenarios_1250.csv'); O=load('C3_Option_Economics_5000.csv'); T=load('C3_Option_Temperature_20000_Segments.csv'); PARAM=load('C3_Species_Assumptions.csv')
# Figures: explicitly SIMULATED
prices=defaultdict(list)
for r in M: prices[(r['species_id'],r['calendar_day_index'])].append(float(r['price_lkr_per_kg']))
fig,ax=plt.subplots(figsize=(10.5,4.3))
for sid,label in [('SP_SKIPJACK','Skipjack'),('SP_YELLOWFIN','Yellowfin'),('SP_MACKEREL','Indian mackerel'),('SP_SARDINE','Sardine (generic)'),('SP_SEER','Seer fish')]:
 y=[np.mean(prices[(sid,str(d))]) for d in range(200)]
 ax.plot(range(200),y,label=label,linewidth=1.45,alpha=.85)
ax.set_title('SYNTHETIC DAILY MARKET PRICE SERIES — NOT OFFICIAL OBSERVATIONS',fontsize=10,weight='bold')
ax.set(xlabel='Day since 2025-01-01',ylabel='Mean simulated price (LKR/kg)')
ax.grid(alpha=.15);ax.legend(ncol=3,fontsize=8,loc='upper right');fig.tight_layout();fig.savefig(ROOT/'C3_Synthetic_Price_Trends.png',dpi=160);plt.close(fig)

fig,ax=plt.subplots(figsize=(9.8,3.75))
for p in PARAM[:3]:
 ea=float(p['Arrhenius_Ea_j_per_mol_assumption']); tr=np.linspace(0,14,100)
 rr=np.exp(-ea/8.314462618*(1/(tr+273.15)-1/273.15))
 ax.plot(tr,rr,label=p['common_name'],linewidth=2)
ax.set_title('ASSUMED ARRHENIUS SPOILAGE RATE MULTIPLIER (0 °C BASELINE)',fontsize=10,weight='bold')
ax.set(xlabel='Fish temperature (°C)',ylabel='k(T) / k(0 °C)');ax.grid(alpha=.17);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'C3_Simulated_Temperature_Rate.png',dpi=160);plt.close(fig)

counts=Counter(s['recommended_action_proxy'] for s in S)
fig,ax=plt.subplots(figsize=(8.7,3.5));names=['SELL_NOW','WAIT_24H','TRANSPORT_NOW'];vals=[counts.get(i,0) for i in names]
rect=ax.bar(names,vals);ax.bar_label(rect,padding=3);ax.set_ylim(0,max(vals)*1.15);ax.set_ylabel('Synthetic decision scenarios (count)');ax.set_title('PROXY ECONOMIC DECISIONS — NOT SAFE-TO-SELL RECOMMENDATIONS',fontsize=10,weight='bold');fig.tight_layout();fig.savefig(ROOT/'C3_Synthetic_Recommendation_Distribution.png',dpi=160);plt.close(fig)

doc=Document(); sec=doc.sections[0];sec.page_height=Cm(29.7);sec.page_width=Cm(21.0);sec.top_margin=Cm(2.0);sec.bottom_margin=Cm(1.8);sec.left_margin=Cm(2.15);sec.right_margin=Cm(2.1)
NAVY=RGBColor(16,42,64);TEAL=RGBColor(2,111,110);SLATE=RGBColor(75,89,105)
styles=doc.styles
normal=styles['Normal'];normal.font.name='Noto Sans Sinhala';normal.font.size=Pt(9.2);normal.font.color.rgb=NAVY
normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.17
for key,size,bold,spaceb in [('Title',19,True,0),('Subtitle',10,False,0),('Heading 1',13.5,True,11),('Heading 2',10.8,True,8),('Heading 3',9.5,True,6)]:
 st=styles[key];st.font.name='Noto Sans Sinhala';st.font.size=Pt(size);st.font.bold=bold;st.font.color.rgb=(TEAL if key.startswith('Heading') else NAVY)
 st.paragraph_format.space_before=Pt(spaceb);st.paragraph_format.space_after=Pt(5)
for key in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
 st=styles[key];st._element.rPr.rFonts.set(qn('w:eastAsia'),'Noto Sans Sinhala');st._element.rPr.rFonts.set(qn('w:cs'),'Noto Sans Sinhala')
header=sec.header.paragraphs[0]
header.text='C3  |  AI-Driven Fish Value Forecasting  |  Research Data Justification'
header.style='Caption';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
for r in header.runs:r.font.size=Pt(7.2);r.font.color.rgb=SLATE
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fr=footer.add_run('SYNTHETIC RESEARCH DATA  •  නොසනාථ කළ prototype  |  2026 ඔක්තෝබර් 16  |  පිටුව ');fr.font.size=Pt(7.5)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

def para(text='',style=None):return doc.add_paragraph(text,style=style)
def heading(title,level=1):return doc.add_heading(title,level=level)
def bullet(text):return doc.add_paragraph(text,style='List Bullet')
def numbered(text):return doc.add_paragraph(text,style='List Number')
def table(headers,rows,widths=None):
 tb=doc.add_table(rows=1, cols=len(headers));tb.style='Light Shading Accent 1';tb.alignment=WD_TABLE_ALIGNMENT.CENTER
 for i,txt in enumerate(headers):tb.rows[0].cells[i].text=str(txt)
 for row in rows:
  cellrow=tb.add_row().cells
  for i,val in enumerate(row):cellrow[i].text=str(val)
 for tr in tb.rows:
  for cell in tr.cells:
   cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(2)
    for r in p.runs:
     r.font.name='Noto Sans Sinhala';r.font.size=Pt(8.0)
  trpr=tr._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
 if widths:
  for row in tb.rows:
   for i,w in enumerate(widths):row.cells[i].width=Cm(w)
 doc.add_paragraph('')
 return tb

def formula(tex):
 p=doc.add_paragraph();p.paragraph_format.left_indent=Cm(.65);p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(7)
 r=p.add_run(tex);r.font.name='DejaVu Sans Mono';r.font.size=Pt(8.2);r.font.color.rgb=TEAL

def fig(name,caption,width=15.2):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(ROOT/name),width=Cm(width))
 pp=doc.add_paragraph(caption);pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
 for r in pp.runs:r.italic=True;r.font.size=Pt(8);r.font.color.rgb=SLATE

def block_note(text):
 p=doc.add_paragraph();p.paragraph_format.left_indent=Cm(.4);p.paragraph_format.right_indent=Cm(.3)
 r=p.add_run('විශේෂ සටහන  |  '+text);r.bold=True;r.font.color.rgb=RGBColor(153,68,11)

# TITLE
p=doc.add_paragraph();p.style='Title';p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('C3 – අවසන් පර්යේෂණ Dataset එක සඳහා\nවිද්‍යාත්මක හා ගණිතමය සාධාරණීකරණය')
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('AI-Driven Perishability-Aware Fish Value Forecasting & Market Decision System').bold=True
p=doc.add_paragraph('ශ්‍රී ලංකා කුඩා ධීවර යාත්‍රා සඳහා Offline-First Safety and Rescue Research System | සංරචකය 03');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph('සංස්කරණය 1.0  •  2026-10-16  •  සිංහල විස්තර + English technical terminology');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
block_note('මෙහි දත්ත 5,000ම simulated (synthetic) වේ. ශ්‍රී ලංකාවේ සත්‍ය වෙළෙඳපොළ මිල, සැබෑ මත්ස්‍ය නියැදි හෝ විද්‍යාගාරයෙන් මිනුම් කළ freshness data නොවේ. “Finalized” යන්නෙන් මෙහි අදහස් වන්නේ සංවර්ධනයට සුදුසු audit කළ research prototype dataset එකයි.')
heading('ක්‍රියාකාරී සාරාංශය',1)
para('මෙම වාර්තාව C3 පද්ධතිය සඳහා දිනය–වෙළෙඳපොළ–මත්ස්‍ය වර්ගය මට්ටමේ 5,000ක price time-series dataset එකක්, එයට සම්බන්ධ 1,250 fish-lot decision scenarios, විකල්ප 5,000ක්, සහ time–temperature segments 20,000ක් ජනනය කරන පර්යේෂණ ක්‍රමවේදය පැහැදිලි කරයි. Price forecasting සඳහා Temporal Fusion Transformer (TFT) භාවිත කළ හැකි පරිදි 28-day encoder හා 7-day prediction windowsද ලබා දී ඇත.')

heading('1. Research problem, targets සහ වැදගත් වෙන්කිරීම්',1)
bullet('Price Forecasting: විවිධ මත්ස්‍ය වර්ගවල දිනපතා වෙළෙඳපොළ LKR/kg මිල පුරෝකථනය.')
bullet('Perishability Proxy: මසුන්ගේ උෂ්ණත්ව ඉතිහාසයෙන් ගුණාත්මකභාවය අඩුවීමේ අනුමානිත index එක ගණනය කිරීම.')
bullet('Decision Support: Sell Now / Wait 24 Hours / Transport Now යන විකල්ප අතර පිරිවැය ඉවත් කළ අපේක්ෂිත ආදායම සංසන්දනය.')
bullet('External Validity: සැබෑ price, catch, temperature-logger, fish inspection සහ sales receipt දත්ත භාවිතයෙන් පසුව තහවුරු කිරීම අත්‍යවශ්‍යයි.')
block_note('Freshness Proxy ≠ ආහාර ආරක්ෂාව. Tuna / mackerel වර්ගවල histamine hazard උෂ්ණත්ව index එකකින් ඉවත් කළ නොහැක. “WAIT” වැනි ප්‍රතිඵල වාණිජ simulation එකක් පමණි; ආහාර පරීක්ෂාවකින් තොරව විකිණීමට/භාවිතයට නිර්දේශයක් නොවේ. [S2]')

heading('2. Dataset ව්‍යුහය, record unit සහ scope',1)
table(['ගොනුව','ප්‍රමාණය','මූලික කාර්යය'],[
 ['C3_Master_5000_Daily_Market_Prices.csv','5,000 rows','5 markets × 5 species × 200 consecutive days; TFT target price'],
 ['C3_Lot_Decision_Scenarios_1250.csv','1,250 rows','එකම fish lot එකට අදාළ economic decision'],
 ['C3_Option_Economics_5000.csv','5,000 rows','එක් lot එකකට විකල්ප 4ක්; net-return calculation'],
 ['C3_Option_Temperature_20000_Segments.csv','20,000 rows','එක් විකල්පයක temperature/time segments 4ක්'],
 ['C3_TFT_[split]_28to7.npz','3 datasets','TFT encoder, future-known, 7-day price target'],
 ['C3_Species_Assumptions.csv','5 rows','අනුමානිත price හා fish-quality kinetic parameters'],
 ['C3_Full_Data_Dictionary.csv','සම්පූර්ණ schema','Column meanings, units, feature roles, provenance'],
])
para('කාල පරාසය: 2025 ජනවාරි 1 සිට 2025 ජූලි 19 දක්වා (දින 200). වෙළෙඳපොළ: Peliyagoda, Negombo, Galle, Mirissa, Tangalle යන නාමිත scenario locations. Species: Skipjack, Yellowfin, Indian mackerel, generic sardine, generic seer fish. මෙම වෙළෙඳපොළ names පමණක් geographical context ය; කිසිම row එකක් සත්‍ය ලංසු/මිලක් නොවේ.')
para('Time-series එකේ ඒකකය: එක් දිනයක, එක් වෙළෙඳපොළක, එක් species එකකට එක් price row එකක්. එක් species×market එකකට consecutive observations 200ක් තිබීම sequence learning සඳහා වැදගත් වේ. අනෙක් decision dataset වල fish lot එකක් යනු වෙනම simulation entity එකකි.')
heading('3. තොරතුරු මූලාශ්‍ර සහ evidence classification',1)
table(['මූලාශ්‍රය','ඇත්තෙන්ම සහය දක්වන කොටස','Dataset provenance'],[
 ['FAO Huss (1995) [S1]','උෂ්ණත්වය මත deterioration හා cumulative exposure','theory only'],
 ['Codex CXC 52-2003 [S2]','chilling, time–temperature control, histamine hazards','safety guidance only'],
 ['Sri Lanka Fisheries Ministry [S3]','2025 official weekly fish price spreadsheets ලැයිස්තුව','no rows imported'],
 ['HARTI [S4]','market commodity price bulletins සොයාගත හැකි මූලාශ්‍රය','no rows imported'],
 ['Fish Freshness Modelling Review [S5]','Arrhenius-based model context සහ limitations','theory only'],
 ['Lim et al. (2021) [S6]','Temporal Fusion Transformer architecture','methodology only'],
 ['Food-quality modelling [S7]','Arrhenius form and Ea discussion','theory only']
])
para('2025 නිල fish price ගොනු වෙබ් අඩවියේ සොයාගත හැකි වුණත් එහි workbook bytes මෙම අවස්ථාවේ ලබාගැනීම අසාර්ථක විය. ඒ නිසා කිසිම synthetic price එකක් නිල මිලක් ලෙස හඳුන්වා නැත. පර්යේෂණයේ real-data stage එකේදී සතිපතා official observations හඳුනාගෙන market/species/unit mapping සමඟ import කළ යුතුය. Weekly මිල daily observation 7ක් බවට copy කිරීමෙන් ස්වාධීන daily measurements බිහි නොවේ.')

heading('4. වෙළෙඳපොළ මිල ජනනය කිරීමේ structural proxy model',1)
para('Target: P(m,s,t) [LKR/kg]. Market–species time series generation එකට ධනාත්මක base price, market multiplier, දෛනික demand proxy, supply ratio, සහ autocorrelated market-shock index යොදාගනී. මෙය supply–demand යාන්ත්‍රණයක් නිරූපණය කරන synthetic function එකකි; ආර්ථික විද්‍යාවේ දත්තවලින් fit කළ elasticity estimates නොවේ.')
formula('P = B_species × M_market × (DemandIndex ^ 0.48) × (SupplyRatio ^ -0.40) × ShockIndex')
para('B_species (LKR/kg) සහ M_market උපකල්පන; exponents 0.48, −0.40 දත්ත මත calibrate නොකළ design constants; 0.82–1.20 අතර ShockIndex එකට පරිණාමශීලී temporal noise එක ඇතුළත් වේ. SupplyRatio = simulated_supply_kg / baseline_supply_kg. ඉහළ supply එකක් ඇති විට අනෙක් දේවල් සමාන නම් මිල අඩුවන අතර demand ඉහළ යන විට මිල ඉහළ යන ලෙස functions සැකසී ඇත.')
rr=M[0]
price_calc=float(rr['base_price_assumed_lkr_kg'])*float(rr['market_multiplier_assumed'])*float(rr['demand_index_simulated'])**.48*float(rr['supply_ratio_simulated'])**(-.40)*float(rr['market_shock_index_simulated'])
para('උදාහරණය (C3M00001): Skipjack – Peliyagoda – 2025-01-01. Base = LKR '+rr['base_price_assumed_lkr_kg']+', market factor = '+rr['market_multiplier_assumed']+', demand = '+rr['demand_index_simulated']+', supply ratio = '+rr['supply_ratio_simulated']+', shock = '+rr['market_shock_index_simulated']+'.')
formula('P ≈ 740 × 1.03 × 0.8325553^0.48 × 1.1385229^-0.40 × 0.9483323 = LKR '+f'{price_calc:.2f}'+'/kg')
fig('C3_Synthetic_Price_Trends.png','රූපය 1 – 2025 synthetic daily prices; දත්ත කිසිසේත් නිල වෙළෙඳපොළ මිල නොවේ.')

heading('5. Biological deterioration: Arrhenius kinetics හා freshness proxy',1)
para('FAO (1995) සහ fish freshness modelling review හි මූලික අවබෝධය අනුව fish spoilage rate එක උෂ්ණත්වයට අතිශය සංවේදීය. මේ පර්යේෂණය Arrhenius සමානතාව භාවිත කරයි. මෙහි kref හා Ea species අනුව අනුමානිත අගයන් වේ; සත්‍ය රසායනාගාරයෙන් හෝ microbial challenge tests වලින් ලැබූ ඒවා නොවේ. [S1, S5, S7]')
formula('k(T) = k_ref × exp{ -Ea/R × [ 1/(T_C+273.15) - 1/273.15 ] }')
formula('D_total = Σ_j [ k(T_j) × Δt_j ]    ;    FreshnessProxy F = exp(−D_total)')
para('R = 8.314462618 J/(mol·K); Ea = 54–60 kJ/mol ලෙස පරාමිතිමය උපකල්පනය; reference T = 0°C; kref ≈ ln(2) / scenario_half_life_hours. D_total dimensionless cumulative deterioration dose. F (0–1) dimensionless quality proxy එකක්. F=0.9 යනු 90% sensory freshness හෝ pathogen-free බව නොපෙන්වයි. එය මෙම උපකල්පන model එකේ අගයකි.')
table(['Species','k_ref (h^-1) assumed','Ea (kJ/mol) assumed','0°C proxy half-life (h)'],[(p['common_name'],p['k_ref_per_h_assumption'],float(p['Arrhenius_Ea_j_per_mol_assumption'])/1000,p['quality_proxy_half_life_h_at_0c_assumption']) for p in PARAM])
fig('C3_Simulated_Temperature_Rate.png','රූපය 2 – උෂ්ණත්වය වැඩි වන විට proxy quality-loss rate වැඩිවීම; species-specific verified curves නොවේ.',width=14.3)
para('කාලය මත උෂ්ණත්වය වෙනස් වෙන නිසා සෑම option එකකටම steps 4ක් තිබේ: (1) මුහුදේ රඳවාගැනීම, (2) වරායේ බලාසිටීම, (3) transport හෝ 24-hour holding, (4) විකිණීමට පෙර auction queue. කාල–උෂ්ණත්ව අනුක්‍රමය වෙනම CSV එකක තබා තිබීමෙන් dose සම්පූර්ණයෙන් යළි ගණනය කළ හැකිය.')
block_note('ෆිෂ් spoilage proxy එක ආහාරයේ histamine, microbial pathogens, toxins හෝ සත්‍ය shelf life මැනීමක් නොවේ. Codex time-temperature guidance සහ නිසි inspe​​ction හඳුන්වාදීම අත්‍යවශ්‍යයි. [S2]')

heading('6. ප්‍රවාහන physics: දුර, උෂ්ණ හුවමාරුව, ice energy',1)
para('ප්‍රවාහන දුර දක්වන්නේ භූගෝලීය Haversine great-circle approximation එක 1.34න් ගුණ කරමිනි. 1.34 මාර්ග ජාලයෙන් මිනුම් කළ calibration factor එකක් නොවේ. එය scenario road-detour multiplier එකකි; සැබෑ විධාන/route planning සඳහා භාවිත නොකළ යුතුය.')
formula('d_gc = 2R_earth × asin( sqrt( sin²(Δφ/2) + cosφ1 cosφ2 sin²(Δλ/2) ) )')
formula('d_road_proxy = 1.34 × d_gc  ;  R_earth = 6371.0088 km')
para('Cold box එකට සිදුවන heat ingress එක සරල lumped UA model එකකින් ගණනය කර ice melt අවශ්‍යතාවයක් proxy ලෙස සැලකේ. මෙය engineered refrigeration design එකක් නොවේ; initial fish cool-down, evaporative/solar loads, melt-water drainage, uneven packing සහ bacterial safety requirements අඩංගු නොවේ.')
formula('Q_in [kJ] = UA [W/K] × max(T_ambient − T_storage, 0) [K] × Δt [h] × 3.6')
formula('m_ice_proxy [kg] = Q_in [kJ] / L_fusion [kJ/kg] ; L_fusion = 334 kJ/kg')
para('Assumptions: UA = 8.5 W/K; ambient = 28°C; market ice price = LKR 42/kg. 1 W·h = 3.6 kJ. Price සහ UA දෙකම සාක්ෂි සහිත measured fleet average ලෙස නොපෙන්වයි. Ice kg proxy එක නිසි ගබඩා උෂ්ණත්වයක් පවත්වාගැනීමට ප්‍රමාණවත් බවට සහතික නොවේ.')

heading('7. Decision algorithm: අවස්ථා, ආදායම් හා පිරිවැය',1)
para('එක් scenario_id යටතේ එකම fish lot එක සඳහා විකල්ප 4ක් සාදයි: SELL_NOW (එම වරායේ), WAIT_24H (එම වෙළෙඳපොළේ), TRANSPORT_NOW (සමීපම වෙනත් වෙළෙඳපොළ දෙකකට). සෑම විකල්පයකම පරස්පර වශයෙන් වෙනස් time–temperature exposure, transport expenses හා expected market price යොදයි.')
formula('QualityMultiplier = 1 − 0.22 × (1 − F)')
formula('SaleableKg = BatchKg × [ 0.98 − 0.065 × (1 − F) ]')
formula('GrossExpected = PriceEstimate × QualityMultiplier × SaleableKg')
formula('NetExpected = GrossExpected × (1 − 0.016) − (175 × RoadKm) − (42 × IceKg) − (7 × BatchKg)')
para('Quality loss price discount 22% weighting, saleable weight adjustment, 1.6% market fee, LKR 175/km transport rate සහ LKR 7/kg handling cost — මේ සියල්ල demonstration assumptions පමණි. ප්‍රායෝගිකව සත්‍ය commission rates, vehicle costs, verified spoilage losses සහ measured price discounts වලින් calibrate කළ යුතුයි.')
para('දිනකට දෙවන දිනයේ මිල තීරණ මොහොතේ නොදන්නා බැවින් WAIT_24H විකල්පය සඳහා අද දින දක්වා පමණක් ලබාගත හැකි පසුගිය දින 7ක මිලවල සරල mean එක භාවිත වේ. අනාගත next-day synthetic price එක `ex_post...` column එකේ තැබෙන්නේ retrospective evaluation සඳහා පමණි; recommendation compute කිරීමට යොදාගෙන නැත. අවශ්‍ය විට training කළ TFT tomorrow forecast එක මෙම baseline එකට ආදේශ කළ හැකිය.')
formula('RecommendedOption = argmax_options ( ExpectedNetReturn )')
formula('ExPostRegret = max_options(RealizedNetReturn) − RealizedNetReturn(RecommendedOption)')

para('මුල් Research Specification එකේ Dynamic Game-Theoretic Decision Framework එකක් යෝජනා කළත් මේ prototype data මත සැබවින්ම ක්‍රියාත්මක වන්නේ single-actor expected-net-return optimization baseline එකකි. Competing buyers, strategic bids, bargaining/payoff matrices හෝ Nash equilibrium දත්ත නැති බැවින් Game Theory novelty එක මෙතෙක් තහවුරු කර නැත. ඒ සඳහා සත්‍ය market-agent data අවශ්‍යයි.')

heading('8. සම්පූර්ණ worked example — Scenario C3S00001',1)
sc=S[0]; opts=[o for o in O if o['scenario_id']==sc['scenario_id']]; segs=[t for t in T if t['option_id']=='C3S00001O1']
para('Decision day: '+sc['decision_date']+'. Fish: '+sc['species_name']+'. Landing port: '+sc['landing_port_id']+'. Batch weight: '+sc['lot_weight_kg']+' kg. At-sea storage: '+sc['at_sea_hours']+' h at '+sc['at_sea_fish_temp_c']+'°C. Pre-decision port holding: '+sc['port_wait_hours']+' h at '+sc['port_fish_temp_c']+'°C.')
table(['විකල්පය','Price estimate (LKR/kg)','F proxy','Net expected (LKR)'],[(o['action']+' → '+o['destination_market_id'],o['decision_time_price_estimate_lkr_kg'],o['freshness_quality_proxy_0_1'],o['expected_net_return_lkr']) for o in opts])
para('SELL_NOW සඳහා පළමු steps දෙකේ damage dose ගණනය:')
for s in segs[:2]:
 formula(f"{s['segment_type']}: k={s['k_per_hour_arrhenius_assumed']} h^-1 × Δt={s['duration_h']} h → D={s['spoilage_dose_increment']}")
base=opts[0]
formula('ΣD (all 4 steps) = '+base['cold_chain_spoilage_dose']+'  ⇒  F = exp(−ΣD) = '+base['freshness_quality_proxy_0_1'])
formula('NetExpected SELL_NOW = '+base['estimated_saleable_kg']+' × '+base['decision_time_price_estimate_lkr_kg']+' × '+base['quality_discount_multiplier_assumption']+' × 0.984 − '+base['transport_cost_lkr']+' − '+base['ice_cost_lkr']+' − '+base['handling_cost_lkr']+' ≈ LKR '+base['expected_net_return_lkr'])
para('මෙම scenario එකේ highest model-estimated net return ලබාදෙන option: '+sc['scenario_best_option_id']+' ('+sc['recommended_action_proxy']+') — '+sc['recommended_market_id']+'. අමතර synthetic profit vs SELL_NOW = LKR '+sc['predicted_increment_vs_sell_now_lkr']+'. මෙය අනුමානිත demonstration result එකක් වන අතර food safety approval එකක් නොවේ.')
fig('C3_Synthetic_Recommendation_Distribution.png','රූපය 3 – 1,250 synthetic fish lots හි model-derived action counts; විකිණීමේ ආරක්ෂක උපදෙස් නොවේ.',width=13.8)

heading('9. Temporal Fusion Transformer: Model-ready preparation',1)
para('TFT (Lim et al., 2021) past observed variables, static descriptors, සහ known future covariates වෙන්කරන attention-based multi-horizon model එකකි. Price data series 25ක් (5 markets × 5 species) ඇත. Encoder දිග 28 දිනක්; forecast horizon 7 දිනක්. Price target LKR/kg; inputs: log(price), log(supply), demand-index (past observations only). Known future: sin/cos weekday, sin/cos day-of-year, weekend. Static group index එකෙන් species–market combination හඳුනාගන්න පුළුවන්. [S6]')
para('Normalisation parameters පුහුණු කාලය (2025 ජනවාරි 1 – මැයි 20 පමණ; පළමු දින 140) භාවිතයෙන් පමණක් fit කර ඇත. Val/test හි target label windows train කාලයට නොගැළපේ. කෙසේ වෙතත් val/test input encoder සඳහා පෙර දිනවල history භාවිත කිරීම අනුමත realistic forecasting practice එකකි.')
table(['Split','Target-day integer limits','No. 28→7 windows'],[['Train','0–139','2,650'],['Validation','140–169','600'],['Test','170–199','600']])
para('Boundary-crossing target windows ඉවත් කර ඇති නිසා මුළු windows 3,850ක් වේ. Models සඳහා comparison baselines: yesterday-price persistence, 7-day moving average, seasonal naïve, සහ statistical ARIMA/ETS වැනි ක්‍රම. Suggested metrics: MAE (LKR/kg), RMSE (LKR/kg), sMAPE, WAPE, quantile pinball loss; economic decision regret. Synthetic data accuracy සත්‍ය market forecasting accuracy ලෙස භාවිත කළ නොහැක.')

heading('10. Independent data integrity validation හා QA',1)
qa=json.loads((ROOT/'C3_QA_Report.json').read_text())
para('`validate_c3.py` මඟින් ස්වාධීනව නැවත ගණනය කළ checks '+str(qa['checks_passed'])+'ක් සමත් විය. මේවා structural/math/code consistency tests පමණි. FAO හෝ governmental agencies ලබාදුන් independent laboratory/market validation එකක් මෙතෙක් නොමැත.')
bullet('5,000 exact master observations, day × species × market duplicates නොමැති බව සහ dates 200ක් අඛණ්ඩව තිබීම.')
bullet('Price generation equation, market supply normalization, chronological splits සහ missing values consistency.')
bullet('Arrhenius rate, cumulative deterioration exposure, freshness quality proxy සහ temperature segments independent recalculation.')
bullet('Same lot per option, transport/ice/market fee formulas, net return, ex-post evaluation සහ future-price leakage control.')
bullet('TFT arrays, 28-day context, 7-day horizon, split boundaries සහ finite numerical data.')
block_note('63/63 QA PASS යනු දත්ත ගුණාත්මකභාවයේ ගණිතමය හා වැඩසටහන් පරීක්ෂණ ප්‍රතිඵලයයි. Model accuracy, fish safety, official price agreement, real economic profit හෝ experimental biological validity සනාථ නොකරයි.')

heading('11. ආර්ථික/ජීව විද්‍යාත්මක limitations හා real-world validation',1)
numbered('2025–2026 නිල සතිපතා fish-price reports, HARTI bulletins සහ actual landing/auction invoices ලබාගෙන wholesale-vs-retail, region, fish species සහ units harmonize කර import කරන්න. Missing days දිගුම දත්ත ලෙස සලකන්න එපා.')
numbered('Fish lot ID, landed kg, actual offer price, time-at-catch, ice loading, temperature logger series, travel receipts, auction fees සහ verified actual sale receipts එකතු කරන්න.')
numbered('Species-resolved laboratory/sensory quality scores (Quality Index Method, TVB-N වැනි indicators හා validated microbiological / histamine measurements) මඟින් Ea, kref සහ quality-to-price relation calibrate කරන්න. මෙහි සරල model එක ස්වාධීනව food-safety thresholds ඉදිරිපත් නොකරයි.')
numbered('Real geocoded route-distance, traffic delays, refrigerated-vehicle costs සහ fish-box heat-transfer coefficients වෙනුවට වර්තමාන proxy constants ආදේශ කරන්න.')
numbered('Purely synthetic training හි test accuracy හැර, unseen real calendar periods සහ unseen market/fish species පරීක්ෂා කරන්න; ablation studies සහ uncertainty bounds ඉදිරිපත් කරන්න.')
numbered('C2 datasets සමඟ fish species, trip fishing-zone සහ landing-port mapping පමණක් conceptually සම්බන්ධ කළ හැක. C2 simulated January–February 2025 zone rows සහ C1 2024 trip rows C3 වෙළෙඳපොළ rows සමඟ actual catch/lot observation ලෙස join කළ නොහැක. සැබෑ trip_id / catch_lot_id crosswalk එකක් එකතු කළ යුතුයි.')
para('ඔන්ලයින් data නොමැති “offline-first” භාවිතය සඳහා stale price indicator, last_sync timestamp, confidence interval, forecast age සහ market quote expiry handling අවශ්‍ය වේ. මසුන් විකිණීමේ තීරණය ප්‍රායෝගික ආරක්ෂක පරීක්ෂණ හෝ සෞඛ්‍ය ආයතනවල මාර්ගෝපදේශ අභිබවා නොයයි.')

heading('12. Summary / Research claim ප්‍රකාශ කරන නිවැරදි ආකාරය',1)
para('මෙම deliverable එක 5,000ක time-series market records, reproducible economic-decision simulations, physics-inspired heat duty estimation සහ Arrhenius-based fish-quality proxy එකක් එකතු කරන audit කළ synthetic system-development dataset එකකි. එය C3 implementation, pipeline debugging, temporal cross-validation practice සහ algorithm demonstrations සඳහා සුදුසුයි. නමුත් එහි price elasticity, spoilage parameters, market fees, logistics multipliers සහ synthetic decision outcomes තවම empirical අර්ථයෙන් validated නැති නිසා “real Sri Lankan market forecasts” හෝ “fish safe to sell” ලෙස presentation නොකළ යුතුය.')

heading('References | Harvard-style',1)
refs=[
 '[S1] Huss, H.H. (1995) Quality and quality changes in fresh fish. FAO Fisheries Technical Paper 348. FAO. Available at: https://www.fao.org/4/V7180E/V7180e07.htm (Accessed: 16 October 2026).',
 '[S2] Codex Alimentarius Commission (2003, updated) Code of Practice for Fish and Fishery Products, CXC 52-2003. FAO/WHO. Available at: https://www.fao.org/fao-who-codexalimentarius/ (Accessed: 16 October 2026).',
 '[S3] Ministry of Fisheries, Aquatic and Ocean Resources, Sri Lanka (2025) Weekly Fish Prices — 2025 archive. Available at: https://www.fisheries.gov.lk/?page_id=8544&paged=3 (Accessed: 16 October 2026).',
 '[S4] Hector Kobbekaduwa Agrarian Research and Training Institute (HARTI) (2025) Daily Food Commodities Bulletin archive. Available at: https://www.harti.gov.lk/daily-price.php (Accessed: 16 October 2026).',
 '[S5] Assessment and Prediction of Fish Freshness Using Mathematical Modelling: A Review (2022). Available at: https://pmc.ncbi.nlm.nih.gov/articles/PMC9368035/ (Accessed: 16 October 2026).',
 '[S6] Lim, B., Arık, S.Ö., Loeff, N. and Pfister, T. (2021) Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. International Journal of Forecasting, 37(4), pp. 1748–1764. doi:10.1016/j.ijforecast.2021.03.012.',
 '[S7] Food Science and Technology (2018) Modelling food quality. Oxford Academic. Available at: https://academic.oup.com/fst/article/32/1/38/7818609 (Accessed: 16 October 2026).',
 '[S8] Giannakourou, M.C. and Taoukis, P.S. (1999) Use of time–temperature integrators and predictive modelling for shelf life control of chilled fish under dynamic storage conditions. International Journal of Food Microbiology, 53(1), pp. 21–31. doi:10.1016/S0168-1605(99)00142-7.'
]
for txt in refs:
 p=doc.add_paragraph(txt);p.paragraph_format.left_indent=Cm(.4);p.paragraph_format.first_line_indent=Cm(-.4)
 for r in p.runs:r.font.size=Pt(8)

heading('Appendix A. Reproducibility සහ ගොනු භාවිතය',1)
para('Seed: 20261016. Main generation: `python build_c3.py` (ඕනෑම reproducible Python environment එකක numpy අවශ්‍ය වේ). Independent checks: `python validate_c3.py`. Results: `C3_Manifest.json` හා `C3_QA_Report.json`. Main time series වෙනම තබා ඇති අතර scenario optimization files TFT input data ලෙස හදිසියේ merge නොකරන්න. Sources file එකේ `observational_rows_imported = 0` නිසා data lineage නිවැරදිව විස්තර කළ හැක.')

out=ROOT/'C3_Dataset_Justification_Sinhala.docx';doc.save(out)
print('CREATED',out,'size',out.stat().st_size)
