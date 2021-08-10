# -*- coding: utf-8 -*-
"""
Created on Sat Aug  7 15:16:48 2021

@author: Михаил
"""

#%% imports
import pandas as pd
from sklearn.manifold import TSNE
import time
import matplotlib
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering

import numpy as np
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

#%% ellipse function
def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensionl dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the stdandard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the stdandard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

#%% xls files
xls_data = 'KPV_lognorm.xlsx'
xls_labels = 'table_labels.xlsx'

data = pd.read_excel(xls_data,index_col = 'id')
long_labels = pd.read_excel(xls_labels,index_col = 'id')

start = time.time()

xy_tsne = TSNE(n_components=2,
         random_state = 123456).fit_transform(data)
stop = time.time()
print('tSNE OK, {} s elapsed'.format(stop-start))

tsne_df = pd.DataFrame(xy_tsne, columns = ['x','y'],
                       index = data.index)

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

df = tsne_df.join([cluster_labels,long_labels.horizon])

#%%
import matplotlib

cm_1 = matplotlib.cm.get_cmap('tab10')
cm_2 = matplotlib.cm.get_cmap('Pastel1')


hor_labels = list(df.horizon.unique())
hor_labels.sort()
clst_labels = list(df.cluster_labels.unique())
clst_labels.sort()

horizon_colors = {}
for i,h in enumerate(hor_labels):
    horizon_colors[h] = cm_1(i)

cluster_colors = {}
for i,h in enumerate(clst_labels):
    # print (type(i),type(h))
    cluster_colors[h] = cm_2(i)





#%% grey scatter
fig, ax = plt.subplots(dpi=300)
plt.scatter(df.x,df.y,c='black')
plt.title('tSNE scatter plot')
plt.xlabel('tSNE axis 1')
plt.ylabel('tSNE axis 2')
xlim = plt.xlim()
ylim = plt.ylim()
#%% hor colored scatter
cm_1 = matplotlib.cm.get_cmap('tab10')

plt.subplots(dpi=300)
g = df.groupby('horizon')
for hor, gr in g:
    # print (hor)
    plt.scatter(gr.x,gr.y,
                color = horizon_colors[hor])

plt.title('tSNE scatter plot')
plt.xlabel('tSNE axis 1')
plt.ylabel('tSNE axis 2')

patches = [ plt.plot([],[], marker="o", ls="", color=horizon_colors[key], 
            label="{}".format(key) )[0]  for key in horizon_colors.keys()]
legend = plt.legend(handles=patches, loc='upper right',title = 'Horizons')
plt.gca().add_artist(legend)

#%% grey scatter + color cluster ellipses
fig, ax = plt.subplots(dpi=300)
plt.scatter(df.x,df.y,c='black')
plt.title('tSNE scatter plot')
plt.xlabel('tSNE axis 1')
plt.ylabel('tSNE axis 2')
g = df.groupby('cluster_labels')
for clst, gr in g:
    confidence_ellipse(gr.x, gr.y, ax=ax,
                       edgecolor = 'black',
                       facecolor = cluster_colors[clst],
                       alpha = 0.5)
plt.xlim(xlim)
plt.ylim(ylim)

add_legend = False
if add_legend:
    patches = [ plt.plot([],[], marker="o", ls="", color=cluster_colors[key], 
                label="{}".format(key) )[0]  for key in cluster_colors.keys()]
    legend = plt.legend(handles=patches, loc='lower left',title = 'Clusters')
    plt.gca().add_artist(legend)

#%% hor colored scatter + contour cluster ellipses
fig, ax = plt.subplots(dpi=300)

g = df.groupby('horizon')
for hor, gr in g:
    print (hor)
    plt.scatter(gr.x,gr.y,
                color = horizon_colors[hor])


plt.title('tSNE scatter plot')
plt.xlabel('tSNE axis 1')
plt.ylabel('tSNE axis 2')
g = df.groupby('cluster_labels')
for clst, gr in g:
    confidence_ellipse(gr.x, gr.y, ax=ax,
                       edgecolor = 'grey')
plt.xlim(xlim)
plt.ylim(ylim)

patches = [ plt.plot([],[], marker="o", ls="", color=horizon_colors[key], 
            label="{}".format(key) )[0]  for key in horizon_colors.keys()]
legend = plt.legend(handles=patches, loc='upper right',title = 'Horizons')
plt.gca().add_artist(legend)