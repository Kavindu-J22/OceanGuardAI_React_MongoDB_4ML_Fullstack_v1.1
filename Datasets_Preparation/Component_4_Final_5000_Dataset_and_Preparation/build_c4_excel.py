"""Professional viewing workbook for C4; the 64-column authoritative data is CSV."""
import csv,statistics
from pathlib import Path
from artifact_tool import Workbook,SpreadsheetFile
P=Path(__file__).resolve().parent
with open(P/'C4_Master_5000_Trip_Scenarios.csv',encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
with open(P/'C4_Synthetic_Engine_Registry_250.csv',encoding='utf-8-sig',newline='') as f:engines=list(csv.DictReader(f))
with open(P/'C4_Data_Dictionary.csv',encoding='utf-8-sig',newline='') as f: dictionary=list(csv.DictReader(f))
selected=['scenario_id','c1_trip_id','vessel_id','vessel_type','c1_zone_id','c2_spatial_nearest_zone_id','displacement_mass_kg','payload_mass_kg','vessel_length_m','vessel_beam_m','loaded_draft_m_approx','engine_rated_hp_assumed','engine_age_years_assumed','propulsive_efficiency_assumed','forecast_wave_hs_m_c1_synthetic','forecast_wind_speed_ms_c1_synthetic','planned_duration_h_c1','travel_roundtrip_distance_km_scenario','outbound_speed_kn_model','inbound_speed_kn_model','outbound_brake_power_kw','inbound_brake_power_kw','transit_fuel_l_model','fishing_fuel_l_model','fuel_consumption_l_model','sensitivity_low_l_scenario','sensitivity_high_l_scenario','dataset_split_vessel_group','fuel_target_provenance','operational_use']

def conv(x):
 if x=='':return ''
 try:return float(x) if ('.' in x or x.startswith('-') or x.isdecimal()) and not (len(x)>1 and x.startswith('0') and x[1].isdigit() and '.' not in x) else x
 except:return x

w=Workbook.create();summary=w.worksheets.add('Summary');sheet=w.worksheets.add('Trip_Viewer_5000');ereg=w.worksheets.add('Engines_250');dd=w.worksheets.add('Data_Dictionary');sources=w.worksheets.add('Sources')
summary.get_range('A1:H1').merge();summary.get_range('A1').values=[['COMPONENT 04  |  RESEARCH-ONLY DATASET']]
summary.get_range('A2:H2').merge();summary.get_range('A2').values=[['Physics-constrained synthetic research scenarios • Not calibrated for vessel operations']]
summary.get_range('A4:B9').values=[['DATASET OVERVIEW','VALUE'],['Trip scenarios',len(rows)],['Outward/return legs',len(rows)*2],['Unique vessel profiles',len(set(x['vessel_id'] for x in rows))],['Independent internal checks',44],['Measured fuel observations',0]]
summary.get_range('A11:C14').values=[['VESSEL TYPE','RECORDS','MEDIAN MODEL FUEL (L)']]+[[type_,len([x for x in rows if x['vessel_type']==type_]),round(statistics.median(float(x['fuel_consumption_l_model']) for x in rows if x['vessel_type']==type_),2)] for type_ in ['OFRP','IDAY','IMUL']]
summary.get_range('A16:H16').merge();summary.get_range('A16').values=[['DATA QUALITY / INTERPRETATION']]
for i,s in enumerate(['No observed fuel-meter data are included; all fuel labels are simulator outputs.','C1 trip_id/vessel_id links are exact; C2 grid zone is only nearest spatial location.','Science QA means formula and data consistency, NOT real-world accuracy.','Reserve and available-fuel fields are illustrative numbers, NOT operating advice.','The .npz is model-ready input data; it is NOT a trained PINN.','For all 64 columns, refer to the C4_Master_5000_Trip_Scenarios.csv file.'],start=17):
 summary.get_range(f'A{i}:H{i}').merge();summary.get_range(f'A{i}').values=[[s]]
# Full 5000 rows in compact 30-column selection
sheet.get_range_by_indexes(0,0,1,len(selected)).values=[selected]
chunk=500
for start in range(0,len(rows),chunk):
 part=rows[start:start+chunk];matrix=[[conv(x[k]) if k not in ['scenario_id','c1_trip_id','vessel_id','vessel_type','c1_zone_id','c2_spatial_nearest_zone_id','dataset_split_vessel_group','fuel_target_provenance','operational_use'] else x[k] for k in selected] for x in part]
 sheet.get_range_by_indexes(start+1,0,len(matrix),len(selected)).values=matrix
eng_k=list(engines[0]);ereg.get_range_by_indexes(0,0,1,len(eng_k)).values=[eng_k]
ereg.get_range_by_indexes(1,0,len(engines),len(eng_k)).values=[[conv(x[k]) if k not in ['vessel_id','vessel_type','data_origin'] else x[k] for k in eng_k] for x in engines]
dd_k=list(dictionary[0]);dd.get_range('A1:D1').values=[dd_k];dd.get_range_by_indexes(1,0,len(dictionary),len(dd_k)).values=[[x[k] for k in dd_k] for x in dictionary]
refs=[['REFERENCE','SOURCE URL'],['ITTC-57 correlation line','https://ittc.info/media/5516/03.pdf'],['FAO Fisherman workbook','https://www.fao.org/4/ah827e/AH827E06.htm'],['NOAA buoy wave characteristics','https://www.ndbc.noaa.gov/faq/wavecalc.shtml'],['FAO/ILO/IMO vessel safety','https://www.fao.org/4/i3108e/i3108e00.htm'],['Sri Lanka fishing vessel statistics','https://www.fisheries.gov.lk/web/images/statistics/annual_report/Fisheries_Statistics_-2024-min.pdf'],['Copernicus wave reanalysis','https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_WAV_001_032/description']]
sources.get_range('A1:B7').values=refs
# Restrained professional styling
navy='#102F47';pale='#DFEFEA';white='#FFFFFF'
for sh,head_range in [(summary,'A1:H1'),(sheet,'A1:AD1'),(ereg,f'A1:{chr(64+len(eng_k))}1'),(dd,'A1:D1'),(sources,'A1:B1')]:
 sh.get_range(head_range).format={'fill':navy,'font':{'color':white,'bold':True},'row_height':31,'wrap_text':True,'vertical_alignment':'center'}
sh=summary
sh.get_range('A4:B4').format={'fill':pale,'font':{'bold':True},'row_height':24}
sh.get_range('A11:C11').format={'fill':pale,'font':{'bold':True},'row_height':24}
sh.get_range('A16:H16').format={'fill':navy,'font':{'color':white,'bold':True}}
sh.get_range('A1:H22').format.column_width=16
sh.get_range('A1:A22').format.column_width=31
sh.get_range('C11:C14').format.column_width=25
sh.get_range('A2:H2').format.row_height=28
sheet.get_range('A1:AD1').format.row_height=42
sheet.freeze_panes.freeze_rows(1)
sheet.get_range('A:A').format.column_width=17
sheet.get_range('B:D').format.column_width=16
sheet.get_range('E:AD').format.column_width=19
for sh in [ereg,dd,sources]:sh.freeze_panes.freeze_rows(1)
ereg.get_range('A:N').format.column_width=17
dd.get_range('A:A').format.column_width=40;dd.get_range('B:B').format.column_width=12;dd.get_range('C:C').format.column_width=35;dd.get_range('D:D').format.column_width=46
sources.get_range('A:A').format.column_width=33;sources.get_range('B:B').format.column_width=68
# chart data are clean categorical aggregates and refer to real cells
try:
 chart=summary.charts.add('column',summary.get_range('A11:C14'))
 chart.title_text='Simulated median fuel by vessel type'
 chart.set_position('E5','L14')
except Exception as exc:print('Non-essential chart omitted:',str(exc)[:140])
output=P/'C4_Dataset_Excel_Viewer.xlsx';SpreadsheetFile.export_xlsx(w).save(str(output))
print('EXPORTED',output,output.stat().st_size)
try:
 inspection=w.inspect({'kind':'table','range':'Summary!A1:C14','include':'values,formulas','table_max_rows':14,'table_max_cols':3})
 print('INSPECTION',inspection.ndjson[:1500])
except Exception as err:print('VIEW INSPECTION UNAVAILABLE',err)
