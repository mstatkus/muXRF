# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 14:22:56 2021

@author: Михаил
"""
#%% init
import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle, CircleFace, TextFace


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

#%% plot tree
ts = TreeStyle()
ts.show_leaf_name = True
ts.mode = "c"
ts.show_scale = False


# =============================================================================
# n = t_dict[95]
# nst1 = NodeStyle()
# nst1["bgcolor"] = "LightSteelBlue"
# n.set_style(nst1)
# =============================================================================



colors_dict = {4  : 'Salmon',
               5  : 'Gold',
               6  : 'Plum',
               7  : 'DarkSeaGreen'}

    

styles_dict = {4 : NodeStyle(bgcolor = 'Salmon'),
              5  : NodeStyle(bgcolor = 'Gold'),
              6  : NodeStyle(bgcolor = 'Plum'),
              7  : NodeStyle(bgcolor = 'DarkSeaGreen')}

ts.legend.add_face(CircleFace(10, 'Salmon'), column=0)
ts.legend.add_face(TextFace(' Horizon 4'), column=1)
ts.legend.add_face(CircleFace(10, 'Gold'), column=0)
ts.legend.add_face(TextFace(' Horizon 5'), column=1)
ts.legend.add_face(CircleFace(10, 'Plum'), column=0)
ts.legend.add_face(TextFace(' Horizon 6'), column=1)
ts.legend.add_face(CircleFace(10, 'DarkSeaGreen'), column=0)
ts.legend.add_face(TextFace(' Horizon 7'), column=1)


root = t.get_tree_root()
for leaf in root.iter_leaves():
    label_id = int(leaf.name)
    horizon = long_labels.loc[label_id]['horizon']
    print(leaf.name, horizon)
    style = styles_dict.get(horizon)
    leaf.set_style(style)

# t.show(tree_style=ts)
# t.render('tree.png', w = 200, units = 'mm', dpi = 600,
#          tree_style = ts)