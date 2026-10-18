"""Turn C1 CSV data into leakage-controlled, time-sorted Bi-LSTM arrays."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
m=pd.read_csv(P/'C1_Master_5000_Trips.csv');w=pd.read_csv(P/'C1_BiLSTM_Weather_60000_Steps.csv')
w=w.sort_values(['trip_id','step_index']).set_index(['trip_id','step_index'])
cols_w=['wind_speed_10m_ms','wind_gust_proxy_ms','significant_wave_height_m','wave_peak_period_s',
        'sea_level_pressure_hpa','pressure_change_3h_hpa','visibility_km','rainfall_mm_h',
        'wave_steepness','gust_lateral_force_proxy_n']
cols_s=['vessel_length_m','vessel_beam_m','lightship_mass_kg','payload_mass_kg','assumed_payload_limit_kg',
        'payload_limit_ratio','estimated_loaded_freeboard_m','planned_trip_duration_h']
Xw=np.stack([w.loc[(trip,slice(None)),cols_w].to_numpy(dtype='float64') for trip in m.trip_id],axis=0)
Xs0=m[cols_s].to_numpy(dtype='float64')
Xtypes=pd.get_dummies(m.vessel_type).reindex(columns=['OFRP','IDAY','IMUL'],fill_value=False).to_numpy(dtype='float64')
Xs=np.concatenate([Xs0,Xtypes],axis=1)
tr=np.where(m.dataset_split=='train')[0];va=np.where(m.dataset_split=='validation')[0];te=np.where(m.dataset_split=='test')[0]
mu_w=Xw[tr].reshape(-1,len(cols_w)).mean(axis=0);sd_w=Xw[tr].reshape(-1,len(cols_w)).std(axis=0);sd_w[sd_w<1e-8]=1
mu_s=Xs[tr,:len(cols_s)].mean(axis=0);sd_s=Xs[tr,:len(cols_s)].std(axis=0);sd_s[sd_s<1e-8]=1
Xw=((Xw-mu_w)/sd_w).astype('float32')
Xs[:,:len(cols_s)]=(Xs[:,:len(cols_s)]-mu_s)/sd_s
Xs=Xs.astype('float32')
labels=m.proxy_risk_label.map({'Safe':0,'Caution':1,'Danger':2}).to_numpy(dtype='int64')
assert Xw.shape==(5000,12,10) and Xs.shape==(5000,11)
assert np.isfinite(Xw).all() and np.isfinite(Xs).all()
np.savez_compressed(P/'C1_BiLSTM_Model_Ready_5000.npz',weather=Xw,static=Xs,labels=labels,
                    risk_score=m.heuristic_dri_score.to_numpy(dtype='float32'),
                    train_indices=tr,validation_indices=va,test_indices=te,
                    trip_ids=m.trip_id.to_numpy(dtype='U9'))
manifest={'weather_shape':list(Xw.shape),'static_shape':list(Xs.shape),'weather_features':cols_w,
'static_features':cols_s+['type_OFRP','type_IDAY','type_IMUL'],
'label_mapping':{'Safe':0,'Caution':1,'Danger':2},'scaling':'z-score numeric features; fit train split ONLY; one-hot type left unscaled',
'chronological_split_counts':{'train':len(tr),'validation':len(va),'test':len(te)},
'weather_train_mean':mu_w.tolist(),'weather_train_std':sd_w.tolist(),
'static_train_mean':mu_s.tolist(),'static_train_std':sd_s.tolist(),
'leakage_excluded':['instantaneous_heuristic_risk','heuristic_dri_score from inputs','proxy_risk_label from inputs',
'scenario_sampling_stratum','sensitivity bounds','label provenance','date timestamp as an identifier'],
'note':'Targets are synthetic heuristic labels. Model accuracy vs these targets does not measure real maritime safety.'}
(P/'C1_BiLSTM_Feature_Manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Tensor output: ',Xw.shape,Xs.shape,'labels',np.unique(labels,return_counts=True))
