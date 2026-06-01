
from pathlib import Path
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
try:
    from IPython.display import display
except Exception:
    def display(x):
        print(x)

def _root():
    cwd=Path.cwd()
    for p in [cwd,*cwd.parents]:
        if (p/'data').exists(): return p
    return cwd

def load_dataset(name):
    p=_root()/ 'data' / name
    return pd.read_csv(p)

def quick_summary(df):
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    display(df.head())
    nums=df.select_dtypes(include='number')
    if len(nums.columns): display(nums.describe().T[['mean','std','min','max']].round(2))

def haversine(lon1,lat1,lon2,lat2):
    R=6371.0088
    lon1,lat1,lon2,lat2=map(np.radians,[lon1,lat1,lon2,lat2])
    dlon=lon2-lon1; dlat=lat2-lat1
    a=np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

def plot_points(df, lon='lon', lat='lat', color=None, title='Spatial view'):
    fig, ax = plt.subplots(figsize=(7,5))
    if color and color in df.columns:
        s=ax.scatter(df[lon], df[lat], c=df[color], s=45, alpha=.78)
        fig.colorbar(s, ax=ax, label=color)
    else:
        ax.scatter(df[lon], df[lat], s=45, alpha=.78)
    ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.set_title(title); ax.grid(True, alpha=.25)
    plt.show()

def grid_pivot(df, value='elevation_m'):
    return df.pivot_table(index='y', columns='x', values=value).sort_index(ascending=False)

def plot_grid(df, value='elevation_m', title='Raster grid'):
    arr=grid_pivot(df,value)
    fig, ax=plt.subplots(figsize=(8,5))
    im=ax.imshow(arr.values, aspect='auto')
    fig.colorbar(im, ax=ax, label=value)
    ax.set_title(title); ax.set_xlabel('grid x'); ax.set_ylabel('grid y')
    plt.show()

def nearest_join(left, right, lon='lon', lat='lat'):
    out=[]
    for _,r in left.iterrows():
        d=haversine(r[lon],r[lat],right[lon].to_numpy(),right[lat].to_numpy())
        j=int(np.argmin(d)); rr=right.iloc[j].to_dict()
        out.append({**r.to_dict(), 'nearest_id': rr.get('id', rr.get('site', rr.get('county','target'))), 'distance_km': float(d[j])})
    return pd.DataFrame(out)

def classify_quantiles(s, k=5):
    return pd.qcut(s.rank(method='first'), k, labels=[f'Q{i}' for i in range(1,k+1)])

def idw(points, value, grid_lon, grid_lat, power=2):
    vals=[]
    for lo,la in zip(grid_lon,grid_lat):
        d=haversine(lo,la,points['lon'].to_numpy(),points['lat'].to_numpy())
        d=np.maximum(d, .001); w=1/(d**power)
        vals.append(float((w*points[value].to_numpy()).sum()/w.sum()))
    return np.array(vals)

def simple_kmeans(df, cols, k=3, n_iter=20):
    X=df[cols].to_numpy(dtype=float)
    X=(X-X.mean(axis=0))/(X.std(axis=0)+1e-9)
    centers=X[np.linspace(0,len(X)-1,k,dtype=int)].copy()
    for _ in range(n_iter):
        labels=((X[:,None,:]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
        for j in range(k):
            if (labels==j).any(): centers[j]=X[labels==j].mean(axis=0)
    return labels

def morans_i(df, value, lon='lon', lat='lat', threshold_km=35):
    x=df[value].to_numpy(dtype=float); z=x-x.mean(); n=len(x); num=0.0; wsum=0.0
    for i in range(n):
        d=haversine(df.iloc[i][lon],df.iloc[i][lat],df[lon].to_numpy(),df[lat].to_numpy())
        w=((d>0)&(d<threshold_km)).astype(float)
        num += (w*z[i]*z).sum(); wsum += w.sum()
    return (n/wsum)*num/(z*z).sum() if wsum else np.nan
