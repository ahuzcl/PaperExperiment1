# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 19:54:42 2017
#BGLL top 200
@author: zcl
"""
# -*- coding: UTF-8 -*-
import networkx as nx
import time
import random

def calculateQ(IN, TOT, m):
    Q =IN/m-((TOT/(2*m))**2)
    return Q



def phases_one(G):
    ##用来存社区编号和其节点
    community_dict={}
    ##用来存节点所对应的社区编号
    community_node_in_dict={}
    ##用来保存边两头节点所在社区
    edge_dict={}
    ##存Tot和In
    Tot={}
    In={}

    ##初始化上述指标
    for node in G.nodes():
        community_dict[node]=[node]
        community_node_in_dict[node]=node
        #初始化Tot
        T=0.
        for nbrs in G.neighbors(node):
            if node==nbrs:
                T += (2*G.get_edge_data(nbrs, node).values()[0])
            else:
                T+=G.get_edge_data(nbrs,node).values()[0]
        Tot[node]=T
        #初始化In
        if G.get_edge_data(node,node)==None:
            In[node]=0.
        else:
            In[node]=G.get_edge_data(node,node).values()[0]

    #初始化M
    M=0.0
    for edge in G.edges():
        M+=G.get_edge_data(*edge).values()[0]
        edge_dict[(edge[0],edge[1])]=(community_node_in_dict[edge[0]],community_node_in_dict[edge[1]])
    index=True
    ##一直遍历直到收敛
    while index==True:
        index=False
        ##遍历所有节点
        for node in G.nodes():
            ##保存节点之前所在社区
            old_community=community_node_in_dict[node]
            # 用来保存节点node的总权值
            ki = 0
            # 保存其所有邻居社区
            nbrs_community={}
            # 保存该节点移动到某社区所带来的In增益
            kiin_dict={}
            # 保存其离开自己所在社区的的In减少量
            kiout=0.
            # 目标社区
            max_community=-1
            max_detaQ=-1
            max_nbrs=-1
            # 临时保存edge_dict变化
            edge_dict_tmp={}
            for nbrs in G.neighbors(node):
                weight=G.get_edge_data(node,nbrs).values()[0]
                if nbrs==node:
                    ki+=(2*weight)
                else:
                    ki+=weight
                current_community=community_node_in_dict[nbrs]
                if current_community==old_community:
                    kiout+=weight
                    continue

                if nbrs_community.has_key(current_community):
                    kiin_dict[current_community]+=weight
                else :
                    nbrs_community[current_community]=current_community
                    kiin_dict[current_community]=weight
                    if G.has_edge(node, node):
                        kiin_dict[current_community] += G.get_edge_data(node, node).values()[0]
            #计算它离开自己社区的detaQ
            detaQ1=calculateQ(In[old_community]-kiout,Tot[old_community]-ki,M)-calculateQ(In[old_community],Tot[old_community],M)
            #计算将要加入的社区的detaQ
            for com in nbrs_community:
                detaQ2=calculateQ(In[com]+kiin_dict[com],Tot[com]+ki,M)-calculateQ(In[com],Tot[com],M)
                Q=detaQ2+detaQ1
                if Q>max_detaQ and Q>0:
                    max_detaQ=Q
                    max_community=com
                    max_nbrs=nbrs
            #如果该社区使网络模块度增加，则加进去
            if max_detaQ>0:
                index=True
                #更新节点社区编号
                community_node_in_dict[node]=max_community
                #更新所去的社区的In和Tot值
                In[max_community]=In[max_community] + kiin_dict[max_community]
                Tot[max_community]=Tot[max_community]+ki
                #更新原先的社区值
                In[old_community]=In[old_community]-kiout
                Tot[old_community]=Tot[old_community]-ki
                #更新社区
                community_dict[max_community].append(node)
                community_dict[old_community].remove(node)
                #原社区没有节点了就删除
                if community_dict[old_community].__len__()==0:
                    community_dict.__delitem__(old_community)
                    In.__delitem__(old_community)
                    Tot.__delitem__(old_community)
                #更新edge
                if edge_dict.has_key((node,max_nbrs)):
                    edge_dict[(node,max_nbrs)]=(max_community,max_community)
                else:
                    edge_dict[(max_nbrs, node)] = (max_community, max_community)

    nowQ = 0
    for com in community_dict:
        nowQ+=calculateQ(In[com], Tot[com] , M)
    return G,community_node_in_dict,community_dict,nowQ,Tot,In



def phase_two(now_G,community_node_dict):
    super_G=nx.Graph()
    super_edge={}
    for edge in now_G.edges():
        super_node1=community_node_dict[edge[0]]
        super_node2=community_node_dict[edge[1]]
        if (super_node1,super_node2) in super_edge or (super_node2,super_node1) in super_edge:
            if super_node1!=super_node2:
                super_edge[(super_node1,super_node2)]+=now_G.get_edge_data(*edge).values()[0]
                super_edge[(super_node2, super_node1)] += now_G.get_edge_data(*edge).values()[0]
            else:
                super_edge[(super_node1, super_node1)] += now_G.get_edge_data(*edge).values()[0]
        else:
            super_edge[(super_node1, super_node2)] = now_G.get_edge_data(*edge).values()[0]
            super_edge[(super_node2, super_node1)] = now_G.get_edge_data(*edge).values()[0]

    for edge in super_edge:
        if super_G.has_edge(*edge):
            continue
        super_G.add_edge(*edge,weight=super_edge[edge])
    for node in now_G.nodes():
        if now_G.degree(node)==0:
            super_G.add_node(node)
    return super_G

def merge_community_node(next_community, tmp_community, community_node_in_dict):
    communitys = {}
    for i in next_community.keys():
        communitys[i] = []
        for node in next_community[i]:
            for n in tmp_community[node]:
                community_node_in_dict[n]=i
                communitys[i].append(n)
    return communitys


def BGLL(G):
    ##进行第一次迭代
    t1 = time.clock()
    now_G, community_node_dict, now_community, now_Q, now_Tot, now_In = phases_one(G)
    community_node_in_dict = community_node_dict
    print "迭代第一次时间：", time.clock() - t1
    print "社区总数：", now_community.__len__()
    tmp_community = now_community
    print "Q:", now_Q, '\n'
    times = 1
    while True:
        times += 1
        ##根据now_edge_dict形成超级节点图
        t2 = time.clock()
        super_G = phase_two(now_G, community_node_dict)
        print "第", times, "个图生成的时间:", time.clock() - t2
        ##用超级节点形成的图去迭代
        t2 = time.clock()
        now_G, community_node_dict, now_community, next_Q, next_Tot, next_In = phases_one(super_G)
        print "迭代第", times, "次的时间：", time.clock() - t2
        print "社区总数：", now_community.__len__()
        ##如果当前社区的nextQ没有增加就返回
        print "Q:", next_Q, '\n'
        if next_Q <= now_Q:
            break
        now_Q = next_Q
        now_Tot, now_In = next_Tot, next_In
        tmp_community = merge_community_node(now_community, tmp_community, community_node_in_dict)
    return tmp_community,community_node_in_dict

t3=time.clock()

#构建网络图
def conGraph():
    g = nx.Graph()
    f = open("hep.txt")
    edge = []
    lines = f.readlines()
    for line in lines :
        n = line.split()
        ns = [ int(x) for x in n ]
        nss = tuple(ns)
        g.add_nodes_from(nss)
        edge.append(nss)
    
    g.add_edges_from(edge,weight =1)
    return g

#获取每个社团内节点的个数
def getComDegree(comID):   
    u = list(comID)
    numset = []
    for u in comID:
        num = len(comID.get(u))
        numset.append(num)
        #numset.sort()
   # print numset[-200:]
    return numset

#获得社团编号+对应的节点个数
def comNum(comID,degNum):
    d = dict(zip(comID,degNum))
    return d    

#按照节点个数大小排序
def degreeSort(numset):
    numset.sort()
    return  numset

#获取Top N
def  getTopN(numset,n):
    return numset[-n:]
  
#获取每个社团内的节点ID号：
def getComNodeID(u,n):
    return u.get(n)

#获取社团内节点的度数,并且排序 
def getcomNodeDe(comID):
    sss = []
    for i in comID:
        sss.append(len(g.neighbors(i)))
    sss.sort()
    return sss    

#找出    
def getNodeDegree(g,i):
    return g.neighbors(i)






if __name__ == '__main__':
    g = conGraph()
    u,v = BGLL(g)
    #print v
    
   # print comNum(u,s)

    ss = getComNodeID(u,6658)
   # print ss
    t = getcomNodeDe(ss)[-2:]
    # 112, 150, 156, 158, 179 190, 192, 194, 198, 206, 215, 256, 272, 288, 301
    #对应的社团编号：
    #301 ： 8027 ；288 : 7658；272 : 4965；256 : 8073；215 ：14742；206 ：13572；
    #198 ：7631 ；194 :5826；192:14317 ；190:5547；179：6658；
    #158：15128 ；156:7648；150:5359 112:13097
    
    #print t
    #print len(g.neighbors(9262))
  
    for i in t:
        for j in g:
            if len(g.neighbors(j)) == i:
                with open('F6658.txt','a') as filetwo:
                    filetwo.writelines(str(j)+'\n') 
 
    #print nuu[-200:]
    #comNum(u,nu)
     
         
             
   
    
'''
    
 
    uu = list(u)
    print uu
    numset = []
    for uu in u :
        num = len(u.get(uu))
        numset.append(num)
    print numset
'''
    
  #  print u.get(7823)
'''
    s = []
    ss = []
    s = u.get(7823)
    for i in s:
     #  ss.append(len(g.neighbors(i)))
    #ss.sort()  
    #print ss
    
        if len(g.neighbors(i)) == 19:
            print i
    
    uu = list(u)
    numset = []
    for uu in u :
        num = len(u.get(uu))
        numset.append(num)
   # print numset
    
    
    uuu = list(u)
    d = dict(zip(u,numset))
   # print d
    
    #print numset
   # print d
   # u.count(6408)
 #   print ("生成的社团编号为：")
   # print list(u)
 
    
    
    print ("最终收敛后的社团数量为：")
    print len(u)
   
    
    print ("第6408个社团内有哪些节点：")
    print u.get(6408)
    u.get
 
   
    with open('hepComDegNum.txt','w+') as filetwo:
        filetwo.writelines(str(ss)+'\n')  
    
   # f = open("result.txt",'w')
   # f.writelines(u)
    #print v
#print "总时间：",time.clock()-t3

'''
