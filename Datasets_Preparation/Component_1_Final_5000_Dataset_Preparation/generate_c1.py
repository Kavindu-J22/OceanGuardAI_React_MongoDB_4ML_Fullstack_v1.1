"""C1 vessel-specific safety: REPRODUCIBLE PHYSICS-CONSTRAINED SYNTHETIC DATA.
Not a measured weather archive, real-vessel registry, or certified safety predictor.
"""
import math, json, csv
from pathlib import Path
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parent
RNG=np.random.default_rng(20261016)
N=5000; N_VESSELS=250; STEPS=12
G=9.80665; RHO_SEA=1025.0; RHO_AIR=1.225; CD=1.10
TYPE_SPEC={
  'OFRP': dict(p=.51,L=(5.4,8.1),B=(1.65,2.55),light=(450,1250),capacity=(450,1400),freeboard=(.62,1.07),cb=(.36,.48),cwp=(.65,.79),hours=(4,15),crew=(2,4)),
  'IDAY': dict(p=.30,L=(8.4,12.0),B=(2.5,3.8),light=(2100,5600),capacity=(1500,4600),freeboard=(.95,1.55),cb=(.42,.56),cwp=(.71,.84),hours=(8,32),crew=(3,6)),
  'IMUL': dict(p=.19,L=(12.4,19.6),B=(3.35,5.25),light=(8500,22000),capacity=(4800,15000),freeboard=(1.36,2.35),cb=(.49,.65),cwp=(.77,.90),hours=(48,160),crew=(4,8)),
}
# Representative offshore points, not navigational waypoints.
ZONES=[
  ('Z01','Negombo Offshore',7.35,79.38,'west'),
  ('Z02','Kalpitiya Offshore',8.42,79.28,'west'),
  ('Z03','Colombo Offshore',6.88,79.40,'west'),
  ('Z04','Beruwala Offshore',6.40,79.45,'west'),
  ('Z05','Galle Offshore',5.75,79.95,'south'),
  ('Z06','Matara Offshore',5.58,80.48,'south'),
  ('Z07','Hambantota Offshore',5.74,81.18,'south'),
  ('Z08','Trincomalee Offshore',8.65,82.10,'east'),
  ('Z09','Batticaloa Offshore',7.45,82.20,'east'),
  ('Z10','Point Pedro Offshore',9.88,80.68,'north'),
]

def r(a,b): return float(RNG.uniform(a,b))
def clamp(x,lo=0.,hi=1.): return float(np.clip(x,lo,hi))
def round3(x): return round(float(x),3)

# Vessel-level synthetic profile; dimensions are **assumptions**, not real registry specifications.
V=[]
for k in range(N_VESSELS):
    typ=str(RNG.choice(list(TYPE_SPEC),p=[x['p'] for x in TYPE_SPEC.values()]))
    sp=TYPE_SPEC[typ]; L=r(*sp['L']); B=r(*sp['B']); light=r(*sp['light']); capacity=r(*sp['capacity'])
    cwp=r(*sp['cwp']); cb=r(*sp['cb']); freeboard0=r(*sp['freeboard'])
    crew_max=int(RNG.integers(sp['crew'][0],sp['crew'][1]+1))
    V.append(dict(vessel_id=f'V{k+1:03d}',vessel_type=typ,length_m=round3(L),beam_m=round3(B),lightship_mass_kg=round3(light),
        nominal_payload_limit_kg=round3(capacity),freeboard_lightship_m=round3(freeboard0),waterplane_coefficient_cwp=round3(cwp),
        block_coefficient_cb=round3(cb),nominal_crew_capacity=crew_max,design_source='synthetic_assumed_not_certified'))
reg=pd.DataFrame(V)

# Distinct weather exposure per trip, stochastic scenarios tempered by seasonal changes.
# We intentionally oversample hazardous scenarios; NOT an unbiased Sri Lankan weather climatology.
scenarios=['calm','moderate','rough','severe']
scen_prob=[.24,.34,.27,.15]

# 2023-2025 chronological split, data from ALL partitions remain synthetic.
dates_train=pd.date_range('2023-01-01','2024-12-31',freq='D')
dates_val=pd.date_range('2025-01-01','2025-06-30',freq='D')
dates_test=pd.date_range('2025-07-01','2025-12-31',freq='D')
parts=[('train',3500,dates_train),('validation',750,dates_val),('test',750,dates_test)]

# Prior uncertainty band is Monte-Carlo sensitivity to simulated weather and load variation.
def compute_physics(vessel,payload,H,U,gust,period,visibility,pressure_change,rain):
    L=float(vessel['length_m']); B=float(vessel['beam_m']); mass=float(vessel['lightship_mass_kg'])+payload
    cb=float(vessel['block_coefficient_cb']); cwp=float(vessel['waterplane_coefficient_cwp'])
    additional_draft=payload/(RHO_SEA*cwp*L*B) # linearized waterplane approximation
    freeboard=max(0.05,float(vessel['freeboard_lightship_m'])-additional_draft)
    approx_draft=mass/(RHO_SEA*cb*L*B)
    cap=float(vessel['nominal_payload_limit_kg']); load_ratio=payload/cap
    lambda_deep=G*period*period/(2*math.pi) # deep-water only, bathymetry unknown
    steep=H/lambda_deep
    wind_area=L*(freeboard+.35)*.7 # proxy, not measured actual lateral projected area
    force=.5*RHO_AIR*CD*wind_area*(gust**2)
    acc_proxy=.5*H*(2*math.pi/period)**2 # linear water surface vertical acceleration amplitude (not vessel acceleration)
    # Research-specific heuristic transformations, NOT FAO/IMO approved coefficients/limits.
    s={
      'wave_length_exposure': clamp((H/L-.035)/.48),
      'wave_freeboard_exposure': clamp((H/freeboard-.30)/3.5),
      'gust_exposure': clamp((gust-4.0)/25.0),
      'wave_steepness_exposure': clamp((steep-.008)/.075),
      'payload_exposure': clamp((load_ratio-.30)/1.00),
      'wind_force_exposure': clamp((force/max(mass*G,1)-.005)/.12),
      'visibility_exposure': clamp((8-visibility)/7.5),
      'pressure_tendency_exposure': clamp((-pressure_change-1)/7),
      'rain_exposure': clamp(rain/25),
    }
    # sum = 1.00; chosen as tunable heuristic research weights, not calibrated risk probabilities
    w=dict(wave_length_exposure=.24,wave_freeboard_exposure=.14,gust_exposure=.16,
       wave_steepness_exposure=.12,payload_exposure=.10,wind_force_exposure=.07,
       visibility_exposure=.07,pressure_tendency_exposure=.06,rain_exposure=.04)
    val=100*sum(s[k]*w[k] for k in w)
    # simple conservative additive proxy for excessive nominal payload, NOT legal overload determination
    if load_ratio>1: val+=min(10.,(load_ratio-1)*25.)
    return dict(draft_added_m=additional_draft,approx_draft_m=approx_draft,freeboard_estimated_m=freeboard,
                payload_ratio=load_ratio,wave_length_m=lambda_deep,wave_steepness=steep,
                gust_lateral_force_proxy_n=force,wave_surface_accel_proxy_mps2=acc_proxy,
                exposure_scores=s,score=clamp(val,0,100))

def get_label(score):
    return 'Safe' if score<35 else ('Caution' if score<65 else 'Danger')

master=[]; hourly=[]; c_idx=0
for split,count,dates in parts:
    for _ in range(count):
        vidx=int(RNG.integers(0,N_VESSELS)); v=V[vidx]; t=v['vessel_type']; sp=TYPE_SPEC[t]
        date=pd.Timestamp(RNG.choice(dates.values)).tz_localize(None)
        departure=int(RNG.integers(3,19))
        zone=ZONES[int(RNG.integers(0,len(ZONES)))]; zid,zname,lat,lon,coast=zone
        length_h=r(*sp['hours']); duration=float(round(length_h,2))
        actual_ts=date+pd.Timedelta(hours=departure)
        trip=f'C1T{c_idx+1:05d}'; c_idx+=1
        # bimodal payload to include overload stress-testing cases with declared oversampling
        ratio=float(np.clip(RNG.beta(2.6,2.1)*1.15,.12,1.18))
        if RNG.random()<.08: ratio=r(1.00,1.26)
        payload=ratio*float(v['nominal_payload_limit_kg'])
        # seas are generated from plausible but uncalibrated distributions; not downloaded observations
        scenario=str(RNG.choice(scenarios,p=scen_prob))
        wind_mean={'calm':3.5,'moderate':7.5,'rough':12.6,'severe':19.0}[scenario]
        month=int(date.month)
        # seasonal variation is an assumption to add temporal structure, NOT a measured monsoon forecast
        if coast in ('west','south') and month in (5,6,7,8,9): wind_mean+=1.15
        if coast in ('east','north') and month in (12,1,2): wind_mean+=1.0
        wind_base=max(1.0,float(RNG.normal(wind_mean,2.25)))
        swell_base=max(.08,float(RNG.gamma(2.0,.30)))
        pressure_base=float(np.clip(RNG.normal(1010.4-.20*(wind_base-7),3.6),994,1023))
        trend=float(RNG.normal(0,.09))
        U_prev=wind_base
        per_step=[]
        for step in range(STEPS):
            lead=duration*step/(STEPS-1)
            # correlated synthetic forecast sequence (AR1), separate sea-state swell state
            U_prev=max(.4, .80*U_prev+.20*wind_base+float(RNG.normal(0,1.10)))
            gust=U_prev*float(RNG.uniform(1.13,1.38))
            h_wind=0.026*(U_prev**1.50)  # empirical-like scenario relationship: chosen, NOT source-derived hindcast
            swell=max(.03,swell_base+float(RNG.normal(0,.07)))
            H=float(np.sqrt(h_wind*h_wind+swell*swell))
            # wave period loosely derived from height and swell; enforce physically reasonable steepness
            period=max(4.0,float(4.35+2.55*math.sqrt(H)+RNG.normal(0,1.0)))
            period=max(period,math.sqrt(H*2*math.pi/(G*.082))) # constrain deep-water significant-wave steepness
            vis=float(np.clip(14-2.5*max(0,U_prev-8)/8-RNG.exponential(1.2),.35,16))
            rain=max(0,float(RNG.gamma(1.2,1.7)-2.0+max(0,U_prev-9)*.75))
            pressure=pressure_base+trend*lead+float(RNG.normal(0,.4))
            # pressure tendency in hPa per 3h, independent-ish event feature
            pressure_tendency=float(np.clip(trend*3+RNG.normal(-.09*max(0,U_prev-12),.8),-8,5))
            phys=compute_physics(v,payload,H,U_prev,gust,period,vis,pressure_tendency,rain)
            row={
                'trip_id':trip,'step_index':step,'forecast_lead_hours':round3(lead),
                'forecast_valid_utc':(actual_ts-pd.Timedelta(hours=5,minutes=30)+pd.Timedelta(hours=lead)).isoformat(),
                'wind_speed_10m_ms':round3(U_prev),'wind_gust_proxy_ms':round3(gust),
                'significant_wave_height_m':round3(H),'wave_peak_period_s':round3(period),
                'sea_level_pressure_hpa':round3(pressure),'pressure_change_3h_hpa':round3(pressure_tendency),
                'visibility_km':round3(vis),'rainfall_mm_h':round3(rain),
                'wave_length_deep_m':round3(phys['wave_length_m']),
                'wave_steepness':round(float(phys['wave_steepness']),5),
                'gust_lateral_force_proxy_n':round3(phys['gust_lateral_force_proxy_n']),
                'surface_accel_proxy_mps2':round3(phys['wave_surface_accel_proxy_mps2']),
                'instantaneous_heuristic_risk':round3(phys['score']),
                'weather_provenance':'synthetic_forecast_not_observed'}
            hourly.append(row)
            per_step.append((row,phys))
        scores=np.array([p['score'] for _,p in per_step])
        # DRI aggregates maximum + high quantile; relative weights are research assumptions.
        max_ii=int(np.argmax(scores)); worst,pp=per_step[max_ii]
        risk=clamp(.60*max(scores)+.40*np.quantile(scores,.75),0,100)
        # interval describes assumptions and perturbation sensitivity, not frequentist CI
        pert=[]
        # Faster approximated sensitivity: perturb only fixed worst and P75 exposure snapshots.
        p75_ii=int(np.argmin(np.abs(scores-np.quantile(scores,.75))))
        selected=[per_step[max_ii],per_step[p75_ii]]
        for _mc in range(16):
            vscore=[]
            sim_load=max(0,payload*float(np.clip(RNG.normal(1,.07),.80,1.22)))
            for x,_p in selected:
                sim_h=max(0.03,float(x['significant_wave_height_m'])*float(np.clip(RNG.normal(1,.13),.65,1.45)))
                sim_u=max(.2,float(x['wind_speed_10m_ms'])*float(np.clip(RNG.normal(1,.10),.7,1.35)))
                sim_g=max(sim_u,float(x['wind_gust_proxy_ms'])*float(np.clip(RNG.normal(1,.10),.7,1.35)))
                sim_p=max(3.2,float(x['wave_peak_period_s'])*float(np.clip(RNG.normal(1,.07),.75,1.25)))
                sim_p=max(sim_p,math.sqrt(sim_h*2*math.pi/(G*.092)))
                z=compute_physics(v,sim_load,sim_h,sim_u,sim_g,sim_p,
                                  float(x['visibility_km']),float(x['pressure_change_3h_hpa']),float(x['rainfall_mm_h']))
                vscore.append(z['score'])
            pert.append(.60*vscore[0]+.40*vscore[1])
        low,high=np.quantile(pert,[.05,.95]);
        phys0=compute_physics(v,payload,float(worst['significant_wave_height_m']),float(worst['wind_speed_10m_ms']),
                              float(worst['wind_gust_proxy_ms']),float(worst['wave_peak_period_s']),
                              float(worst['visibility_km']),float(worst['pressure_change_3h_hpa']),float(worst['rainfall_mm_h']))
        strengths={k:phys0['exposure_scores'][k]*weight for k,weight in {
            'wave_length_exposure':.24,'wave_freeboard_exposure':.14,'gust_exposure':.16,'wave_steepness_exposure':.12,
            'payload_exposure':.10,'wind_force_exposure':.07,'visibility_exposure':.07,
            'pressure_tendency_exposure':.06,'rain_exposure':.04}.items()}
        mainfactor=max(strengths,key=strengths.get)
        master.append({
            'trip_id':trip,'decision_timestamp_local':actual_ts.isoformat(), 'year':actual_ts.year,'month':actual_ts.month,
            'zone_id':zid,'zone_description':zname,'zone_lat':lat,'zone_lon':lon,
            'vessel_id':v['vessel_id'],'vessel_type':t,'vessel_length_m':v['length_m'],'vessel_beam_m':v['beam_m'],
            'lightship_mass_kg':v['lightship_mass_kg'],'payload_mass_kg':round3(payload),
            'total_displacement_mass_proxy_kg':round3(float(v['lightship_mass_kg'])+payload),
            'assumed_payload_limit_kg':v['nominal_payload_limit_kg'],
            'payload_limit_ratio':round3(phys0['payload_ratio']),
            'assumed_lightship_freeboard_m':v['freeboard_lightship_m'],
            'estimated_extra_draft_m':round3(phys0['draft_added_m']),
            'estimated_loaded_draft_m':round3(phys0['approx_draft_m']),
            'estimated_loaded_freeboard_m':round3(phys0['freeboard_estimated_m']),
            'planned_trip_duration_h':round3(duration),
            'forecast_window_steps':STEPS,'worst_forecast_step_index':max_ii,
            'forecast_max_wind_ms':round3(max(x['wind_speed_10m_ms'] for x,_ in per_step)),
            'forecast_max_gust_ms':round3(max(x['wind_gust_proxy_ms'] for x,_ in per_step)),
            'forecast_max_wave_height_m':round3(max(x['significant_wave_height_m'] for x,_ in per_step)),
            'forecast_min_pressure_hpa':round3(min(x['sea_level_pressure_hpa'] for x,_ in per_step)),
            'forecast_min_visibility_km':round3(min(x['visibility_km'] for x,_ in per_step)),
            'worst_wave_peak_period_s':worst['wave_peak_period_s'],
            'worst_wave_steepness':worst['wave_steepness'],
            'worst_lateral_wind_force_proxy_n':worst['gust_lateral_force_proxy_n'],
            'heuristic_dri_score':round3(risk),'sensitivity_p05_dri_score':round3(low),
            'sensitivity_p95_dri_score':round3(high),'proxy_risk_label':get_label(risk),
            'dominant_proxy_risk_factor':mainfactor,
            'scenario_sampling_stratum':scenario,'dataset_split':split,
            'label_provenance':'rule_based_synthetic_proxy_not_incident_ground_truth',
            'weather_provenance':'synthetic_forecast_not_observed',
            'vessel_provenance':'synthetic_design_not_measured',
        })

m=pd.DataFrame(master); h=pd.DataFrame(hourly)
# Output exact floating point structure and tracked provenance
m.to_csv(OUT/'C1_Master_5000_Trips.csv',index=False,float_format='%.5f')
h.to_csv(OUT/'C1_BiLSTM_Weather_60000_Steps.csv',index=False,float_format='%.5f')
reg.to_csv(OUT/'C1_Vessel_Registry_250.csv',index=False,float_format='%.5f')

# Data dictionary produced with explicit dtype/unit/provenance for ALL CSV columns
columns={}
for fname,frame in [('C1_Master_5000_Trips.csv',m),('C1_BiLSTM_Weather_60000_Steps.csv',h),('C1_Vessel_Registry_250.csv',reg)]:
    for col in frame.columns:
        units=''
        if col.endswith('_ms'): units='m/s'
        elif col.endswith('_kg'): units='kg'
        elif col.endswith('_h'): units='hours'
        elif col.endswith('_m'): units='m'
        elif col.endswith('_hpa'): units='hPa'
        elif col.endswith('_s'): units='s'
        elif col.endswith('_n'): units='N'
        elif col.endswith('_km'): units='km'
        elif col.endswith('_mm_h'): units='mm/h'
        elif col.endswith('_dri_score') or col=='instantaneous_heuristic_risk': units='0-100 heuristic index'
        dtype='number' if pd.api.types.is_numeric_dtype(frame[col]) else 'text/date'
        if col in ('proxy_risk_label','heuristic_dri_score','sensitivity_p05_dri_score','sensitivity_p95_dri_score','instantaneous_heuristic_risk'): src='heuristic_rule_based'
        elif col.startswith(('estimated_','worst_lateral_wind','worst_wave_steepness','wave_length_deep','wave_steepness','gust_lateral_force','surface_accel','payload_limit_ratio','total_displacement')): src='physics_derived_approximation'
        elif 'provenance' in col: src='provenance_metadata'
        else: src='synthetic_assumption_or_identifier'
        columns[(fname,col)]=dict(file=fname,column=col,dtype=dtype,unit=units,source_type=src)
pd.DataFrame(columns.values()).to_csv(OUT/'C1_Data_Dictionary.csv',index=False)

weights={'wave_length_exposure':.24,'wave_freeboard_exposure':.14,'gust_exposure':.16,
       'wave_steepness_exposure':.12,'payload_exposure':.10,'wind_force_exposure':.07,
       'visibility_exposure':.07,'pressure_tendency_exposure':.06,'rain_exposure':.04}
config={
 'dataset_name':'C1 Vessel-Specific Safety Physics-Constrained Synthetic Research Dataset',
 'version':'1.0.0','generated_date':'2026-10-16','seed':20261016,
 'sample_count':N,'vessel_count':N_VESSELS,'steps_per_trip':STEPS,
 'physics_constants':{'gravity_mps2':G,'seawater_density_kgm3':RHO_SEA,'air_density_kgm3':RHO_AIR,'assumed_lateral_drag_coefficient':CD},
 'sample_design':'synthetic; 2023-2025; stratified stress cases; not representative of observed climatology',
 'risk_weights_assumptions_not_official':weights,'risk_aggregation':'0.6*max(per-step score)+0.4*quantile75(per-step score)',
 'classification_cutoffs_research_assumptions':{'Safe':'<35','Caution':'35 to <65','Danger':'>=65'},
 'data_split':'train 2023-2024; validation 2025 H1; test 2025 H2; all are synthetic',
 'sources':[ 
   {'title':'FAO/ILO/IMO 2012 Fishing Vessel Safety Recommendations','url':'https://www.fao.org/4/i3108e/i3108e00.htm','role':'qualitative vessel-safety context, not numeric proxy thresholds'},
   {'title':'FAO 2009 Safety practices related to small fishing vessel stability','url':'https://www.fao.org/4/i0625e/i0625e00.htm','role':'load/freeboard/stability concepts, not numerical hull specs'},
   {'title':'NOAA NDBC significant wave height and wave steepness','url':'https://www.ndbc.noaa.gov/faq/wavecalc.shtml','role':'wave terminology, not observed data downloaded'},
   {'title':'NOAA wave relationships and deep water approximation','url':'https://www.weather.gov/media/wrh/online_publications/TMs/TM-51.pdf','role':'wave dispersion equation'},
   {'title':'OpenStax drag forces','url':'https://openstax.org/books/college-physics/pages/5-2-drag-forces','role':'generic drag force law'},
   {'title':'Sri Lanka 2024 Annual Fisheries Statistical Bulletin','url':'https://www.fisheries.gov.lk/web/images/statistics/annual_report/Annual_Fisheries_Statistical_Bulletin_2024_compressed.pdf','role':'vessel category names only; synthetic vessel specs'},
   {'title':'Open-Meteo Marine Weather API','url':'https://open-meteo.com/en/docs/marine-weather-api','role':'future real weather ingestion option, no API downloaded'},
 ],
 'provenance_notice':'ALL rows for vessels/weather/labels are synthetic and are NOT official FAO/IMO limits, measured accidents, or certified maritime safety advice.'
}
(OUT/'C1_Method_and_Provenance.json').write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding='utf-8')

# Machine-auditable tests across CSV and model join relationships
assert len(m)==5000 and len(h)==60000 and len(reg)==250
assert m.trip_id.is_unique and h.groupby('trip_id').size().eq(STEPS).all()
assert set(m.trip_id)==set(h.trip_id)
assert (m.heuristic_dri_score.between(0,100)).all()
assert (m.estimated_loaded_freeboard_m.gt(0)).all()
assert (m.estimated_loaded_draft_m.gt(0)).all()
assert (m.payload_limit_ratio.gt(0)).all()
assert h.wave_steepness.le(.082).all()
assert h.wind_gust_proxy_ms.ge(h.wind_speed_10m_ms).all()
assert m.isna().sum().sum()==0 and h.isna().sum().sum()==0 and reg.isna().sum().sum()==0
assert m.apply(lambda z:get_label(z.heuristic_dri_score)==z.proxy_risk_label,axis=1).all()
assert (m.sensitivity_p05_dri_score<=m.sensitivity_p95_dri_score).all()
assert m.dataset_split.value_counts().to_dict()=={'train':3500,'validation':750,'test':750}
# Critical numerical physics recompute on raw vessel inputs
pp=(m['payload_mass_kg']/(RHO_SEA*(m['vessel_length_m']*m['vessel_beam_m'])*m['vessel_id'].map(reg.set_index('vessel_id')['waterplane_coefficient_cwp'])))
assert np.allclose(pp,m.estimated_extra_draft_m,atol=.002)
assert m.estimated_loaded_freeboard_m.le(m.assumed_lightship_freeboard_m).all()
assert h.groupby('trip_id').step_index.nunique().eq(12).all()
assert (pd.to_datetime(m[m.dataset_split=='train'].decision_timestamp_local)<pd.Timestamp('2025-01-01')).all()
assert (pd.to_datetime(m[m.dataset_split=='validation'].decision_timestamp_local).between('2025-01-01','2025-06-30 23:59:59')).all()
assert (pd.to_datetime(m[m.dataset_split=='test'].decision_timestamp_local)>=pd.Timestamp('2025-07-01')).all()
validation={
 'master_records':len(m),'temporal_records':len(h),'vessels':len(reg),'steps_per_trip':STEPS,
 'missing_cells':int(m.isna().sum().sum()+h.isna().sum().sum()+reg.isna().sum().sum()),
 'duplicate_trip_ids':int(m.trip_id.duplicated().sum()),
 'class_count':m.proxy_risk_label.value_counts().to_dict(),
 'class_count_by_split':pd.crosstab(m.dataset_split,m.proxy_risk_label).to_dict(),
 'vessel_count_by_type':reg.vessel_type.value_counts().to_dict(),
 'scenario_count':m.scenario_sampling_stratum.value_counts().to_dict(),
 'feature_ranges':{a:{'minimum':float(m[a].min()),'maximum':float(m[a].max())} for a in [
 'heuristic_dri_score','payload_limit_ratio','estimated_loaded_freeboard_m','forecast_max_wind_ms','forecast_max_wave_height_m','planned_trip_duration_h']},
 'tests_passed':[
 'exactly_5000_trip_samples','exactly_60000_time_steps','12_forecast_steps_per_trip','250_synthetic_vessels',
 'all_trip_ids_join','no_missing_values','unique_trip_ids','valid_label_score_mapping',
 '0_to_100_scores','gust_ge_mean_wind','deepwater_steepness_le_0.082',
 'draft_load_equation_verified','chronological_split_verified','reproducible_fixed_random_seed'],
 'external_field_validation':'NOT PERFORMED: no observed vessel, weather, expert/incident risk labels',
 'model_performance':'NOT TRAINED / NOT EVALUATED', 'sensitivity_note':'16 weather/load perturbations of fixed worst & P75 snapshots per trip; screening only, not statistical confidence interval'
}
(OUT/'C1_Validation_Report.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
(OUT/'README_FIRST.txt').write_text('''C1 | VESSEL SAFETY | 5000-RECORD PHYSICS-CONSTRAINED SYNTHETIC DATASET\n\n1. C1_Master_5000_Trips.csv: 5,000 synthetic trip decisions (one row per trip).\n2. C1_BiLSTM_Weather_60000_Steps.csv: 12 simulated forecast steps for each trip.\n3. C1_Vessel_Registry_250.csv: 250 synthetic hull profiles.\n4. C1_Data_Dictionary.csv: machine-readable variables and units.\n5. C1_Method_and_Provenance.json: source links, assumptions and weights.\n6. C1_Validation_Report.json: actual tests run and distributions.\n7. generate_c1.py: reproduces every data file deterministically.\n8. C1_Dataset_Justification_Sinhala.docx: Sinhala methodological explanation.\n\nIMPORTANT: This IS NOT measured marine weather, observed accident data, validated seaworthiness certification, real hull specifications, nor a real-world risk probability.\nSafe/Caution/Danger are SYNTHETIC PROXY labels computed from transparent, uncalibrated heuristics.\nFAO/IMO sources supply qualitative context; they DO NOT endorse the numeric cutoffs or arbitrary vessel dimensions.\nArchive data are not downloaded in this build. Need official measurements and expert labels before operational adoption.\n\nBi-LSTM input: join master by trip_id to 12 ordered steps, exclude heuristic_risk/score/label/provenance/scenario and all future-unknown signals.\nFor experiment, use synthetic forecast covariates and vessel geometry/weight, train using train split, tune with validation, hold test untouched.\n''',encoding='utf-8')
print('DONE',validation)
