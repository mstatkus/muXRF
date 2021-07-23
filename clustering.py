# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 14:22:56 2021

@author: Михаил
"""
#%% init
import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle


xls_data = 'KPV_lognorm.xlsx'
xls_labels = 'table_labels.xlsx'

#%% funcs
def zmatrix(model):

    children = model.children_
    distances = model.distances_
    
    n_samples = len(model.labels_)
    n_clusters = len(children)
    
    cluster_index = list(range(n_samples,n_clusters+n_samples))
    
    z = pd.DataFrame(data=children,
                     columns = ['left','right'])
    z['cid'] = cluster_index
    z['dist'] = distances
    z.set_index(keys='cid',drop=False,inplace=True)
    z.sort_index(ascending=False,inplace=True)
    return z

def create_tree(z,data):
    
    s_template = '{:03}'
    c_template = 'C-{:03}'
    
    n_samples = len(data)
    print (n_samples)

    root_cid = z.index.tolist()[0] #max cluster id
    root_dist = z.iloc[0].dist
    
    t = Tree(name = c_template.format(root_cid),
             dist = root_dist)
    t_dict = {root_cid : t}


    for cid, row  in z.iterrows():        
        #lookup node with this cid
        node = t_dict.get(cid)
        if node: #TODO check valid node
            
            children = (int(row['left']),int(row['right']))
        
            dist = row['dist']
            
            for child in children:
                if child >= n_samples:
                    # print ('c',child)
                    name = c_template.format(child) # cluster
                else:
                    # print ('s',child)
                    name = s_template.format(data.iloc[child].name)
                
                # name = template.format(child) 
                child_node = node.add_child(name=name,
                                            dist = dist)
                child_node.cid = child
                t_dict[child] = child_node
                
                

    return t, t_dict
#%% read xls files
data = pd.read_excel(xls_data,index_col = 'id')
long_labels = pd.read_excel(xls_labels,index_col = 'id')


#%% clustering
from sklearn.cluster import AgglomerativeClustering

m = AgglomerativeClustering(n_clusters = None,
                            distance_threshold = 0,
                            linkage = 'ward',
                            compute_full_tree = True,
                            )
m.fit(data)

#%% compose zmatrix
z = zmatrix(m)
#%% create tree
t, t_dict = create_tree(z,data)

#%%
ts = TreeStyle()
ts.show_leaf_name = True
ts.mode = "c"
ts.show_scale = False



n = t_dict[71]
nst1 = NodeStyle()
nst1["bgcolor"] = "LightSteelBlue"
n.set_style(nst1)

t.show(tree_style=ts)
