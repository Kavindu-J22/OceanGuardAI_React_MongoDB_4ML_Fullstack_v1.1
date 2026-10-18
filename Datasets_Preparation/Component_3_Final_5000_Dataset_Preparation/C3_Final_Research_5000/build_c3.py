#!/usr/bin/env python3
"""Reproducible C3 physics/biology-constrained synthetic market dataset generator.
All prices, lots, temperatures, and economic decision records are SYNTHETIC.
Sources inform conceptual model but none of the rows are measured observations.
"""
from __future__ import annotations
import csv, json, math, hashlib
from pathlib import Path
from datetime import date, timedelta
import numpy as np

ROOT=Path(__file__).resolve().parent
SEED=20261016
rng=np.random.default_rng(SEED)
START=date(2025,1,1); DAYS=200
SPECIES=[
 {'id':'SP_SKIPJACK','name':'Skipjack tuna','scientific':'Katsuwonus pelamis','base':740.,'baseline_supply':1800.,'k_ref_hr':math.log(2)/190.,'Ea_j_mol':54000.,'histamine_risk':'YES'},
 {'id':'SP_YELLOWFIN','name':'Yellowfin tuna','scientific':'Thunnus albacares','base':1450.,'baseline_supply':1100.,'k_ref_hr':math.log(2)/185.,'Ea_j_mol':57000.,'histamine_risk':'YES'},
 {'id':'SP_MACKEREL','name':'Indian mackerel','scientific':'Rastrelliger kanagurta','base':690.,'baseline_supply':2100.,'k_ref_hr':math.log(2)/140.,'Ea_j_mol':58500.,'histamine_risk':'YES'},
 {'id':'SP_SARDINE','name':'Sardine (generic scenario)','scientific':'Sardinella spp. (not species-resolved)','base':430.,'baseline_supply':2700.,'k_ref_hr':math.log(2)/125.,'Ea_j_mol':56000.,'histamine_risk':'YES'},
 {'id':'SP_SEER','name':'Seer fish / king mackerel (generic)','scientific':'Scomberomorus spp. (not species-resolved)','base':1820.,'baseline_supply':670.,'k_ref_hr':math.log(2)/175.,'Ea_j_mol':60000.,'histamine_risk':'YES'},
]
MARKETS=[
 {'id':'M_PELIYAGODA','name':'Peliyagoda Central Fish Market','port':'P_PELIYAGODA','lat':6.959,'lon':79.901,'mult':1.03},
 {'id':'M_NEGOMBO','name':'Negombo (scenario market)','port':'P_NEGOMBO','lat':7.209,'lon':79.839,'mult':0.99},
 {'id':'M_GALLE','name':'Galle (scenario market)','port':'P_GALLE','lat':6.033,'lon':80.217,'mult':1.04},
 {'id':'M_MIRISSA','name':'Mirissa (scenario market)','port':'P_MIRISSA','lat':5.947,'lon':80.459,'mult':1.07},
 {'id':'M_TANGALLE','name':'Tangalle (scenario market)','port':'P_TANGALLE','lat':6.025,'lon':80.793,'mult':1.05},
]
R_GAS=8.314462618 # J/mol/K
T_REF_K=273.15
CATEGORY='SYNTHETIC_SCENARIO_NOT_OBSERVED'


def save_csv(name,rows,columns=None):
 p=ROOT/name
 if columns is None: columns=list(rows[0])
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore')
  writer.writeheader();writer.writerows(rows)
 return p

def rounded(x,n=4): return round(float(x),n)

def dstr(d): return d.isoformat()

def arr_k(Ea,k_ref,temp_c):
 Tk=float(temp_c)+273.15
 return k_ref*math.exp(-(Ea/R_GAS)*(1/Tk-1/T_REF_K))

def great_circle_km(a,b):
 r=6371.0088; phi1,phi2=math.radians(a['lat']),math.radians(b['lat']);dphi=phi2-phi1;dlon=math.radians(b['lon']-a['lon'])
 h=math.sin(dphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dlon/2)**2
 return 2*r*math.asin(min(1,math.sqrt(h)))

market_price_raw={}
market_rows=[]
random_walk={ (m['id'],s['id']):0. for m in MARKETS for s in SPECIES }
# Common daily weather-influenced landing volume scenarios and shared cost shocks, not observed data
for day in range(DAYS):
 current=START+timedelta(days=day)
 weekend=int(current.weekday()>=5)
 season=1+0.08*math.sin(2*math.pi*day/85+0.3)+0.03*math.cos(2*math.pi*day/31)
 shared_demand_noise=rng.normal(0,.045)
 shared_supply_noise=rng.normal(0,.09)
 daily_market_shock=1+0.035*math.sin(day/10.2)+rng.normal(0,.018)
 for market in MARKETS:
  for species in SPECIES:
   key=(market['id'],species['id'])
   random_walk[key]=float(np.clip(.77*random_walk[key]+rng.normal(0,.027),-.13,.13))
   demand=float(np.clip(0.95+0.10*weekend+0.065*math.sin(2*math.pi*day/33+int(species['base'])/80)+shared_demand_noise+rng.normal(0,.055),.57,1.51))
   supply_ratio=float(np.clip(season*(1+shared_supply_noise + rng.normal(0,.11))*(1-.045*weekend),.46,1.65))
   supply_kg=round(species['baseline_supply']*supply_ratio,2)
   # All prices from explicitly synthetic structural price equation; not empirical Sri Lanka price series.
   shock_idx=float(max(.82,min(1.20,daily_market_shock*(1+random_walk[key]))))
   price=round(species['base']*market['mult']*(demand**.48)*(supply_ratio**(-.40))*shock_idx,2)
   row={
    'record_id':f'C3M{len(market_rows)+1:05d}','date':dstr(current),'market_id':market['id'],
    'market_name':market['name'],'market_port_id':market['port'],'species_id':species['id'],'species_name':species['name'],
    'calendar_day_index':day,'day_of_week_mon0':current.weekday(),'weekend_known_future':weekend,
    'month_known_future':current.month,'base_price_assumed_lkr_kg':species['base'],
    'market_multiplier_assumed':market['mult'],'supply_kg_simulated':supply_kg,
    'baseline_supply_kg_assumed':species['baseline_supply'],
    'supply_ratio_simulated':rounded(supply_ratio,7),'demand_index_simulated':rounded(demand,7),
    'market_shock_index_simulated':rounded(shock_idx,7),'price_lkr_per_kg':price,
    'data_split':('train' if day<140 else 'validation' if day<170 else 'test'),
    'data_provenance':CATEGORY,'price_safety_status':'NOT_REAL_MARKET_QUOTE',
   }
   market_rows.append(row)
   market_price_raw[(day,market['id'],species['id'])]=price
save_csv('C3_Master_5000_Daily_Market_Prices.csv',market_rows)

species_params=[]
for species in SPECIES:
 species_params.append({'species_id':species['id'],'common_name':species['name'],'scientific_name':species['scientific'],
   'initial_price_lkr_kg_synthetic':species['base'],'baseline_supply_kg_synthetic':species['baseline_supply'],
   'reference_temperature_c_assumption':0.0,'quality_proxy_half_life_h_at_0c_assumption':rounded(math.log(2)/species['k_ref_hr'],3),
   'k_ref_per_h_assumption':rounded(species['k_ref_hr'],9),'Arrhenius_Ea_j_per_mol_assumption':species['Ea_j_mol'],
   'histamine_hazard_relevant_group_flag':species['histamine_risk'],
   'source_status':'ASSUMED_UNCALIBRATED_NOT_SPECIES_LAB_MEASURED'})
save_csv('C3_Species_Assumptions.csv',species_params)
save_csv('C3_Market_Registry.csv',[{'market_id':m['id'],'market_name':m['name'],'mapped_port_id':m['port'],
      'scenario_lat_approx':m['lat'],'scenario_lon_approx':m['lon'],'price_factor_assumption':m['mult'],
      'location_status':'APPROX_FOR_SCENARIO_NOT_SURVEYED','price_status':'ALL_SYNTHETIC'} for m in MARKETS])

# Exact historical trailing mean available at a proposed decision date; no tomorrow price in input.
def naive_wait_prediction(day,mid,sid):
 prior=[market_price_raw[(i,mid,sid)] for i in range(max(0,day-6),day+1)]
 return round(float(np.mean(prior)),2)

scenarios=[];options=[];segments=[]
ROAD_FACTOR=1.34 # HAVERSINE * 1.34, explicit scenario multiplier, NOT verified road routing
ROAD_COST_PER_KM=175. # LKR/km, assumption only
ICE_PRICE_KG=42. # LKR/kg, assumption only
BOX_UA_W_K=8.5 # W/K, assumption only (lumped heat-transfer conductance)
ICE_LATENT_KJ_KG=334. # ice latent heat of fusion approx near 0 C
T_AMBIENT_C=28. # assumed effective ambient for box load
MARKET_FEE_FRACTION=.016
HANDLING_LKR_PER_KG=7.
QUALITY_PRICE_PENALTY_WEIGHT=.22
QUALITY_SALEABLE_LOSS_WEIGHT=.065
SCENARIOS=1250

for j in range(SCENARIOS):
 day=int(rng.integers(8,DAYS-1))
 species=SPECIES[int(rng.integers(0,5))]
 origin=MARKETS[int(rng.integers(0,5))]
 sid=species['id']; origin_mid=origin['id']
 batch=float(rng.uniform(75,500))
 catch_age_h=float(rng.uniform(5.0,26.0))
 onboard_temp=float(rng.uniform(0.8,7.5))
 port_wait_h=float(rng.uniform(.5,4.5))
 port_temp=float(rng.uniform(1.3,10.0))
 # Same fish lot quality state across all options at the point of decision.
 lot_segments=[('at_sea_storage',catch_age_h,onboard_temp),('predecision_port_holding',port_wait_h,port_temp)]
 scenario_id=f'C3S{j+1:05d}'
 candidates=sorted([m for m in MARKETS if m['id']!=origin_mid],key=lambda m:great_circle_km(origin,m))[:2]
 scenario_rows=[]
 for opt_index,(action,dest) in enumerate([('SELL_NOW',origin),('WAIT_24H',origin),('TRANSPORT_NOW',candidates[0]),('TRANSPORT_NOW',candidates[1])],start=1):
  is_wait=action=='WAIT_24H'; is_transport=action=='TRANSPORT_NOW'
  dist=round(great_circle_km(origin,dest)*ROAD_FACTOR,2) if is_transport else 0.
  travel_time_h=dist/38 if is_transport else (24. if is_wait else 0.)
  if is_wait:
   transit_temp=float(rng.uniform(0.8,5.0))
  elif is_transport:
   transit_temp=float(rng.uniform(1.0,9.0))
  else:
   transit_temp=float(port_temp)
  sale_queue_h=float(rng.uniform(.3,1.2))
  sale_queue_temp=float(rng.uniform(2.0,8.0))
  entire_segments=lot_segments+[('transport_or_wait',travel_time_h,transit_temp),('auction_queue',sale_queue_h,sale_queue_temp)]
  cumulative_dose=0.
  for seg_num,(segment_name,duration,temp) in enumerate(entire_segments,1):
   k=arr_k(species['Ea_j_mol'],species['k_ref_hr'],temp)
   dose=k*duration
   cumulative_dose+=dose
   segments.append({'option_id':f'{scenario_id}O{opt_index}', 'scenario_id':scenario_id,
    'segment_sequence':seg_num,'segment_type':segment_name,'duration_h':rounded(duration,5),
    'fish_temperature_c_simulated':rounded(temp,5),'k_per_hour_arrhenius_assumed':rounded(k,9),
    'spoilage_dose_increment':rounded(dose,8),'temperature_provenance':CATEGORY})
  freshness=math.exp(-cumulative_dose)
  discount_factor=1-QUALITY_PRICE_PENALTY_WEIGHT*(1-freshness)
  saleable_fraction=.98-QUALITY_SALEABLE_LOSS_WEIGHT*(1-freshness)
  saleable_kg=batch*saleable_fraction
  observed_today=market_price_raw[(day,dest['id'],sid)]
  price_forecast=naive_wait_prediction(day,dest['id'],sid) if is_wait else observed_today
  actual_later=market_price_raw[(day+1,dest['id'],sid)] if is_wait else observed_today
  # For an unlabeled cool-box with temperature higher than 0C, UA model computes only indicative latent heat duty.
  # No claim that amount of ice will ensure required temperature / food safety.
  ice_kg=(BOX_UA_W_K*max(0,T_AMBIENT_C-transit_temp)*travel_time_h*3.6/ICE_LATENT_KJ_KG) if (is_wait or is_transport) else 0.0
  ice_cost=ice_kg*ICE_PRICE_KG
  transport_cost=dist*ROAD_COST_PER_KM
  fixed_handling=HANDLING_LKR_PER_KG*batch
  effective_price_pred=price_forecast*discount_factor
  effective_price_real=actual_later*discount_factor
  gross_pred=effective_price_pred*saleable_kg
  gross_real=effective_price_real*saleable_kg
  fee_pred=gross_pred*MARKET_FEE_FRACTION
  fee_real=gross_real*MARKET_FEE_FRACTION
  net_pred=gross_pred-fee_pred-transport_cost-ice_cost-fixed_handling
  net_real=gross_real-fee_real-transport_cost-ice_cost-fixed_handling
  option={
   'option_id':f'{scenario_id}O{opt_index}','scenario_id':scenario_id,'scenario_date':dstr(START+timedelta(days=day)),
   'origin_port_id':origin['port'],'origin_market_id':origin_mid,'destination_market_id':dest['id'],
   'species_id':sid,'action':action,'lot_weight_kg':rounded(batch,4),
   'total_time_since_catch_h':rounded(sum(seg[1] for seg in entire_segments),4),
   'estimated_route_km_synthetic':rounded(dist,4),'transport_or_wait_h':rounded(travel_time_h,4),
   'cold_chain_spoilage_dose':rounded(cumulative_dose,8),'freshness_quality_proxy_0_1':rounded(freshness,8),
   'quality_discount_multiplier_assumption':rounded(discount_factor,8),
   'saleable_fraction_assumption':rounded(saleable_fraction,8),
   'estimated_saleable_kg':rounded(saleable_kg,4),
   'observed_same_day_synthetic_quote_lkr_kg':rounded(observed_today,2),
   'decision_time_price_estimate_lkr_kg':rounded(price_forecast,2),
   'ex_post_next_day_or_same_day_price_lkr_kg':rounded(actual_later,2),
   'ice_melt_proxy_kg':rounded(ice_kg,6),'ice_cost_lkr':rounded(ice_cost,2),
   'transport_cost_lkr':rounded(transport_cost,2),'handling_cost_lkr':rounded(fixed_handling,2),
   'market_fee_fraction_assumption':MARKET_FEE_FRACTION,
   'expected_net_return_lkr':rounded(net_pred,2),'ex_post_net_return_lkr':rounded(net_real,2),
   'price_forecast_method':('TRAILING_7_DAY_MEAN_NO_FUTURE_LEAKAGE' if is_wait else 'SAME_DAY_SYNTHETIC_QUOTE'),
   'quality_status':'UNCALIBRATED_INDEX_NOT_FOOD_SAFETY_TEST',
   'decision_provenance':CATEGORY,'model_safety_restriction':'DECISION_SUPPORT_DEMONSTRATION_ONLY'
  }
  scenario_rows.append(option); options.append(option)
 best=max(scenario_rows,key=lambda r:r['expected_net_return_lkr'])
 best_oracle=max(scenario_rows,key=lambda r:r['ex_post_net_return_lkr'])
 # a realistically available baseline: SELL_NOW local from same scenario
 baseline=scenario_rows[0]
 scenarios.append({
  'scenario_id':scenario_id,'decision_date':dstr(START+timedelta(days=day)),
  'landing_port_id':origin['port'],'local_market_id':origin_mid,'species_id':sid,
  'species_name':species['name'],'lot_weight_kg':rounded(batch,4),
  'at_sea_hours':rounded(catch_age_h,4),'at_sea_fish_temp_c':rounded(onboard_temp,4),
  'port_wait_hours':rounded(port_wait_h,4),'port_fish_temp_c':rounded(port_temp,4),
  'scenario_best_option_id':best['option_id'],'recommended_action_proxy':best['action'],
  'recommended_market_id':best['destination_market_id'],
  'predicted_best_net_return_lkr':best['expected_net_return_lkr'],
  'predicted_sell_now_baseline_lkr':baseline['expected_net_return_lkr'],
  'predicted_increment_vs_sell_now_lkr':round(best['expected_net_return_lkr']-baseline['expected_net_return_lkr'],2),
  'ex_post_actual_net_for_selected_lkr':best['ex_post_net_return_lkr'],
  'ex_post_oracle_best_option_id_FOR_EVALUATION_ONLY':best_oracle['option_id'],
  'ex_post_regret_lkr_FOR_EVALUATION_ONLY':round(best_oracle['ex_post_net_return_lkr']-best['ex_post_net_return_lkr'],2),
  'decision_provenance':CATEGORY,'requires_food_safety_verification':'YES_NOT_SAFETY_APPROVAL',
 })

save_csv('C3_Lot_Decision_Scenarios_1250.csv',scenarios)
save_csv('C3_Option_Economics_5000.csv',options)
save_csv('C3_Option_Temperature_20000_Segments.csv',segments)

# TFT: 28-day encoder and 7-day prediction target; 25 groups, 200 days -> 4,150 windows.
# Splits based on target window, no target may cross a split; encoder may use preceding history.
features=[]; feature_groups=[]
for market in MARKETS:
 for species in SPECIES:
  series=[r for r in market_rows if r['market_id']==market['id'] and r['species_id']==species['id']]
  assert len(series)==DAYS
  features.append(np.array([[math.log(r['price_lkr_per_kg']),math.log(r['supply_kg_simulated']),r['demand_index_simulated']] for r in series],dtype=np.float32))
  feature_groups.append({'group_id':f"{market['id']}__{species['id']}",'market_id':market['id'],'species_id':species['id']})
allfeat=np.stack(features) # groups * dates * 3
mean=allfeat[:,:140,:].reshape(-1,3).mean(axis=0)
std=allfeat[:,:140,:].reshape(-1,3).std(axis=0)
std=np.where(std==0,1.,std)
windows=[]
# known future calendar: sin and cos dow, sin and cos day-of-year, weekend
for group_index,market_spec in enumerate(feature_groups):
 for forecast_start in range(28,DAYS-7+1):
  end=forecast_start+7
  split='train' if end<=140 else 'validation' if forecast_start>=140 and end<=170 else 'test' if forecast_start>=170 and end<=200 else 'boundary_excluded'
  if split=='boundary_excluded': continue
  known=[]
  for d in range(forecast_start,forecast_start+7):
   dt=START+timedelta(days=d); dow=dt.weekday(); doy=dt.timetuple().tm_yday
   known.append([math.sin(2*math.pi*dow/7),math.cos(2*math.pi*dow/7),math.sin(2*math.pi*doy/365.25),math.cos(2*math.pi*doy/365.25),float(dow>=5)])
  windows.append((group_index,forecast_start,split,((allfeat[group_index,forecast_start-28:forecast_start,:]-mean)/std),np.array(known,dtype=np.float32),
   np.exp(allfeat[group_index,forecast_start:forecast_start+7,0]).astype(np.float32)))

by_split={}
for spl in ['train','validation','test']:
 subs=[w for w in windows if w[2]==spl]
 file=ROOT/f'C3_TFT_{spl}_28to7.npz'
 np.savez_compressed(file,
    encoder_x=np.stack([w[3] for w in subs]), future_known_x=np.stack([w[4] for w in subs]),
    target_price_lkr_kg=np.stack([w[5] for w in subs]),
    group_index=np.array([w[0] for w in subs],dtype=np.int16),
    forecast_start_day=np.array([w[1] for w in subs],dtype=np.int16))
 by_split[spl]={'windows':len(subs),'encoder_shape':[len(subs),28,3],'known_future_shape':[len(subs),7,5],'target_shape':[len(subs),7]}

save_csv('C3_TFT_Training_Scaler.csv',[{'feature_name':name,'mean_train_only':rounded(mu,9),'std_train_only':rounded(sd,9)} for name,mu,sd in zip(['log_price','log_supply','demand_index'],mean,std)])
save_csv('C3_TFT_Group_Index.csv',[{'group_index':i,**v} for i,v in enumerate(feature_groups)])

# Full, machine-readable dictionary with semantic statements and provenance constraints
cols=[]
for typ, data in [('market_master',market_rows[0]),('scenario',scenarios[0]),('option',options[0]),('temperature_segment',segments[0])]:
 for col,val in data.items():
  name=col.lower()
  role=('target' if col=='price_lkr_per_kg' else 'posthoc_label' if 'ex_post' in col or 'best_option' in col or 'regret' in col else 'synthetic_input' if 'assum' in name or 'simulat' in name else 'identifier_or_model_feature')
  unit=('LKR/kg' if 'price' in name and 'lkr' in name else 'LKR' if 'lkr' in name else 'kg' if '_kg' in name else 'h' if '_h' in name or '_hours' in name else 'degC' if 'temp_c' in name else 'dimensionless_or_label')
  cols.append({'table':typ,'column_name':col,'example_value':str(val),'unit_or_type':unit,'purpose':role,
   'provenance':'ALL_ROWS_SYNTHETIC; source references are scientific context, not direct row sources'})
save_csv('C3_Full_Data_Dictionary.csv',cols)

# Sources/reference indexes: NOT actual pulled observations
sources=[
 {'id':'S1','name':'FAO Huss 1995 Quality and quality changes in fresh fish','url':'https://www.fao.org/4/V7180E/V7180e07.htm','application':'Temperature effects and cumulative shelf-life concepts','observational_rows_imported':0},
 {'id':'S2','name':'FAO Codex Code of Practice for Fish and Fishery Products CXC 52-2003','url':'https://www.fao.org/fao-who-codexalimentarius/sh-proxy/pl/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXC%2B52-2003%252FCXC_052e.pdf','application':'Near-0C chilling, histamine hazards: not validated as safe decision model','observational_rows_imported':0},
 {'id':'S3','name':'Ministry of Fisheries Sri Lanka Weekly Fish Prices (2025)','url':'https://www.fisheries.gov.lk/?page_id=8544&paged=3','application':'Identifies authoritative source for empirical future replacement of synthetic prices; spreadsheet download not successful','observational_rows_imported':0},
 {'id':'S4','name':'HARTI Daily Food Commodities Bulletin','url':'https://www.harti.gov.lk/daily-price.php','application':'Candidate cross-check for weekly and daily real market prices','observational_rows_imported':0},
 {'id':'S5','name':'Review: Assessment and Prediction of Fish Freshness Using Mathematical Modelling 2022','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC9368035/','application':'Arrhenius model as spoilage quality proxy','observational_rows_imported':0},
 {'id':'S6','name':'Lim et al. 2021 TFT International Journal of Forecasting','url':'https://doi.org/10.1016/j.ijforecast.2021.03.012','application':'Model architecture: past observed/static/known future separation','observational_rows_imported':0},
 {'id':'S7','name':'Food quality modelling review Oxford Academic','url':'https://academic.oup.com/fst/article/32/1/38/7818609','application':'Arrhenius/temperature-kinetics equation parameter rationale','observational_rows_imported':0},
]
save_csv('C3_Source_Provenance.csv',sources)

manifest={'dataset_name':'C3 Synthetic Fish Market and Perishability Decision Data', 'version':'1.0.0','seed':SEED,
 'coverage':{'start':START.isoformat(),'end':(START+timedelta(days=DAYS-1)).isoformat(), 'days':DAYS,
 'markets':len(MARKETS),'species':len(SPECIES),'market_observation_rows':len(market_rows),
 'decision_scenarios':len(scenarios),'decision_options':len(options),'temperature_steps':len(segments)},
 'market_price_formula':'base_price * market_multiplier * demand_index**0.48 * supply_ratio**(-0.40) * market_shock_index',
 'rate_formula':'k(T) = k_ref * exp[-Ea/R * (1/(T_C+273.15) - 1/273.15)]',
 'freshness_formula':'F = exp(-sum(k(T_segment)*duration_hour))',
 'decision_formula':'expected_net = saleable_kg * estimated_price * (1-.22*(1-F)) * (1-.016) - distance_km*175 - indicative_ice_kg*42 - batch_kg*7',
 'transport_formula':'distance_proxy_km = haversine(origin,destination) * 1.34',
 'indicative_ice_melt_formula':'m_ice_kg = UA_W_per_K * max(T_ambient-T_storage,0) * duration_h * 3.6 / 334',
 'caveat':'All measurements are simulated, Arrhenius parameters uncalibrated; not food safety, route navigation or real prices.',
 'tft_split_policy':'Target dates train days 0..139, val 140..169, test 170..199; boundary-crossing target windows excluded.',
 'tft':by_split,'references':sources}
(ROOT/'C3_Manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')

readme=f'''# C3 Research Dataset, v1.0 - synthetic prototype\n\n**PRIMARY DATASET: C3_Master_5000_Daily_Market_Prices.csv — 5,000 records exactly.**\n25 daily series = 5 markets × 5 species; {START} to {START+timedelta(days=199)} inclusive.\n\n**CRITICAL: NONE OF THE DATASET ROWS ARE REAL OBSERVATIONS, OFFICIAL FISH PRICES OR LAB MEASUREMENTS.**\nAll market prices are generated from a transparent demand–supply structural proxy. All fish-quality kinetic parameters, logistics costs and storage temperatures are scenario assumptions. No 2025 fish-price workbook was imported. See C3_Source_Provenance.csv.\n\n## Contents\n- C3_Master_5000_Daily_Market_Prices.csv: main 5,000 model observations.\n- C3_Lot_Decision_Scenarios_1250.csv: 1,250 independent synthetic fish landing decisions.\n- C3_Option_Economics_5000.csv: four comparable options per same lot (sell now, wait, transport to two alternative markets).\n- C3_Option_Temperature_20000_Segments.csv: four full temperature/history segments per option; all heat/damage model inputs visible.\n- C3_TFT_train_28to7.npz, C3_TFT_validation_28to7.npz, C3_TFT_test_28to7.npz: leakage-aware temporal samples, price forecasts with 28-day context, 7-day horizons.\n- C3_TFT_Training_Scaler.csv: fitted on train period only.\n- C3_Species_Assumptions.csv: illustrative not measured species kinetics / base prices.\n- C3_Market_Registry.csv, C3_Full_Data_Dictionary.csv, C3_Source_Provenance.csv, C3_Manifest.json.\n- build_c3.py: full deterministic synthetic generator.\n- validate_c3.py: independent recalc and integrity tests.\n- C3_Dataset_Justification_Sinhala.docx: Sinhala rationale and references.\n\n## Usage\npython build_c3.py\npython validate_c3.py\n\nUse pure market master for TFT price forecasting and scenario/options/temperature for the separate decision and degradation optimization module. Avoid training TFT on columns that contain ex-post next-day/oracle prices. C2 shares Galle/Mirissa/Tangalle port IDs and Yellowfin/Skipjack concepts but no actual catch ID join exists. Do not falsely join C1 (different periods) or claim integrated empirical validation.\n\n## Food safety\nThe quality proxy is *not* a microbiological safety/edibility predictor; it cannot detect histamine. Never advise selling/eating fish based only on this synthetic quality index. Temperature control and verified inspection are required.\n'''
(ROOT/'README_FIRST.md').write_text(readme,encoding='utf-8')
print(json.dumps({"master":len(market_rows),"scenarios":len(scenarios),"options":len(options),"segments":len(segments),"tft":by_split,"min_price":min(r['price_lkr_per_kg'] for r in market_rows),"max_price":max(r['price_lkr_per_kg'] for r in market_rows)},indent=2))
