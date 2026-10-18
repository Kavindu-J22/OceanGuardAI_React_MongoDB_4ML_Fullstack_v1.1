import csv
from pathlib import Path
from collections import defaultdict
from artifact_tool import Workbook, SpreadsheetFile
ROOT=Path(__file__).resolve().parent

def read(fn):
 with (ROOT/fn).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
master=read('C3_Master_5000_Daily_Market_Prices.csv')
decs=read('C3_Lot_Decision_Scenarios_1250.csv')
species=read('C3_Species_Assumptions.csv')
sources=read('C3_Source_Provenance.csv')
wb=Workbook.create()
readme=wb.worksheets.add('START_HERE')
readme.get_range('A1:H2').merge_cells() if False else None
readme.merge_cells('A1:H2')
readme.get_range('A1').values=[['C3 · FINALIZED SYNTHETIC RESEARCH DATASET | 5,000 DAILY MARKET RECORDS']]
readme.get_range('A1:H2').format={'fill':'#12394C','font':{'bold':True,'color':'#FFFFFF','size':15},'vertical_alignment':'center','row_height':24}
notes=[
 ['DATA PROVENANCE','All values are SYNTHETIC. Not imported from the government or measured in any market.'],
 ['MASTER RECORD COUNT','5,000 = 5 markets × 5 fish categories × 200 consecutive calendar dates.'],
 ['DATE COVERAGE','2025-01-01 to 2025-07-19 inclusive.'],
 ['MARKET INPUTS','Structural demand/supply proxy; price exponent constants are research assumptions.'],
 ['DECISION SCENARIOS','1,250 synthetic lots with independent cost and biological exposure assumptions.'],
 ['BIOLOGICAL MODEL','Arrhenius quality proxy is uncalibrated; NOT a food safety or histamine test.'],
 ['MODEL TRAINING','TFT 28-day history -> 7-day targets. Training windows are in companion .npz files.'],
 ['QA','63 mathematical/data-integrity checks PASS; zero real-world validation performed.'],
 ['SOURCES','See SOURCES sheet and the Sinhala Word report; no observational rows imported.'],
 ['DISCLAIMER','Do not use to advise selling or consuming fish without verified safety inspection.'],
]
readme.get_range('A4:B13').values=notes
readme.get_range('A4:A13').format={'fill':'#D7E9E8','font':{'bold':True,'color':'#174750'},'column_width':27}
readme.get_range('B4:B13').format={'column_width':96,'wrap_text':True,'row_height':32}
readme.get_range('A4:B13').format.row_height=34

numkeys={'calendar_day_index','day_of_week_mon0','weekend_known_future','month_known_future','base_price_assumed_lkr_kg','market_multiplier_assumed','supply_kg_simulated','baseline_supply_kg_assumed','supply_ratio_simulated','demand_index_simulated','market_shock_index_simulated','price_lkr_per_kg','lot_weight_kg','at_sea_hours','at_sea_fish_temp_c','port_wait_hours','port_fish_temp_c','predicted_best_net_return_lkr','predicted_sell_now_baseline_lkr','predicted_increment_vs_sell_now_lkr','ex_post_actual_net_for_selected_lkr','ex_post_regret_lkr_FOR_EVALUATION_ONLY'}
def writedata(title,rows):
 sh=wb.worksheets.add(title)
 headers=list(rows[0]);data=[headers]
 for r in rows:
  data.append([float(r[h]) if h in numkeys and r[h]!='' else r[h] for h in headers])
 sh.get_range_by_indexes(0,0,len(data),len(headers)).values=data
 sh.get_range_by_indexes(0,0,1,len(headers)).format={'fill':'#0F766E','font':{'bold':True,'color':'#FFFFFF','size':10},'row_height':28,'wrap_text':True}
 sh.get_range_by_indexes(0,0,len(data),1).format.column_width=18
 # controlled widths for text data (avoid 5000x costly cell formatting)
 for j,h in enumerate(headers):
  if j==0:continue
  sh.get_range_by_indexes(0,j,1,1).format.column_width=(24 if ('name' in h or 'provenance' in h or 'status' in h) else 16)
 sh.freeze_panes.freeze_rows(1)
 return sh
writedata('MARKET_5000',master)
writedata('DECISIONS_1250',decs)
writedata('SPECIES_PARAMETERS',species)
src=wb.worksheets.add('SOURCES')
headers=list(sources[0]);src.get_range_by_indexes(0,0,len(sources)+1,len(headers)).values=[headers]+[[int(x[h]) if h=='observational_rows_imported' else x[h] for h in headers] for x in sources]
src.get_range_by_indexes(0,0,1,len(headers)).format={'fill':'#0F766E','font':{'bold':True,'color':'#FFFFFF'},'row_height':26}
src.get_range('A1:A9').format.column_width=12
src.get_range('B1:B9').format.column_width=52
src.get_range('C1:C9').format.column_width=85
src.get_range('D1:D9').format.column_width=67
src.get_range('E1:E9').format.column_width=20

series=defaultdict(list)
for r in master:series[(r['date'],r['species_id'])].append(float(r['price_lkr_per_kg']))
trend=wb.worksheets.add('SYNTHETIC_PRICE_TRENDS')
market_sids=['SP_SKIPJACK','SP_YELLOWFIN','SP_MACKEREL','SP_SARDINE','SP_SEER']
rows=[['DATE']+market_sids]
for dd in sorted({r['date'] for r in master}):
 rows.append([dd]+[round(sum(series[(dd,sid)])/5,2) for sid in market_sids])
trend.get_range('A1:F201').values=rows
trend.get_range('A1:F1').format={'fill':'#0F766E','font':{'bold':True,'color':'#FFFFFF'},'row_height':26}
trend.get_range('A1:A201').format.column_width=18
trend.get_range('B1:F201').format.column_width=18
trend.freeze_panes.freeze_rows(1)
# Chart optional; create after rows are stored
try:
 ch=trend.charts.add('line',trend.get_range('A1:F201'))
 ch.title_text='Simulated Mean Prices by Species (LKR/kg) — Not observed'
 ch.has_legend=True
 ch.legend.position='bottom'
 ch.set_position('H3','S20')
except Exception as exc:
 print('Chart skipped due to renderer limitations:',str(exc)[:160])
out=ROOT/'C3_Final_5000_Dataset_Excel.xlsx'
SpreadsheetFile.export_xlsx(wb).save(str(out))
print('EXPORTED',out,out.stat().st_size)
try:
 print(wb.inspect({'kind':'table','range':'START_HERE!A4:B9','include':'values','table_max_rows':6,'table_max_cols':2}).ndjson[:1500])
except Exception as e:print('inspect error',e)
