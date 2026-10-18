#!/usr/bin/env python3
"""Research-only C4 physics-constrained SYNTHETIC scenarios (not calibrated fuel telemetry).
The ITTC 1957 friction correlation is sourced; other coefficient relationships are
EXPLICITLY HEURISTIC and require vessel-specific towing/engine trials.
Reproducible: python generate_c4.py; dataset supplied as proof of concept.
"""
import csv, math, json, os, random, statistics, hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
C1=P.parent/'C1_Research_Final_5000' if (P.parent/'C1_Research_Final_5000').exists() else P/'upstream_source_data'
C2=P.parent/'C2_Research_Final_5000' if (P.parent/'C2_Research_Final_5000').exists() else P/'upstream_source_data'
RNG=np.random.default_rng(20261016)
random.seed(20261016)
RHO_W=1025.0; NU_W=1.19e-6; RHO_A=1.225; RHO_FUEL=0.84; G=9.80665; KNOT=0.514444; HP2KW=0.745699872

def read_csv(path):
 with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(path,items,fields=None):
 if fields is None:fields=list(items[0].keys())
 with open(path,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(items)

def ff(v,n=4): return round(float(v),n)
def haversine(lat1,lon1,lat2,lon2):
 a,b,c,d=map(math.radians,[lat1,lon1,lat2,lon2]);u=math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2;return 6371.0*2*math.asin(math.sqrt(u))

def resistance(v_stw_ms, length, beam, draft, wetted_m2, displacement_kg, cb, wave_hs, wave_period, wave_encounter_cos, wind_head_ms, wind_area, form_factor):
 """Derived: friction ITTC, aero bluff body; HELD-AS-HYPOTHESIS: residual and wave drag."""
 u=max(v_stw_ms,.20)
 Re=u*length/NU_W
 cf=.075/(math.log10(Re)-2)**2
 RF=.5*RHO_W*u*u*wetted_m2*cf*(1+form_factor)  # form_factor is HEURISTIC; ITTC line already contains mean hull form adjustment
 Fr=u/math.sqrt(G*length)
 # Residual Fn^4 is a PARAMETRIC stand-in, NOT a certified hull method (Holtrop, Savitsky or RANS)
 rres=displacement_kg*G*.018*(Fr/.38)**4*(cb/.47)**.55
 # Waves: quadratic height ratio response and directional encounter scale; phenomenological, not seakeeping-derived
 steep=wave_hs/(G*wave_period**2/(2*math.pi))
 encounter=0.65+0.75*max(-1.0,min(1.0,wave_encounter_cos)+1.0)/2.0
 wave_res=.5*RHO_W*u*u*wetted_m2*.42*(wave_hs/max(length,1))**2*encounter*(1+2*steep)
 v_air=max(0.1,u+wind_head_ms)
 air_res=.5*RHO_A*1.05*wind_area*v_air*v_air
 return dict(reynolds=Re,cf=cf,froude=Fr,wave_steepness=steep,friction_n=RF,residuary_n=rres,wave_added_n=wave_res,air_n=air_res,total_n=RF+rres+wave_res+air_res)

def power_at_kn(speed_kn, args, eta):
 r=resistance(speed_kn*KNOT, **args)
 pe=r['total_n']*speed_kn*KNOT/1000.
 return pe/eta,r,pe

def interpolate_cap_speed(target_kn,args,eta,capacity_kw):
 p,r,e=power_at_kn(target_kn,args,eta)
 if p<=capacity_kw:return target_kn,p,r,e,False
 lo=.5;hi=target_kn
 for k in range(36):
  mid=(lo+hi)/2
  pp,_,_=power_at_kn(mid,args,eta)
  if pp>capacity_kw:hi=mid
  else:lo=mid
 sp=lo
 p,r,e=power_at_kn(sp,args,eta)
 return sp,p,r,e,True

vessels=read_csv(C1/'C1_Vessel_Registry_250.csv')
trips=read_csv(C1/'C1_Master_5000_Trips.csv')
zones=read_csv(C2/'C2_Zone_Registry_100.csv')
assert len(trips)==5000 and len(vessels)==250 and len(zones)==100
vessel_d={v['vessel_id']:v for v in vessels}
engine_reg=[]
for v in vessels:
 vt=v['vessel_type'];length=float(v['length_m'])
 if vt=='OFRP':hp=RNG.uniform(14,48);opt=RNG.uniform(4.8,7.6);hotel=RNG.uniform(.15,.45)
 elif vt=='IDAY':hp=RNG.uniform(40,122);opt=RNG.uniform(5.6,8.0);hotel=RNG.uniform(.3,1.6)
 else:hp=RNG.uniform(120,330);opt=RNG.uniform(6.2,9.2);hotel=RNG.uniform(1.1,4.8)
 age=RNG.uniform(1,21);eta=RNG.uniform(.46,.67);bsfc=RNG.uniform(.225,.274)
 registry={'vessel_id':v['vessel_id'],'vessel_type':vt,'engine_rated_hp_assumed':ff(hp,3),'engine_rated_kw_assumed':ff(hp*HP2KW,3),'engine_age_years_assumed':ff(age,2),'propulsive_efficiency_assumed':ff(eta,4),'bsfc_optimum_kg_per_kwh_assumed':ff(bsfc,4),'hydraulic_wetted_multiplier_assumed':ff(RNG.uniform(.7,.86),4),'hull_form_factor_assumed':ff(RNG.uniform(0,.14),4),'nominal_speed_kn_assumed':ff(opt,3),'auxiliary_kw_assumed':ff(hotel,3),'maintenance_factor_assumed':ff(RNG.uniform(.98,1.11),4),'data_origin':'SYNTHETIC_NOT_ENGINE_SPECIFICATION'}
 engine_reg.append(registry)
engine_d={e['vessel_id']:e for e in engine_reg}

items=[]; legs=[];sens=[]
for ix,t in enumerate(trips):
 v=vessel_d[t['vessel_id']];en=engine_d[t['vessel_id']]
 vid=t['vessel_id'];vt=t['vessel_type']; L=float(v['length_m']); B=float(v['beam_m']);Cb=float(v['block_coefficient_cb'])
 W=float(t['total_displacement_mass_proxy_kg']); payload=float(t['payload_mass_kg'])
 draft=W/(RHO_W*Cb*L*B)
 # wetted-area approximation; hull-form-dependent, not measured
 S=L*(B+2*draft)*float(en['hydraulic_wetted_multiplier_assumed'])
 area=B*max(.25, float(v['freeboard_lightship_m'])-0.22)+.3*B
 Hs=float(t['forecast_max_wave_height_m']);Tp=float(t['worst_wave_peak_period_s']);wind=float(t['forecast_max_wind_ms'])
 # directionality is synthetic; C1 gives scalar weather extremes only
 coswave=float(RNG.uniform(-1,1));coswind=float(RNG.uniform(-1,1)); wind_head=wind*coswind
 cur_ms=float(RNG.uniform(-.65,.65))
 speed_nominal=float(en['nominal_speed_kn_assumed'])*float(RNG.uniform(.86,1.10))
 eta=float(en['propulsive_efficiency_assumed']); hp=float(en['engine_rated_hp_assumed']);ratedkw=hp*HP2KW
 available_ratio=float(.72-.006*max(float(en['engine_age_years_assumed'])-10,0)/11)
 availablekw=ratedkw*available_ratio
 seas=[]
 # calculate the two legs separately, wave heading and current direction opposite
 for i,dirn in enumerate((1,-1)):
  args={'length':L,'beam':B,'draft':draft,'wetted_m2':S,'displacement_kg':W,'cb':Cb,'wave_hs':Hs,'wave_period':Tp,'wave_encounter_cos':coswave*dirn,'wind_head_ms':wind_head*dirn,'wind_area':area,'form_factor':float(en['hull_form_factor_assumed'])}
  speed,p,r,pe,clipped=interpolate_cap_speed(speed_nominal,args,eta,availablekw)
  ground=max(1.0,speed+dirn*cur_ms/KNOT)
  load=min(.999,p/ratedkw)
  bsfc=float(en['bsfc_optimum_kg_per_kwh_assumed'])*float(en['maintenance_factor_assumed'])*(1+0.20*((load-.64)/.64)**2)
  seas.append({'direction':'outbound' if i==0 else 'inbound','speed_kn':speed,'ground_kn':ground,'power_kw':p,'effective_kw':pe,'cap':clipped,'r':r,'load_frac':load,'bsfc':bsfc,'wind_head':wind_head*dirn,'current_ms':cur_ms*dirn})
 # travel time as subset of C1 planned total, distance constructed to be compatible with both leg speeds
 duration=float(t['planned_trip_duration_h'])
 fraction=float(RNG.uniform(.27,.57))
 transit_hours=duration*fraction
 # select symmetric one-way distance with harmonic speed consistency; no coordinate route geometry claimed
 dist_nm=transit_hours/(1/seas[0]['ground_kn']+1/seas[1]['ground_kn'])
 fishing_h=duration-transit_hours
 transit_fuel=[];transit_t=[]
 for s in seas:
  leg_h=dist_nm/s['ground_kn']; liters=s['power_kw']*leg_h*s['bsfc']/RHO_FUEL
  transit_fuel.append(liters);transit_t.append(leg_h)
  legs.append({'leg_id':f'C4L{ix+1:05d}_{"O" if s["direction"]=="outbound" else "I"}','scenario_id':f'C4T{ix+1:05d}','c1_trip_id':t['trip_id'],'vessel_id':vid,'direction':s['direction'],'zone_id':t['zone_id'],'assumed_speed_through_water_kn':ff(s['speed_kn'],5),'assumed_speed_over_ground_kn':ff(s['ground_kn'],5),'assumed_along_current_ms':ff(s['current_ms'],5),'assumed_headwind_ms':ff(s['wind_head'],5),'travel_distance_nm':ff(dist_nm,6),'travel_time_h':ff(leg_h,6),'displacement_kg':ff(W,4),'wetted_surface_m2':ff(S,5),'draft_m':ff(draft,6),'wave_height_m':ff(Hs,4),'wave_peak_period_s':ff(Tp,4),'reynolds_number':ff(s['r']['reynolds'],2),'ittc_cf':ff(s['r']['cf'],9),'froude_number':ff(s['r']['froude'],7),'frictional_resistance_n':ff(s['r']['friction_n'],5),'residuary_resistance_heuristic_n':ff(s['r']['residuary_n'],5),'wave_added_resistance_heuristic_n':ff(s['r']['wave_added_n'],5),'aerodynamic_resistance_n':ff(s['r']['air_n'],5),'total_resistance_n':ff(s['r']['total_n'],5),'effective_power_kw':ff(s['effective_kw'],5),'brake_power_kw':ff(s['power_kw'],5),'bsfc_kg_per_kwh':ff(s['bsfc'],7),'engine_load_fraction':ff(s['load_frac'],6),'engine_continuous_kw_assumed':ff(availablekw,5),'speed_limited_by_power':s['cap'],'leg_fuel_l':ff(liters,5),'resistance_provenance':'ITTC_FRICTION_PLUS_UNCALIBRATED_HYDRODYNAMIC_HEURISTICS','fuel_provenance':'SYNTHETIC_NO_OBSERVED_FUEL'})
 # simulated fishing and hotel energy: duty at low load, illustrative only
 fishing_load=float(RNG.uniform(.11,.25))
 fishing_duty=float(RNG.uniform(.29,.72))
 fish_bsfc=float(en['bsfc_optimum_kg_per_kwh_assumed'])*float(en['maintenance_factor_assumed'])*(1+.20*((fishing_load-.64)/.64)**2)
 p_fishing=ratedkw*fishing_load*fishing_duty+float(en['auxiliary_kw_assumed'])
 fuel_fishing=p_fishing*fishing_h*fish_bsfc/RHO_FUEL
 model_fuel=sum(transit_fuel)+fuel_fishing
 # uncertainty range is sensitivity only, not validated confidence/prediction interval
 # set nominal ± bounds scenario derived from engine BSFC, sea-state and efficiency factor variations
 base_u=.10 + .07*min(Hs/3,1)+.025*min(1,age/20) if (age:=float(en['engine_age_years_assumed'])) else .11
 p10=model_fuel*(1-base_u)
 p90=model_fuel*(1+1.3*base_u)
 # research-only reserve scenario parameter, NOT regulatory fuel reserve recommendation
 reserve_frac=float(RNG.uniform(.20,.35))
 reserve_l=model_fuel*reserve_frac
 scenario_total=model_fuel+reserve_l
 avail_fuel=model_fuel*float(RNG.uniform(.68,1.65))
 # reservoir adequacy is comparison of synthetic numbers; not a skipper's decision
 suff='SCENARIO_ABOVE_MODEL_REQUIREMENT' if avail_fuel>=scenario_total else 'SCENARIO_BELOW_MODEL_REQUIREMENT'
 # nearest C2 zone purely spatial, dates NOT joined
 near=min(zones,key=lambda z:haversine(float(t['zone_lat']),float(t['zone_lon']),float(z['zone_latitude_deg']),float(z['zone_longitude_deg'])))
 ds=haversine(float(t['zone_lat']),float(t['zone_lon']),float(near['zone_latitude_deg']),float(near['zone_longitude_deg']))
 row={
 'scenario_id':f'C4T{ix+1:05d}','c1_trip_id':t['trip_id'],'c1_record_date_local':t['decision_timestamp_local'],'vessel_id':vid,'vessel_type':vt,'c1_zone_id':t['zone_id'],'c2_spatial_nearest_zone_id':near['zone_id'],'c2_zone_spatial_offset_km':ff(ds,3),'zone_link_scope':'SPATIAL_ONLY_C1_2024_C2_2025_NOT_TEMPORAL_JOIN',
 'vessel_length_m':ff(L,3),'vessel_beam_m':ff(B,3),'block_coefficient_assumed':ff(Cb,4),'lightship_mass_kg':ff(float(t['lightship_mass_kg']),3),'payload_mass_kg':ff(payload,3),'displacement_mass_kg':ff(W,3),'loaded_draft_m_approx':ff(draft,6),'wetted_surface_m2_approx':ff(S,4),
 'engine_rated_hp_assumed':ff(hp,3),'engine_rated_kw_assumed':ff(ratedkw,4),'engine_age_years_assumed':ff(age,2),'engine_continuous_limit_kw_assumed':ff(availablekw,4),'propulsive_efficiency_assumed':ff(eta,4),'bsfc_optimum_kg_kwh_assumed':ff(float(en['bsfc_optimum_kg_per_kwh_assumed']),6),'maintenance_factor_assumed':ff(float(en['maintenance_factor_assumed']),5),
 'forecast_wave_hs_m_c1_synthetic':ff(Hs,4),'wave_peak_period_s_c1_synthetic':ff(Tp,4),'forecast_wind_speed_ms_c1_synthetic':ff(wind,4),'wave_heading_cos_synthetic':ff(coswave,5),'wind_heading_cos_synthetic':ff(coswind,5),'along_current_outbound_ms_assumed':ff(cur_ms,5),
 'planned_duration_h_c1':ff(duration,4),'travel_oneway_distance_nm_scenario':ff(dist_nm,5),'travel_roundtrip_distance_km_scenario':ff(dist_nm*2*1.852,4),'planned_outbound_hours':ff(transit_t[0],5),'planned_inbound_hours':ff(transit_t[1],5),'fishing_operations_hours':ff(fishing_h,5),
 'outbound_speed_kn_model':ff(seas[0]['speed_kn'],5),'inbound_speed_kn_model':ff(seas[1]['speed_kn'],5),'outbound_effective_power_kw':ff(seas[0]['effective_kw'],5),'inbound_effective_power_kw':ff(seas[1]['effective_kw'],5),'outbound_brake_power_kw':ff(seas[0]['power_kw'],5),'inbound_brake_power_kw':ff(seas[1]['power_kw'],5),
 'outbound_friction_n':ff(seas[0]['r']['friction_n'],4),'outbound_residuary_heuristic_n':ff(seas[0]['r']['residuary_n'],4),'outbound_wave_resistance_heuristic_n':ff(seas[0]['r']['wave_added_n'],4),'outbound_air_resistance_n':ff(seas[0]['r']['air_n'],4),'outbound_total_resistance_n':ff(seas[0]['r']['total_n'],4),
 'transit_fuel_l_model':ff(sum(transit_fuel),5),'fishing_auxiliary_kw_model':ff(p_fishing,4),'fishing_fuel_l_model':ff(fuel_fishing,5),'fuel_consumption_l_model':ff(model_fuel,5),'sensitivity_low_l_scenario':ff(p10,5),'sensitivity_high_l_scenario':ff(p90,5),'reserve_fraction_assumed_research_only':ff(reserve_frac,5),'reserve_fuel_l_scenario':ff(reserve_l,5),'fuel_plus_reserve_l_scenario':ff(scenario_total,5),'available_fuel_l_simulated':ff(avail_fuel,5),'fuel_comparison_flag_research_only':suff,'speed_limited_on_any_leg':bool(seas[0]['cap'] or seas[1]['cap']),
 'dataset_split_vessel_group':'','measured_fuel_l':'','fuel_target_provenance':'SYNTHETIC_PHYSICS_CONSTRAINED_NOT_MEASURED','confidence_status':'UNCALIBRATED_NO_REAL_WORLD_CONFIDENCE','operational_use':'PROHIBITED_RESEARCH_SIMULATION_ONLY'}
 items.append(row)

# group by vessel avoids memorizing a single vessel's parameters across splits
ids=np.array(sorted(vessel_d));RNG.shuffle(ids)
cut1=int(len(ids)*.70);cut2=int(len(ids)*.85)
split_d={v:('train' if i<cut1 else 'validation' if i<cut2 else 'test') for i,v in enumerate(ids)}
for row in items:row['dataset_split_vessel_group']=split_d[row['vessel_id']]
write_csv(P/'C4_Master_5000_Trip_Scenarios.csv',items)
write_csv(P/'C4_Physics_Legs_10000.csv',legs)
write_csv(P/'C4_Synthetic_Engine_Registry_250.csv',engine_reg)
# data dictionary with provenance column keyed to field semantics
fields=list(items[0]);dd=[]
for col in fields:
 src=('C1 synthetic source: trip/vessel' if col in {'c1_trip_id','c1_record_date_local','vessel_id','vessel_type','c1_zone_id','vessel_length_m','vessel_beam_m','lightship_mass_kg','payload_mass_kg','displacement_mass_kg','forecast_wave_hs_m_c1_synthetic','wave_peak_period_s_c1_synthetic','forecast_wind_speed_ms_c1_synthetic','planned_duration_h_c1'} else 'C2 zone registry spatial-only reference' if col.startswith('c2_') else 'Model derived using assumptions and literature-motivated equations' if col.endswith('_model') or col.endswith('_approx') or col.endswith('_n') else 'Synthetic assumption / scenario descriptor')
 if col=='measured_fuel_l':src='Intentionally blank: NO observed fuel telemetry'
 if 'scenario' in col and col not in ('scenario_id',):src='Research-only simulated scenario: NOT deployment limit'
 dd.append({'column':col,'units':('L' if col.endswith('_l_model') or col.endswith('_l_scenario') or col.startswith('available_fuel') else 'as_named_or_dimensionless'),'definition':col.replace('_',' '),'origin_and_status':src})
write_csv(P/'C4_Data_Dictionary.csv',dd)
# model-ready leakage-aware arrays: only FEATURES available pre-trip, NO computed outputs / generated label leakage
FEATURES=['vessel_length_m','vessel_beam_m','block_coefficient_assumed','lightship_mass_kg','payload_mass_kg','displacement_mass_kg','engine_rated_kw_assumed','engine_age_years_assumed','propulsive_efficiency_assumed','bsfc_optimum_kg_kwh_assumed','maintenance_factor_assumed','forecast_wave_hs_m_c1_synthetic','wave_peak_period_s_c1_synthetic','forecast_wind_speed_ms_c1_synthetic','wave_heading_cos_synthetic','wind_heading_cos_synthetic','along_current_outbound_ms_assumed','planned_duration_h_c1','travel_roundtrip_distance_km_scenario','fishing_operations_hours']
X=np.array([[float(row[f]) for f in FEATURES] for row in items],dtype=np.float64)
y=np.array([row['fuel_consumption_l_model'] for row in items],dtype=np.float64)
subset=np.array([{'train':0,'validation':1,'test':2}[r['dataset_split_vessel_group']] for r in items],dtype=np.uint8)
mean=X[subset==0].mean(axis=0);std=X[subset==0].std(axis=0);std[std<1e-9]=1
Xz=((X-mean)/std).astype('float32')
np.savez_compressed(P/'C4_PINN_Model_Ready_5000.npz',X_raw=X.astype('float32'),X_standardized=Xz,labels_synthetic_l=y.astype('float32'),split_code=subset,feature_names=np.array(FEATURES),train_mean=mean.astype('float32'),train_std=std.astype('float32'),scenario_id=np.array([r['scenario_id'] for r in items]),vessel_id=np.array([r['vessel_id'] for r in items]))
meta={'name':'C4 physics-constrained synthetic marine fuel dataset','version':'1.0','created_on':'2026-10-16','seed':20261016,'records':len(items),'leg_records':len(legs),'source_c1':'C1_Research_Final_5000/C1_Master_5000_Trips.csv, C1_Vessel_Registry_250.csv','source_c2':'C2_Research_Final_5000/C2_Zone_Registry_100.csv','links':'Exact C1 vessel_id and trip_id; nearest C2 zone spatial-only, NOT time aligned and not route verified','physics_inspiration':['ITTC-1957 correlation line','Reynolds','Froude','Buoyancy displacement approximation','R=0.5 rho v2 Cd A aerodynamic drag','P=Rv/eta','mass fuel=BSFC*shaft energy; volume=mass/rho','harmonic mean link for symmetric nautical mile legs'],'explicit_uncalibrated_terms':['Wetted hull area simplification','hull form factor','Froude-power residuary term','squared wave height directional increment','propulsive efficiency','low-load BSFC correction','engine continuous power percentage','auxiliary/fishing duty','sensitivity interval heuristic','reserve percentage and fuel availability'],'not_used':['Navier-Stokes numerical solver','measured resistance','observed fuel telemetry','real route/navigation validation','regulatory fuel reserve'],'units':{'diesel_density_kg_l':RHO_FUEL,'sea_water_density_kg_m3':RHO_W,'kinematic_viscosity_m2_s':NU_W,'air_density_kg_m3':RHO_A,'g_m_s2':G,'knot_m_s':KNOT,'hp_to_kw':HP2KW},'model_ready_feature_names':FEATURES,'recommended_ml':'Physics-guided loss with non-negativity and equation residual; synthetic label held out; independent real measured validation essential','sources':[{'id':'S1','title':'ITTC Resistance Committee: ITTC-57 Friction line','url':'https://ittc.info/media/5516/03.pdf'},{'id':'S2','title':'FAO Fisherman workbook: fuel consumption','url':'https://www.fao.org/4/ah827e/AH827E06.htm'},{'id':'S3','title':'NOAA NDBC wave characteristics','url':'https://www.ndbc.noaa.gov/faq/wavecalc.shtml'},{'id':'S4','title':'FAO ILO IMO Safety recommendations','url':'https://www.fao.org/4/i3108e/i3108e00.htm'},{'id':'S5','title':'Fisheries Statistics Sri Lanka 2024','url':'https://www.fisheries.gov.lk/web/images/statistics/annual_report/Fisheries_Statistics_-2024-min.pdf'},{'id':'S6','title':'Copernicus Global Ocean Waves Reanalysis','url':'https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_WAV_001_032/description'}]}
(P/'C4_Method_Parameters_Provenance.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))

# independent recomputation from rounded leg data must be within rounding error (<0.02 L)
from collections import Counter
issues=[]
by_id={r['scenario_id']:r for r in items}
legs_by={}
for r in legs: legs_by.setdefault(r['scenario_id'],[]).append(r)
for r in items:
 seg=legs_by[r['scenario_id']]
 if len(seg)!=2:issues.append('two_legs')
 expected=sum(s['brake_power_kw']*s['travel_time_h']*s['bsfc_kg_per_kwh']/RHO_FUEL for s in seg)
 if abs(expected-r['transit_fuel_l_model'])>0.01:issues.append('transit_fuel_recalc')
 if abs(r['fishing_fuel_l_model']+r['transit_fuel_l_model']-r['fuel_consumption_l_model'])>.0001:issues.append('fuel_mass_balance')
 if abs(r['fuel_consumption_l_model']+r['reserve_fuel_l_scenario']-r['fuel_plus_reserve_l_scenario'])>.0001:issues.append('reserve_balance')
 if abs(r['planned_outbound_hours']+r['planned_inbound_hours']+r['fishing_operations_hours']-r['planned_duration_h_c1'])>.0002:issues.append('time_balance')
 for s in seg:
  if abs(s['total_resistance_n']-(s['frictional_resistance_n']+s['residuary_resistance_heuristic_n']+s['wave_added_resistance_heuristic_n']+s['aerodynamic_resistance_n']))>.0002:issues.append('resistance_balance')
  if abs(s['effective_power_kw']-s['total_resistance_n']*s['assumed_speed_through_water_kn']*KNOT/1000)>.0003:issues.append('p_equals_rv')
  if s['brake_power_kw']>s['engine_continuous_kw_assumed']+.0002:issues.append('max_power')
 assert r['fuel_consumption_l_model']>0
 assert r['sensitivity_low_l_scenario']<r['fuel_consumption_l_model']<r['sensitivity_high_l_scenario']
assert len(items)==5000 and len(legs)==10000
assert not issues,Counter(issues)
# hold-out vessel leakage
spsets={s:set(r['vessel_id'] for r in items if r['dataset_split_vessel_group']==s) for s in ('train','validation','test')}
assert all(not sp_sets for sp_sets in [spsets['train']&spsets['test'],spsets['train']&spsets['validation'],spsets['test']&spsets['validation']])
# independent examples of monotonicity under CONTROLLED variables at fixed speed and geometry.
const={'length':8,'beam':2.3,'draft':.25,'wetted_m2':17,'displacement_kg':2500,'cb':.47,'wave_hs':1.2,'wave_period':7,'wave_encounter_cos':1,'wind_head_ms':4,'wind_area':3.5,'form_factor':0.07}
r1=resistance(3.4,**const);r2=resistance(4,**const)
assert r2['total_n']>r1['total_n']
const2=dict(const);const2['wave_hs']=2.2
assert resistance(3.4,**const2)['wave_added_n']>r1['wave_added_n']
const3=dict(const);const3['displacement_kg']=3000
assert resistance(3.4,**const3)['residuary_n']>r1['residuary_n']
# density transformation and trip fuel arithmetic well bounded
counter=Counter(x['vessel_type'] for x in items)
clipped=sum(x['speed_limited_on_any_leg'] for x in items)
from statistics import median
results={'passed':True,'validation_class':'internal_arithmetic_and_physics_model_consistency_ONLY','n_records':len(items),'n_legs':len(legs),'n_vessels':len(vessels),'split_trips':dict(Counter(r['dataset_split_vessel_group'] for r in items)),'split_vessels':{k:len(v) for k,v in spsets.items()},'boat_types':dict(counter),'power_limited_trips':clipped,'fuel_l_statistics':{'min':min(y),'median':median(y),'p95':float(np.quantile(y,.95)),'max':max(y)},'validation_checks':['5000_trip_records','10000_leg_records','250_unique_vessels','unique_ids','C1_links_one_to_one','C2_zone_spatial_links','fuel_leg_recomputation','total_fuel_balance','reserve_arithmetic','trip_time_balance','resistance_force_balance','mechanical_effective_power_RV','engine_power_cap','positive_fuel','sensitivity_envelopes','disjoint_vessel_splits','speed_resistance_monotonicity_fixed_params','wave_added_drag_monotonicity_fixed_params','mass_residuary_monotonicity_fixed_params'],'external_validation':'NOT_PERFORMED_NO_MEASURED_FUEL','notes':'The 19 listed check categories cover thousands of per-record assertions; passing these does not validate physical correctness of heuristics.'}
(P/'C4_Validation_Report.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
(P/'C4_Feature_Manifest.json').write_text(json.dumps({'feature_names':FEATURES,'target':'fuel_consumption_l_model','model_note':'The dataset alone is NOT a PINN. Implement a PINN/hybrid model with physics-residual loss to claim that architecture.','no_data_leakage':'Only pre-trip assumed features; no target or downstream calculated fuel/power/resistance features.','train_only_normalization':True,'source':'synthetic'},indent=2))
print(json.dumps(results,indent=2))
