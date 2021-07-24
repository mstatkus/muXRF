# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 14:22:56 2021

@author: Михаил
"""
#%% init
import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle, CircleFace, TextFace
from ete3 import faces, PieChartFace
import matplotlib.cm as cm
import matplotlib

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

horizons = list(range(4,8)) #TODO - get horizons from label list

cmap = cm.get_cmap('tab10', 10)    
hexlist = [matplotlib.colors.rgb2hex(c) for c in cmap.colors]

root = t.get_tree_root()
for leaf in root.iter_leaves():
    label_id = int(leaf.name)
    horizon = long_labels.loc[label_id]['horizon']
    leaf.horizon = horizon


#%% pie charts
cut_level = 3 #root level = 0
cmar = 5
root = t.get_tree_root()
for node in t.traverse("levelorder"):
    rdist = node.get_distance(root,topology_only=True)
    if rdist==cut_level:
        leaves = node.get_leaves()
        h_counts = dict.fromkeys(horizons,0)
        h_total = 0
        # print (leaves)
        for leaf in leaves:
            h_counts[leaf.horizon] += 1
            h_total += 1
        percents = []
        for h in sorted(h_counts):
            h_counts[h] /= (h_total/100)
            percents.append(h_counts[h])
        
        
        # print (node.name, percents)
        f = PieChartFace(percents = percents,
                         width = 50,
                         height = 50,
                         colors = hexlist,
                         line_color = 'black')
        f.margin_bottom = cmar
        f.margin_top = cmar
        f.margin_left = cmar
        f.margin_right = cmar
        
        node.add_face(f, column=0)




#%% plot tree



ts = TreeStyle()
ts.show_leaf_name = True
ts.mode = "c"
ts.show_scale = False
margins = 10

ts.margin_left = margins
ts.margin_right = margins
ts.margin_top = margins
ts.margin_bottom = margins



colors_dict = dict(zip(horizons,hexlist))

def create_colorstyle(h,colors_dict):
    c = colors_dict.get(h)
    ns = NodeStyle(bgcolor = c)
    return ns


styles_dict = {h : create_colorstyle(h,colors_dict) for h in horizons}

for h in horizons:
    ts.legend.add_face(CircleFace(10, colors_dict.get(h)), column=0)
    ts.legend.add_face(TextFace(' Horizon {}'.format(h)), column=1)



root = t.get_tree_root()
for leaf in root.iter_leaves():
    style = styles_dict.get(leaf.horizon)
    leaf.set_style(style)

# t.show(tree_style=ts)
t.render('tree.svg', w = 200, units = 'mm', dpi = 600,
          tree_style = ts)

