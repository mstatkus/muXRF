# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 21:41:41 2021

@author: Михаил
"""
#%% init 
import hyperspy.api as hs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm


#%% load
# list of macro elements for ochre plates
# macro_element_list = ['Al','Si', 'K', 'Ca', 'Ti', 'Mn', 'Fe']
macro_element_list = ['K', 'Ca', 'Ti', 'Mn', 'Fe']
replace_element_list = True

bcf_file ='PLT-1-D.bcf'

bcf = hs.load(bcf_file)
hmap = bcf[4]
hmap.metadata.Acquisition_instrument.SEM.beam_energy=80

if replace_element_list:
    print ('Replacing original elements with custom list...',end='')
   
    hmap.set_elements([]) #TODO - check whether clearing is necessary
    hmap.set_lines([])
    
    hmap.set_elements(macro_element_list)
    hmap.add_lines()
    print ('done.')

im = hmap.get_lines_intensity()

im_elements_list = []
for m in im:
    elt = m.metadata.Sample.elements[0]
    im_elements_list.append(elt)

#%% prepare stack
signal = hs.stack(im, stack_metadata = False)
signal.axes_manager[2].name='elements'
signal.axes_manager[2].navigate=False


#%% clustering
# for n_clusters in range(2,10):
n_clusters = 8
signal.cluster_analysis(cluster_source = 'signal',
                        n_clusters=n_clusters,
                        algorithm = 'kmeans',
                        preprocessing = 'standard')

clab = signal.get_cluster_labels()
smean = signal.get_cluster_signals(signal="mean")

clusters = []

for cluster_label, cluster_signal in zip (clab.data, smean.data):
    sum_signal = np.sum(cluster_signal)
    cluster = {'cluster_label'  : cluster_label,
               'cluster_signal' : cluster_signal,
               'sum_signal'     : sum_signal}
    clusters.append(cluster)

from operator import itemgetter
clusters_sorted = sorted(clusters, key=itemgetter('sum_signal')) 


phases = np.zeros(shape = np.shape(clab.data[0]))

for i, c in enumerate(clusters_sorted):
    phases += c['cluster_label'].astype(int)*(i)


cmap = cm.get_cmap('tab10')
bounds = np.arange(-0.5,n_clusters,1.)
norm = colors.BoundaryNorm(boundaries=bounds,
                           ncolors=n_clusters)

plt.imshow(phases,cmap=cmap,
           interpolation='none',
           norm=norm)
plt.title('6 elts, clusters: {}'.format(n_clusters))
plt.colorbar(ticks = range(n_clusters))
plt.savefig('6elts_{}_phases.png'.format(n_clusters),dpi=300)
plt.close()

# cluster signals


for i, c in enumerate(clusters_sorted):
    p = c['cluster_signal']
    xmax = len(p)
    plt.plot(p,label=str(i),color=cmap(i))
    plt.legend()
    plt.xticks(range(xmax),im_elements_list)
plt.savefig('signals_{}_phases.png'.format(n_clusters),dpi=300)
plt.close()


