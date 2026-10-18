"""C2 physics-constrained SYNTHETIC benchmark. NOT real satellite/catch data.
Reproducible generator: NumPy + Python standard library; no live fetches.
"""
import csv,json,math,hashlib
from pathlib import Path
from datetime import date,timedelta
import numpy as np

O=Path(__file__).parent
SEED=20261016
rng=np.random.default_rng(SEED)
N_DAYS,N_ROWS,N_COLS=50,10,10
N=N_ROWS*N_COLS
lat_grid=np.linspace(5.22,5.76,N_ROWS)
lon_grid=np.linspace(79.78,80.77,N_COLS)
lat=np.array([lat_grid[i] for i in range(N_ROWS) for j in range(N_COLS)])
lon=np.array([lon_grid[j] for i in range(N_ROWS) for j in range(N_COLS)])
ids=[f'C2Z{k+1:03d}' for k in range(N)]
DATES=[(date(2025,1,1)+timedelta(days=i)).isoformat() for i in range(N_DAYS)]
# Demonstration harbours only; illustrative coordinate approximations, not navigational locations.
PORTS=[{'port_id':'P_GALLE','port_name':'Galle (approx.)','latitude':6.035,'longitude':80.216},
       {'port_id':'P_MIRISSA','port_name':'Mirissa (approx.)','latitude':5.949,'longitude':80.458},
       {'port_id':'P_TANGALLE','port_name':'Tangalle (approx.)','latitude':6.023,'longitude':80.797}]
# C1 centroids from the actual C1 synthetic data; these are schematic zone labels only.
C1_CENTROIDS=[('Z01',7.35,79.38),('Z02',8.42,79.28),('Z03',6.88,79.40),
('Z04',6.40,79.45),('Z05',5.75,79.95),('Z06',5.58,80.48),
('Z07',5.74,81.18),('Z08',8.65,82.10),('Z09',7.45,82.20),('Z10',9.88,80.68)]

def great_circle_km(lat1,lon1,lat2,lon2):
    a1,a2=np.radians(lat1),np.radians(lat2)
    dlat=a2-a1;dlon=np.radians(np.asarray(lon2)-np.asarray(lon1))
    a=np.sin(dlat/2)**2+np.cos(a1)*np.cos(a2)*np.sin(dlon/2)**2
    return 6371.0088*2*np.arcsin(np.sqrt(np.clip(a,0,1)))

def sigmoid(z): return 1/(1+np.exp(-np.clip(z,-40,40)))

def write_csv(name, rows, fields):
    with (O/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields, extrasaction='ignore');w.writeheader();w.writerows(rows)

def roundfloat(x,d=5):return round(float(x),d)

# 4-neighbor graph: 180 undirected links / 360 directional; weight inverse geographic distance.
EDGES=[]
for r in range(N_ROWS):
    for c in range(N_COLS):
        a=r*N_COLS+c
        for dr,dc in [(1,0),(0,1)]:
            nr,nc=r+dr,c+dc
            if nr<N_ROWS and nc<N_COLS:
                b=nr*N_COLS+nc
                distance=float(great_circle_km(lat[a],lon[a],lat[b],lon[b]))
                for s,t in [(a,b),(b,a)]:
                    EDGES.append({'source_zone_id':ids[s], 'target_zone_id':ids[t], 'distance_km':roundfloat(distance,3),
                                  'weight_inverse_distance':roundfloat(1/(1+distance),7)})
write_csv('C2_Graph_Edges_360.csv',EDGES,list(EDGES[0]))

# Southern Sri Lankan grid and C1 schematic spatial centroid correspondence.
NODES=[]
for k in range(N):
    pairs=[(str(z),float(great_circle_km(lat[k],lon[k],zlat,zlon))) for z,zlat,zlon in C1_CENTROIDS]
    closest=min(pairs,key=lambda p:p[1])
    NODES.append({'zone_id':ids[k], 'grid_row':k//N_COLS,'grid_col':k%N_COLS,
      'zone_latitude_deg':roundfloat(lat[k],5),'zone_longitude_deg':roundfloat(lon[k],5),
      'nearest_c1_centroid_id':closest[0], 'nearest_c1_centroid_km':roundfloat(closest[1],3),
      'coordinate_provenance':'synthetic_offshore_grid_not_legally_or_bathymetrically_verified'})
write_csv('C2_Zone_Registry_100.csv',NODES,list(NODES[0]))
write_csv('C2_Port_Scenarios.csv',PORTS,list(PORTS[0]))

# x east / y north coordinates from Earth-radius local tangent-plane approx.
ref_lat=np.mean(lat)
x=6371008.8*np.cos(np.deg2rad(ref_lat))*np.deg2rad(lon-np.mean(lon))
y=6371008.8*np.deg2rad(lat-np.mean(lat))
X=x.reshape(N_ROWS,N_COLS);Y=y.reshape(N_ROWS,N_COLS)
kx=2*np.pi/145000
ky=2*np.pi/105000
thermal_memory=np.zeros((N_ROWS,N_COLS))
chl_memory=np.zeros((N_ROWS,N_COLS))
SST=np.zeros((N_DAYS,N_ROWS,N_COLS));CHL=np.zeros_like(SST)
U=np.zeros_like(SST);V=np.zeros_like(SST)
DIVMAX=[]
# A = m2/s; u = - dpsi/dy; v= dpsi/dx -> analytical divergence = 0 exactly.
for t in range(N_DAYS):
    phase=0.11*t
    amp=2300 + 280*np.sin(2*np.pi*t/29)
    p=kx*X+0.14*t
    q=ky*Y-0.12*t
    ubg=0.07 + 0.035*np.cos(2*np.pi*t/24)
    vbg=0.025*np.sin(2*np.pi*t/30)
    uu=ubg-amp*ky*np.sin(p)*np.cos(q)
    vv=vbg+amp*kx*np.cos(p)*np.sin(q)
    U[t]=uu; V[t]=vv
    # ∂u/∂x and ∂v/∂y cancel algebraically for this stream function.
    deriv_u_x=-amp*ky*kx*np.cos(p)*np.cos(q)
    deriv_v_y= amp*kx*ky*np.cos(p)*np.cos(q)
    DIVMAX.append(float(np.max(np.abs(deriv_u_x+deriv_v_y))))
    nx0=-17500+8000*np.cos(2*np.pi*t/31)
    ny0= 12000+9000*np.sin(2*np.pi*t/23)
    bloom=np.exp(-((X-nx0)**2/(2*33000**2)+(Y-ny0)**2/(2*23000**2)))
    thermal_memory=0.72*thermal_memory+0.28*rng.normal(0,0.14,(N_ROWS,N_COLS))
    chl_memory=0.68*chl_memory+0.32*rng.normal(0,0.22,(N_ROWS,N_COLS))
    sst=28.18 +0.30*np.sin(2*np.pi*(t+14)/55) -0.40*bloom +0.42*np.sin(1.4*kx*X+0.045*t) \
        +0.23*np.cos(ky*Y+0.035*t)+thermal_memory
    chl=np.exp(-1.77 + 0.75*bloom +0.30*np.sin(kx*X+0.05*t) \
        +0.24*np.cos(ky*Y-0.04*t) + chl_memory)
    SST[t]=np.clip(sst,24.5,32)
    CHL[t]=np.clip(chl,0.01,5.0)

# SST-front |∇ SST| in Celsius / km, finite differences on physical x,y axes.
front=np.zeros_like(SST)
for t in range(N_DAYS):
    dsd_y,dsd_x=np.gradient(SST[t],y.reshape(N_ROWS,N_COLS)[:,0]/1000,
                                  x.reshape(N_ROWS,N_COLS)[0,:]/1000,edge_order=2)
    front[t]=np.hypot(dsd_x,dsd_y)

# Biological proxies, NOT empirical catch probabilities.
PARAM={
 'yellowfin': {'temperature_optimum_c':28.0,'temperature_sigma_c':2.2,'food_half_saturation_mg_m3':0.17,
    'score_weights':{'temp':0.42,'food':0.33,'front':0.17,'current':0.08},'synthetic_logit_intercept':-2.8,
    'synthetic_logit_gain':4.4},
 'skipjack': {'temperature_optimum_c':28.6,'temperature_sigma_c':1.8,'food_half_saturation_mg_m3':0.20,
    'score_weights':{'temp':0.37,'food':0.29,'front':0.22,'current':0.12},'synthetic_logit_intercept':-2.65,
    'synthetic_logit_gain':4.25}}
# Front feature and current encounter are bounded heuristic indices.
front_response=1-np.exp(-front/0.026)
cs=np.hypot(U,V)
current_response=np.exp(-0.5*((cs-0.22)/0.23)**2)
responses={}
for sp,pv in PARAM.items():
  temp_response=np.exp(-0.5*((SST-pv['temperature_optimum_c'])/pv['temperature_sigma_c'])**2)
  food_response=CHL/(CHL+pv['food_half_saturation_mg_m3'])
  w=pv['score_weights']
  score=w['temp']*temp_response+w['food']*food_response+w['front']*front_response+w['current']*current_response
  synthetic_probability=sigmoid(pv['synthetic_logit_intercept']+pv['synthetic_logit_gain']*score)
  responses[sp]={'temp':temp_response,'food':food_response,'score':score,'pseudo':synthetic_probability}

# Port-to-zone distance and fuel scenario. Assumptions, not measured route or fuel.
SCENARIO={'route_factor':1.15,'speed_knots':8.0,'fuel_burn_l_per_h':6.0,
 'illustrative_fuel_price_lkr_per_l':300.0,'site_fishing_hours':4.0,
 'site_idle_fuel_lph':2.0,'site_current_sensitivity_lph_per_ms':8.0,
 'earth_radius_km':6371.0088,
 'one_nautical_mile_km':1.852}
DIST={p['port_id']:great_circle_km(p['latitude'],p['longitude'],lat,lon) for p in PORTS}
# primary scenario Galle; dynamically recompute for other port / boat in recommendations.
primary='P_GALLE'
primary_km=DIST[primary]*SCENARIO['route_factor']
roundtrip_km=2*primary_km
travel_h=roundtrip_km/(SCENARIO['speed_knots']*1.852)
transit_fuel_l=travel_h*SCENARIO['fuel_burn_l_per_h']
site_fuel_l=SCENARIO['site_fishing_hours']*(SCENARIO['site_idle_fuel_lph']+SCENARIO['site_current_sensitivity_lph_per_ms']*cs)
# Fuel cost varies with daily ocean-current scenario (station-keeping operational load).
price_lkr=(transit_fuel_l[None,:]+site_fuel_l.reshape(N_DAYS,N))*SCENARIO['illustrative_fuel_price_lkr_per_l']

# Next-day target 7-day history. Chronological split, 43 target days Jan 8 through Feb 19.
SPLIT=['context_only' if t<=6 else ('train' if t<=35 else 'validation' if t<=42 else 'test') for t in range(N_DAYS)]
# train 29 days (t=7..35), validation 7 (36..42), test 7 (43..49).
ROWS=[]
for t in range(N_DAYS):
  for k in range(N):
    i,j=divmod(k,N_COLS)
    rec={'record_id':f'C2R{t*N+k+1:05d}', 'date_utc':DATES[t], 'zone_id':ids[k],
      'zone_latitude_deg':roundfloat(lat[k],5),'zone_longitude_deg':roundfloat(lon[k],5),
      'c1_nearest_centroid_id':NODES[k]['nearest_c1_centroid_id'],
      'sst_c':roundfloat(SST[t,i,j],5),'chlorophyll_a_mg_m3':roundfloat(CHL[t,i,j],6),
      'ocean_current_u_ms':roundfloat(U[t,i,j],6),'ocean_current_v_ms':roundfloat(V[t,i,j],6),
      'ocean_current_speed_ms':roundfloat(cs[t,i,j],6),
      'sst_front_gradient_c_per_km':roundfloat(front[t,i,j],7),
      'yft_temperature_response':roundfloat(responses['yellowfin']['temp'][t,i,j],6),
      'yft_food_response':roundfloat(responses['yellowfin']['food'][t,i,j],6),
      'yft_habitat_suitability_index':roundfloat(responses['yellowfin']['score'][t,i,j],6),
      'yft_synthetic_uncalibrated_probability':roundfloat(responses['yellowfin']['pseudo'][t,i,j],6),
      'skipjack_temperature_response':roundfloat(responses['skipjack']['temp'][t,i,j],6),
      'skipjack_food_response':roundfloat(responses['skipjack']['food'][t,i,j],6),
      'skipjack_habitat_suitability_index':roundfloat(responses['skipjack']['score'][t,i,j],6),
      'skipjack_synthetic_uncalibrated_probability':roundfloat(responses['skipjack']['pseudo'][t,i,j],6),
      'galle_great_circle_km':roundfloat(DIST['P_GALLE'][k],4),
      'mirissa_great_circle_km':roundfloat(DIST['P_MIRISSA'][k],4),
      'tangalle_great_circle_km':roundfloat(DIST['P_TANGALLE'][k],4),
      'galle_estimated_oneway_route_km':roundfloat(primary_km[k],4),
      'galle_roundtrip_km':roundfloat(roundtrip_km[k],4),
      'galle_travel_time_h':roundfloat(travel_h[k],4),
      'galle_scenario_transit_fuel_l':roundfloat(transit_fuel_l[k],4),
      'galle_scenario_site_fuel_l':roundfloat(site_fuel_l[t,i,j],4),
      'galle_scenario_fuel_l':roundfloat(transit_fuel_l[k]+site_fuel_l[t,i,j],4),
      'galle_scenario_fuel_cost_lkr':roundfloat(price_lkr[t,k],2),
      'time_split':SPLIT[t],
      'environment_provenance':'SYNTHETIC_smooth_spatiotemporal_scenarios',
      'catch_label_provenance':'SYNTHETIC_BIOLOGICAL_HEURISTIC_NO_OBSERVED_CATCH',
      'navigation_status':'SIMULATION_ONLY_NOT_FOR_REAL_NAVIGATION'}
    ROWS.append(rec)
write_csv('C2_Master_5000_ZoneDays.csv',ROWS,list(ROWS[0]))

# Feature tensor: [time,nodes,features]. Only observable environmental data.
F=np.stack([SST,CHL,U,V,front],axis=-1).reshape(N_DAYS,N,5).astype(np.float32)
Yscore=np.stack([responses['yellowfin']['score'],responses['skipjack']['score']],axis=-1).reshape(N_DAYS,N,2).astype(np.float32)
Ypseudo=np.stack([responses['yellowfin']['pseudo'],responses['skipjack']['pseudo']],axis=-1).reshape(N_DAYS,N,2).astype(np.float32)
# 7-day history t..t+6 -> prediction t+7; 43 examples.
X_raw=np.stack([F[t-7:t] for t in range(7,N_DAYS)],axis=0)
y_score=np.stack([Yscore[t] for t in range(7,N_DAYS)],axis=0)
y_pseudo=np.stack([Ypseudo[t] for t in range(7,N_DAYS)],axis=0)
labels=[SPLIT[t] for t in range(7,N_DAYS)]
train_indices=np.where(np.array(labels)=='train')[0]
val_indices=np.where(np.array(labels)=='validation')[0]
test_indices=np.where(np.array(labels)=='test')[0]
trainonly=X_raw[train_indices]
means=trainonly.mean(axis=(0,1,2))
stds=trainonly.std(axis=(0,1,2))
stds=np.maximum(stds,1e-6)
X_std=(X_raw-means[None,None,None,:])/stds[None,None,None,:]
Adj=np.eye(N,dtype=np.float32)
idx={name:k for k,name in enumerate(ids)}
for edge in EDGES:
   a,b=idx[edge['source_zone_id']],idx[edge['target_zone_id']]
   Adj[a,b]=float(edge['weight_inverse_distance'])
Adj=Adj/Adj.sum(axis=1,keepdims=True)
np.savez_compressed(O/'C2_STGCN_Model_Ready_43_Windows.npz',
  X=X_std.astype('float32'), y_suitability=y_score,y_pseudo_probability=y_pseudo,
  normalized_adjacency=Adj, train_indices=train_indices,val_indices=val_indices,
  test_indices=test_indices,feature_mean_train=means,feature_std_train=stds,
  node_ids=np.array(ids),target_dates=np.array(DATES[7:]),
  input_feature_names=np.array(['sst_c','chlorophyll_a_mg_m3','ocean_current_u_ms',
   'ocean_current_v_ms','sst_front_gradient_c_per_km']),
  target_species=np.array(['yellowfin','skipjack']))

# Non-dominated Pareto per trip scenario, WITHOUT arbitrary weighted ordering.
def pareto(candidates):
  result=[]
  for a in candidates:
    dominated=False
    for b in candidates:
      if a is b:continue
      if (b['suitability']>=a['suitability'] and b['oneway_km']<=a['oneway_km'] and
          b['fuel_lkr']<=a['fuel_lkr'] and (b['suitability']>a['suitability'] or
          b['oneway_km']<a['oneway_km'] or b['fuel_lkr']<a['fuel_lkr'])):
        dominated=True;break
    if not dominated: result.append(a)
  return result

RECS=[]
for species in ('yellowfin','skipjack'):
  for port in PORTS:
    pk=port['port_id']; d=DIST[pk]*SCENARIO['route_factor']
    candidate=[]
    for k in range(N):
      s=float(responses[species]['score'][-1,k//N_COLS,k%N_COLS]);dist=float(d[k]);
      cost=(2*dist/(SCENARIO['speed_knots']*1.852)*SCENARIO['fuel_burn_l_per_h']
            +float(site_fuel_l[-1,k//N_COLS,k%N_COLS]))*SCENARIO['illustrative_fuel_price_lkr_per_l']
      candidate.append({'scenario_date_utc':DATES[-1],'species':species,'port_id':pk,'zone_id':ids[k],
        'zone_latitude_deg':roundfloat(lat[k],5),'zone_longitude_deg':roundfloat(lon[k],5),
        'suitability':s,'oneway_km':dist,'fuel_lkr':cost})
    nd=pareto(candidate)
    for c in sorted(nd,key=lambda a:a['oneway_km']):
      RECS.append({'date_utc':c['scenario_date_utc'], 'target_species':species,'port_id':pk,
       'pareto_zone_id':c['zone_id'],'latitude':c['zone_latitude_deg'],'longitude':c['zone_longitude_deg'],
       'synthetic_habitat_suitability_index':roundfloat(c['suitability'],6),
       'assumed_route_oneway_km':roundfloat(c['oneway_km'],3),
       'assumed_fuel_cost_lkr':roundfloat(c['fuel_lkr'],2),
       'c1_safety_gate':'NOT_ASSESSED','c4_fuel_gate':'NOT_ASSESSED',
       'research_status':'NON_DOMINATED_SCENARIO_ONLY_NOT_SAFE_TO_NAVIGATE'})
write_csv('C2_Pareto_Example_Recommendations.csv',RECS,list(RECS[0]))

# leave-one-step persistence baseline evaluated on time-held-out targets; synthetic performance only.
Yprev=np.stack([Yscore[t-1] for t in range(7,N_DAYS)],axis=0)
TEST_METRICS={}
for k,species in enumerate(('yellowfin','skipjack')):
    truth=y_score[test_indices,:,k];pred=Yprev[test_indices,:,k]
    TEST_METRICS[species]={'persistence_baseline_test_MAE':roundfloat(np.abs(truth-pred).mean(),7),
      'persistence_baseline_test_RMSE':roundfloat(np.sqrt(((truth-pred)**2).mean()),7)}

# Independent numeric validations on unrounded double-precision arrays and rounded CSV rows.
check={}
check['exact_5000_master_rows']=len(ROWS)==5000
check['exact_100_unique_spatial_nodes']=len(set(ids))==100
check['exact_50_unique_dates']=len(set(DATES))==50
check['full_spatiotemporal_cartesian_product']=len(set((r['date_utc'],r['zone_id']) for r in ROWS))==5000
check['360_directional_four_neighbor_edges']=len(EDGES)==360
check['edge_bidirectionality']=all((e['target_zone_id'],e['source_zone_id']) in {(v['source_zone_id'],v['target_zone_id']) for v in EDGES} for e in EDGES)
check['physical_current_divergence_exact']=max(DIVMAX)<1e-12
check['chlorophyll_strictly_positive']=bool(np.all(CHL>0))
check['sst_physical_scenario_range']=bool(np.all((SST>=24.5)&(SST<=32)))
check['current_speed_nonnegative']=bool(np.all(cs>=0))
check['sst_front_nonnegative_finite']=bool(np.all(np.isfinite(front)) and np.all(front>=0))
check['habitat_index_yft_in_unit_interval']=bool(np.all((Yscore[:,:,0]>=0)&(Yscore[:,:,0]<=1)))
check['habitat_index_skipjack_in_unit_interval']=bool(np.all((Yscore[:,:,1]>=0)&(Yscore[:,:,1]<=1)))
check['synthetic_probability_yft_in_unit_interval']=bool(np.all((Ypseudo[:,:,0]>=0)&(Ypseudo[:,:,0]<=1)))
check['synthetic_probability_skipjack_in_unit_interval']=bool(np.all((Ypseudo[:,:,1]>=0)&(Ypseudo[:,:,1]<=1)))
check['all_galle_distances_positive']=bool(np.all(DIST[primary]>0))
check['distance_roundtrip_formula']=bool(np.allclose(roundtrip_km,2*DIST[primary]*SCENARIO['route_factor']))
check['fuel_cost_formula']=bool(np.allclose(price_lkr,(transit_fuel_l[None,:]+site_fuel_l.reshape(N_DAYS,N))*SCENARIO['illustrative_fuel_price_lkr_per_l']))
check['proper_knots_to_kmh_conversion']=abs(8*1.852-14.816)<1e-12
check['time_split_counts_29_7_7']=len(train_indices)==29 and len(val_indices)==7 and len(test_indices)==7
check['target_date_no_overlap']=len(set(DATES[7:][a] for a in train_indices)&set(DATES[7:][a] for a in test_indices))==0
check['tensor_X_shape_43_7_100_5']=X_raw.shape==(43,7,100,5)
check['tensor_y_shape_43_100_2']=y_score.shape==(43,100,2)
check['train_only_standardization']=bool(np.allclose(X_std[train_indices].mean(axis=(0,1,2)),0,atol=1e-3))
check['adjacency_row_stochastic']=bool(np.allclose(Adj.sum(axis=1),1,atol=1e-5))
check['unique_grid_id_per_row']=len(NODES)==100 and len(set(n['zone_id'] for n in NODES))==100
# robust independent check via matching IDs, not dict-equality that can alias floating points
rec_set={(r['target_species'],r['port_id'],r['pareto_zone_id']) for r in RECS}
for species in ('yellowfin','skipjack'):
  for port in PORTS:
    pk=port['port_id'];d=DIST[pk]*SCENARIO['route_factor'];C=[]
    for k in range(N):
      C.append({'zone_id':ids[k], 'suitability':float(responses[species]['score'][-1,k//10,k%10]),
        'oneway_km':float(d[k]),'fuel_lkr':float((2*d[k]/(8*1.852)*6+site_fuel_l[-1,k//10,k%10])*300)})
    expected={(species,pk,r['zone_id']) for r in pareto(C)}
    check[f'pareto_matches_{species}_{pk}']=expected=={v for v in rec_set if v[0]==species and v[1]==pk}
check['no_na_or_inf_features']=bool(np.all(np.isfinite(F)))
check['csv_rounded_values_valid']=all(float(r['chlorophyll_a_mg_m3'])>0 and 0<=float(r['yft_habitat_suitability_index'])<=1 for r in ROWS)
check['synthetic_status_every_row']=all('SYNTHETIC' in r['catch_label_provenance'] and r['navigation_status'].startswith('SIMULATION') for r in ROWS)
check['nonnegative_transit_and_site_fuel']=bool(np.all(transit_fuel_l>0) and np.all(site_fuel_l>0))
check['cost_not_strictly_distance_redundant']=bool(np.ptp((price_lkr[-1,:]/primary_km))>1.0)
check['front_uses_physical_km']=bool(np.max(front)<0.2)
check['species_scores_not_identical']=bool(np.mean(np.abs(Yscore[:,:,0]-Yscore[:,:,1]))>0.001)
# do not let QA claim external empirical validation
assert all(check.values()),{k:v for k,v in check.items() if not v}

REFERENCE=[
 {'id':'SRC01','organization':'Copernicus Marine','title':'Global Ocean Physics Analysis and Forecast','url':'https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description','usage':'variable concepts SST, east/north current; no downloaded values'},
 {'id':'SRC02','organization':'Copernicus Marine','title':'Global Ocean Colour L4 product','url':'https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/services','usage':'daily chlorophyll-a observational replacement source; not accessed'},
 {'id':'SRC03','organization':'NASA','title':'MODIS Chlorophyll-a Concentration','url':'https://modis.gsfc.nasa.gov/data/dataprod/chlor_a.php','usage':'chlorophyll-a variable definition and units; not downloaded'},
 {'id':'SRC04','organization':'NOAA Fisheries','title':'Pacific Yellowfin Tuna','url':'https://www.fisheries.noaa.gov/species/pacific-yellowfin-tuna','usage':'yellowfin temperature-related habitat background; coefficients illustrative'},
 {'id':'SRC05','organization':'FAO','title':'Resources fishing and biology of tropical tunas','url':'https://www.fao.org/4/t0081e/T0081E18.htm','usage':'skipjack regional temperature variability; coefficients illustrative'},
 {'id':'SRC06','organization':'PubMed','title':'Multiple ocean parameter-based potential fishing zone generation and validation in Western Bay of Bengal','url':'https://pubmed.ncbi.nlm.nih.gov/38153544/','usage':'evidence fronts/chlorophyll and need actual CPUE validation'},
 {'id':'SRC07','organization':'IEEE','title':'Deb et al., NSGA-II, 2002','url':'https://doi.org/10.1109/4235.996017','usage':'Pareto multiple objective conceptual basis'},
 {'id':'SRC08','organization':'IHO','title':'Nautical mile definition','url':'https://registry.iho.int/fdd/view5.do?idx=824&type=5&valueType=0','usage':'1 nautical mile exactly 1852 meters'},
 {'id':'SRC09','organization':'NOAA Fisheries','title':'Atlantic Skipjack Tuna','url':'https://www.fisheries.noaa.gov/species/atlantic-skipjack-tuna','usage':'skipjack affinity for convergence/upwelling habitats'}]

MANIFEST={'dataset_title':'C2 Southern Sri Lanka synthetic spatial fishing habitat and Pareto benchmark',
 'release':'1.0-prototype','creation_date':'2026-10-16',
 'very_important':'NO OBSERVED SATELLITE VALUES, CATCH EVENTS, OR VALIDATED CATCH PROBABILITIES IN THE CSV. DO NOT REPRESENT SYNTHETIC SCORES AS FIELD PERFORMANCE OR USE FOR NAVIGATION.',
 'data_type':'synthetic scenario data with physically consistent streamfunction current and unit-consistent cost calculations',
 'actual_satellite_values_downloaded':False,'observed_catch_records':0,
 'latitude_range':[float(min(lat)),float(max(lat))], 'longitude_range':[float(min(lon)),float(max(lon))],
 'start_date':DATES[0],'end_date':DATES[-1],'records':len(ROWS),
 'zone_nodes':len(NODES),'days':N_DAYS,'graph_directed_edges':len(EDGES),
 'species':['yellowfin','skipjack'],'biological_model':'Gaussian temperature suitability + saturating chlorophyll response + fronts + currents, parameter values illustrative and uncalibrated',
 'streamfunction':{'psi_m2_per_s':'A(t)*sin(kx*x+0.14*t)*sin(ky*y-0.12*t)',
 'u_ms':'u_bg(t) - dpsi/dy','v_ms':'v_bg(t) + dpsi/dx','divergence_analytical':0,
 'kx_rad_per_m':kx,'ky_rad_per_m':ky,'A_m2_per_s_range':[2020,2580]},
 'physics_and_cost_scenario':SCENARIO,'species_parameters_are_assumptions_not_established_thresholds':PARAM,
 'heat_front_scale_c_per_km':0.026,'current_optimum_ms':0.22,'current_sigma_ms':0.23,
 'input_tensor_shape':list(X_raw.shape),'target_tensor_shape':list(y_score.shape),
 'split_note':'Next-day target in 43 windows with 7-day history; chronological train 29, validation 7, test 7; normalize on train only; same spatial nodes on all dates',
 'integration_note':'C1 nearest centroid only, not a shared validated operational safety gate. C4 must recompute fuel for vessel before any trip.',
 'known_limitations':['No empirical CPUE/catch labels','No real Copernicus/NASA observations yet','No calibrated biological coefficients',
  'No legal maritime boundary/land/bathymetry/geofencing validation',
  'Ports approximate, route line surrogate only, not navigable waypoints',
  'Fuel on-site/current coefficients assumed, not experimentally fitted',
  'No adverse-weather, hazards, prohibited areas, gear type or boat licensing filters',
  'Only 50 synthetic days; test metrics reflect simulator, not true ecological skill'],
 'references':REFERENCE}
(O/'C2_Method_Provenance_and_Parameters.json').write_text(json.dumps(MANIFEST,indent=2,ensure_ascii=False),encoding='utf-8')
REPORT={'version':'1.0-prototype','records':len(ROWS),'date_count':N_DAYS,'nodes':N,
  'graph_edges':len(EDGES),'train_days':29,'validation_days':7,'test_days':7,
  'QA_passed':sum(check.values()),'QA_total':len(check),'QA_checks':check,'baseline_metrics':TEST_METRICS,
  'summary':{'sst_c_min_max':[roundfloat(SST.min(),3),roundfloat(SST.max(),3)],
  'chl_mg_m3_min_max':[roundfloat(CHL.min(),3),roundfloat(CHL.max(),3)],
  'current_ms_min_max':[roundfloat(cs.min(),3),roundfloat(cs.max(),3)],
  'front_c_per_km_min_max':[roundfloat(front.min(),5),roundfloat(front.max(),5)],
  'yft_suitability_min_max':[roundfloat(Yscore[:,:,0].min(),3),roundfloat(Yscore[:,:,0].max(),3)],
  'skipjack_suitability_min_max':[roundfloat(Yscore[:,:,1].min(),3),roundfloat(Yscore[:,:,1].max(),3)],
  'galle_oneway_km_min_max':[roundfloat(primary_km.min(),1),roundfloat(primary_km.max(),1)],
  'galle_fuel_cost_lkr_min_max':[roundfloat(price_lkr.min(),0),roundfloat(price_lkr.max(),0)]},
  'warning':'All QA checks are internal mathematical/computational validations, NOT empirical catch accuracy or sea-navigation validation.'}
(O/'C2_Independent_QA_and_Baseline.json').write_text(json.dumps(REPORT,indent=2),encoding='utf-8')
# Glossary for every field
DESCRIPTIONS={
 'record_id':('Unique spatial-day record key','synthetic','id'),
 'date_utc':('Simulation day, not actual observation time','synthetic','date'),
 'zone_id':('Synthetic 10x10 zone identifier','synthetic','id'),
 'c1_nearest_centroid_id':('Nearest C1 schematic zone centroid; spatial crosswalk only','calculated','id'),
 'sst_c':('Synthetic sea surface temperature','synthetic','degC'),
 'chlorophyll_a_mg_m3':('Synthetic chlorophyll-a pigment concentration','synthetic','mg/m3'),
 'ocean_current_u_ms':('East current, streamfunction derivative','physics_scenario','m/s'),
 'ocean_current_v_ms':('North current, streamfunction derivative','physics_scenario','m/s'),
 'ocean_current_speed_ms':('Hypotenuse of horizontal current vector','calculated','m/s'),
 'sst_front_gradient_c_per_km':('Central-difference SST horizontal gradient magnitude','calculated','degC/km'),
 'yft_habitat_suitability_index':('Uncalibrated yellowfin ecological proxy, 0-1, NOT catch probability','heuristic','unitless'),
 'skipjack_habitat_suitability_index':('Uncalibrated skipjack ecological proxy, 0-1, NOT catch probability','heuristic','unitless'),
 'yft_synthetic_uncalibrated_probability':('Synthetic sigmoid rescaling, NOT empirical probability','heuristic','unitless'),
 'skipjack_synthetic_uncalibrated_probability':('Synthetic sigmoid rescaling, NOT empirical probability','heuristic','unitless'),
 'galle_great_circle_km':('Great-circle straight-line distance, no marine routing or hazards','calculated','km'),
 'mirissa_great_circle_km':('Great-circle straight-line distance','calculated','km'),
 'tangalle_great_circle_km':('Great-circle straight-line distance','calculated','km'),
 'galle_estimated_oneway_route_km':('Great-circle x assumed 1.15 route factor','scenario','km'),
 'galle_roundtrip_km':('2 times oneway route proxy','scenario','km'),
 'galle_travel_time_h':('Roundtrip / assumed ground speed','scenario','hours'),
 'galle_scenario_transit_fuel_l':('Transit hours x assumed 6 liters/hour','scenario','liter'),
 'galle_scenario_site_fuel_l':('Four assumed on-site hours times idle+current sensitivity','scenario','liter'),
 'galle_scenario_fuel_l':('Transit fuel plus assumed on-site fuel; C4 replaces','scenario','liter'),
 'galle_scenario_fuel_cost_lkr':('Fuel liters x assumed LKR 300/liter; NOT retail market quote','scenario','LKR'),
 'time_split':('context_only/train/validation/test chronological split','calculated','category'),
 'catch_label_provenance':('Distinguishes synthetic rule target from actual catch data','provenance','category')}
DICT=[]
for key,value in ROWS[0].items():
    d=DESCRIPTIONS.get(key)
    if d is None:
        if key.startswith('yft_') or key.startswith('skipjack_'): d=('Heuristic species response term','heuristic','0..1')
        elif key in ['zone_latitude_deg','zone_longitude_deg']:d=('Synthetic offshore grid coordinate, NOT safe/legal coordinate','synthetic','WGS84 decimal degree')
        else:d=('Explicit scenario or provenance field','scenario','text')
    DICT.append({'column_name':key,'meaning':d[0],'source_class':d[1],'unit':d[2]})
write_csv('C2_Data_Dictionary.csv',DICT,list(DICT[0]))

readme='''# Component 2 | ST-GCN Fishing Habitat Proxy Dataset\n\n**SYNTHETIC PROTOTYPE / NOT FIELD-VALIDATED / NOT FOR MARINE NAVIGATION**\n\nMain file: `C2_Master_5000_ZoneDays.csv` (100 synthetic zones x 50 consecutive dates = 5,000).\nThe *scores* and synthetic pseudo-probabilities **DO NOT measure real probability of catching fish**.\n\nFiles:\n- `C2_Master_5000_ZoneDays.csv`: exactly 5,000 spatial-day rows, yellowfin and skipjack surrogate suitability.\n- `C2_Zone_Registry_100.csv`: stable zone coordinates and spatial C1 crosswalk.\n- `C2_Graph_Edges_360.csv`: directed 4-neighbour adjacency edge list.\n- `C2_Port_Scenarios.csv`: demonstration departure ports, approximate coordinates.\n- `C2_STGCN_Model_Ready_43_Windows.npz`: X [43,7,100,5], targets [43,100,2], adjacency [100,100]; 29/7/7 target-date split.\n- `C2_Pareto_Example_Recommendations.csv`: exact non-dominated zone sets for two species/three port scenarios on final day; NOT navigational recommendations.\n- `C2_Method_Provenance_and_Parameters.json`: explicit model, physics, coefficients, citations, data limitations.\n- `C2_Independent_QA_and_Baseline.json`: deterministic QA and next-day persistence baseline; not field validation.\n- `C2_Data_Dictionary.csv`: all field definitions.\n- `generate_c2.py`: reproducible generator, use Python + NumPy; `python generate_c2.py`.\n- `C2_Dataset_Justification_Sinhala.docx`: in-depth Sinhala report.\n\nSatellite sources are documented as **sources to fetch in a next empirical phase**, not present in the synthetic CSV. The biological suitability coefficients, speed, route factor, consumption and fuel price are educational assumptions, NOT scientifically fitted values. Google Earth/coastline/bathymetry/EEZ restriction and safety constraints have not been checked.\n\nDeployment gates: join C1 actual safety risk (weather-vessel), collect legally cleared fishing areas and port coordinates, integrate C4 vessel-calibrated fuel model, and empirically train/calibrate labels against catch+effort logbooks (CPUE).\n'''
(O/'README_FIRST.md').write_text(readme,encoding='utf-8')
print('OK:',len(ROWS),'records;',len(EDGES),'edges;',len(RECS),'pareto options;',len(check),'QA checks', 'all passed')
print('summary',REPORT['summary'])
print('baseline',TEST_METRICS)
print('first row', {k:ROWS[0][k] for k in ['record_id','date_utc','zone_id','sst_c','chlorophyll_a_mg_m3','yft_habitat_suitability_index','galle_scenario_fuel_cost_lkr']})
