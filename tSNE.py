# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:01:36 2021

@author: Михаил
"""
import pandas as pd
from sklearn.manifold import TSNE
import time
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering



xls_data = 'KPV_lognorm.xlsx'
xls_labels = 'table_labels.xlsx'
#%% read xls files
data = pd.read_excel(xls_data,index_col = 'id')
long_labels = pd.read_excel(xls_labels,index_col = 'id')

#%% tSNE

start = time.time()

xy_tsne = TSNE(n_components=2,
         random_state = 123456).fit_transform(data)
stop = time.time()
print('tSNE OK, {} s elapsed'.format(stop-start))

tsne_df = pd.DataFrame(xy_tsne, columns = ['x','y'],
                       index = data.index)

#%% clustering
start = time.time()
agc = AgglomerativeClustering(n_clusters = 8,
                            distance_threshold = None,
                            linkage = 'ward',
                            compute_full_tree = True)
agc.fit(data)
stop = time.time()
print('clustering OK, {} s elapsed'.format(stop-start))

cluster_labels = pd.Series(agc.labels_,
                          name='cluster_labels',
                          index = data.index)

#%% construct dataframe
df = tsne_df.join([cluster_labels,long_labels.horizon])



#%%
colors_8 = {0:'tab:blue',
          1:'tab:orange',
          2:'tab:green',
          3:'tab:red',
          4:'tab:purple',
          5:'tab:brown',
          6:'tab:pink',
          7:'tab:gray'}

markers_hor = {4:'o',
                5:'v',
                6:'s',
                7:'P'}

#%%

plt.scatter(df.x, df.y)


#%%
plt.subplots(dpi=300)
gr = df.groupby('horizon')
for hor, g in gr:
    # print (g)
    m = markers_hor[hor]
    plt.scatter(g.x,g.y,c=g['cluster_labels'].map(colors_8),marker=m)

patches_1 = [ plt.plot([],[], marker="o", ls="", color=colors_8[key], 
            label="{}".format(key) )[0]  for key in colors_8.keys()]
first_legend = plt.legend(handles=patches_1, loc='lower left',title = 'Clusters')
ax = plt.gca().add_artist(first_legend)

patches_2 = [ plt.plot([],[], marker=markers_hor[key], ls="", color='black', 
            label="{}".format(key) )[0]  for key in markers_hor.keys()]
plt.legend(handles=patches_2, loc='upper right',title='Horizons')

#%%
data = data.join([cluster_labels,long_labels.horizon])
data.to_excel('data_clusters.xlsx')

#%%
g = data.groupby('cluster_labels')
gmean = g.mean()
gmean.to_excel('cluster_mean.xlsx')
