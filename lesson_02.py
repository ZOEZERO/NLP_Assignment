# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 17:38:29 2019

@author: 212477678
"""

!pip install urllib
!pip install bs4

import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

headers =  {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
all_url = 'https://shanghai.8684.cn'  ##开始的URL地址
start_html=requests.get(all_url)
Soup = BeautifulSoup(start_html.text,'lxml')
second_info = Soup.find('div',class_='bus_layer_r').find_all('a')[0]
second_href = second_info['href']
second_html = all_url+second_href
second_html = requests.get(second_html)
Soup2 = BeautifulSoup(second_html.text,'lxml')
third_info = Soup2.find('div',class_='stie_list').find_all('a')  

#metro_list=[]

def find_time(string):
    string_len = len(string)
    stop = string.find('|')
    start = stop-11
    time1 = string[5:stop]
    time2 = string[stop+1:]
    return time1,time2

def find_change_station_info(string):
#    string = line_label
    string_len = len(string)
    start = string.find('换乘信息')
    end = string.find('各车站周边主要信息')
    string_trim = string[start+5:end]
    return string_trim

metro_list=[]
for line in third_info:
#    line = third_info[-1]
    line_href = line['href']
    print(line_href)
    line_html = all_url+line_href  
    line_html = requests.get(line_html)
    line_Soup = BeautifulSoup(line_html.text,'lxml')
    line_name = line_Soup.find('div',class_='bus_i_t1').find('h1').get_text()[:-5]
    line_time = line_Soup.find_all('p',class_='bus_i_t4')[0].get_text()
    line_time1,line_time2 = find_time(line_time)
    line_label = line_Soup.find('div',class_='bus_label')
    if line_label:    
        line_change = line_Soup.find('div',class_='bus_label').get_text()
    else:
        line_change = None
    try:
        line_change_info= find_change_station_info(line_change)
    except:
        line_change_info = ''
    line_stations = line_Soup.find('div',class_='bus_line_site').get_text()
    information=[line_name,line_time1,line_time2,line_change_info,line_stations]
    metro_list.append(information)

del information,line,line_change,line_change_info,line_href,line_name,line_time1,line_time2,line_label,line_stations

del second_href,line_time
#label line name

station_change={}
line_name_mapping ={}
line_station = {}
station_connection_info ={}
import re
for line in metro_list:
#    line = metro_list[0]
#    print(line)
    station_info = line[-1]
    line_name = line[0]
    print(line_name)
    try:
        pattern2 = re.compile(r'(\d+)')
#        line_name_clean=re.findall(pattern2,line_name)[0]+str("号线")
        if line_name.find('支线')<0:
            line_name_clean=re.findall(pattern2,line_name)[0]+str("号线")
        else:
            line_name_clean=re.findall(pattern2,line_name)[0]+str("号线支线")
#        print(line_name2)
    except:
        if line_name =='上海金山铁路公交车路线':
            line_name_clean = '金山铁路'
        if line_name =='上海APM轨交浦江线公交车路线':
            line_name_clean = '浦江线'
        if line_name =='上海轨道交通5号线公交车路线':
            line_name_clean = '5号支线'        
    line_name_mapping[line_name] = line_name_clean
    pattern = re.compile(r'(\D+)')
    station_name = re.findall(pattern,station_info)
    line_station[line_name_clean] = station_name
    print (station_name)    
    for i,value in enumerate(station_name):
#        i=1
        print (station_name[i])
        if value not in station_change.keys():
            station_change[value] = [line_name_clean]
        else:
            station_change[value].append(line_name_clean)
            
        if i ==0:
            if value not in station_connection_info.keys():
                station_connection_info[value] = [station_name[i+1]]
#            else:
            elif station_name[i+1] not in station_connection_info[value]:
                station_connection_info[value].append(station_name[i+1])
        elif i == (len(station_name)-1):
            if value not in station_connection_info.keys():
                station_connection_info[value] = [station_name[i-1]]
            elif station_name[i-1] not in station_connection_info[value]:
                station_connection_info[value].append(station_name[i-1])
        else:
            if value not in station_connection_info.keys():
                station_connection_info[value] = [station_name[i-1],station_name[i+1]]
            else:
                if station_name[i-1] not in station_connection_info[value]:
                    station_connection_info[value].append(station_name[i-1])
                if station_name[i+1] not in station_connection_info[value]:
                    station_connection_info[value].append(station_name[i+1])
        
#        line_info[line_name_clean].append(i)

#station_change['世纪大道']
#station_connection_info['人民广场']
#breath first, 广度优先遍历

def breath_first_seach(start,end,connection,sort_method):
    pathes=[[start]]
    visited=set()
    final_path=[]
    while pathes:
        path = pathes.pop()
        next_stop = path[-1]
#        print(next_stop)
        if next_stop in visited: continue
        successors = connection[next_stop]
        for successor in successors:
            if successor in visited: continue
            new_path = path + [successor]
            pathes = pathes + [new_path]
#            pathes.append(new_path)
#            print (pathes)
            if successor == end:
#                transfer_line_info(new_path)
                final_path +=[new_path]
#                return final_path
        visited.add(next_stop)
        pathes = sort_method(pathes)
        print(pathes)
#        pathes = transfer_station_least_first(pathes)
#        final_path = sort_method(final_path)
    return final_path



def transfer_station_least_first(pathes):
    return sorted(pathes,key=len,reverse=True)

def transfer_station_most_first(pathes):
    return sorted(pathes,key=len,reverse=False)

def transfer_line_info(pathes):
#    for i,value in enumerate(pathes):
        new_pathes = pathes[0]
#        new_pathes = pathes.copy()    
        begin_station = new_pathes.pop(0)
        next_station = new_pathes.pop(0)
        line_first = station_change[begin_station]
        line_next = station_change[next_station]
        line_begin=set(line_first).intersection(set(line_next))
        line_transfer= line_begin
        final_path = [[begin_station,list(line_transfer)[0]]]+[[next_station,list(line_transfer)[0]]]
        while new_pathes !=[]:
            station = new_pathes.pop(0)
            new_line=set(station_change[station])
            if line_transfer.intersection(new_line)!=set():                
                new_line=line_transfer.intersection(new_line)
                new_station_info = [[station,list(new_line)[0]]]
                final_path +=new_station_info
            else:
                next_station = new_pathes.pop(0)
                new_line2 = set(station_change[next_station])
                new_line = new_line.intersection(new_line2)
                line_transfer=line_transfer.union(new_line)
                
                new_station_info = [[station,list(new_line)[0]]]
                final_path +=new_station_info 
                new_station_info = [[next_station,list(new_line)[0]]]
                final_path +=new_station_info                 
                
        final_path = pd.DataFrame(final_path)
        final_path['transfer']=final_path.iloc[:,1].shift(-1)
        return final_path
#        commute_lines = final_path.iloc[:,1].drop_duplicates()
        
#        change_info = final[]            
        

pathes=breath_first_seach('上海科技馆','徐家汇',station_connection_info,sort_method=transfer_station_least_first)


#final path : take which line and change line in which station
final_path =transfer_line_info(pathes)










c=a.intersection(b)

def depth_first_search(start,end,connection):
    pathes=[[start]]
    visited=set()
    while pathes:
        path = pathes.pop()
        next_stop = path[-1]
#        print(next_stop)
        if next_stop in visited:continue
        successors = connection[next_stop]
        for successor in successors:
            if successor in visited: continue
            new_path =  path +[successor]
#            pathes.append(new_path)
#            pathes = pathes + [new_path]
            pathes = [new_path] +pathes
#            print (pathes)
            if successor ==end:
                return new_path
        visited.add(next_stop)
        print(visited)
#    return pathes
        
depth_first_search('龙阳路','世纪大道',station_connection_info)        

station_connection_info['龙阳路']      
        
              
breath_first_seach('龙阳路','人民广场',station_connection_info)             
depth_first_search('龙阳路',station_connection_info)            


def search_update(start,end,connection):
#    start='龙阳路'
    visited =[start]
    seen = set()
    while visited:
        connect_stop = visited.pop(0)
        if connect_stop in seen: continue
        for next_stop in connection[connect_stop]:
            if next_stop in seen: continue
            visited = visited + [next_stop]  #breath first
            visited = [next_stop] + visited  #depth first
            print (visited)
            path = connect_stop+next_stop
            if next_stop==end: return path
        seen.add(connect_stop)
        
search_update('龙阳路','人民广场',station_connection_info)               

def bfs(graph,start):
#    start='长沙'
#    graph = simple_connection_info
    "breath first search"
    visited = [start]
    seen = set()
    while visited:
        froninter = visited.pop()
        if froninter  in seen: continue
        for successor in graph[froninter]:
            if successor in seen: continue
#            print(successor)
#            visited.append(successor)

#            visited =   [successor] +visited # 每次都考虑已经发现的点-->breath first
            visited =   visited + [successor]   #每次都考虑最新的点--->depth first
            print (visited)
        seen.add(froninter)
    return seen

bfs(station_connection_info,'龙阳路')


del line_name,station_info,line,line_name_clean,station_name,value






import networkx as nx
#G = nx.path_graph(24)

G = nx.Graph()
G.add_nodes_from(line_station)

nx.draw(nx.Graph(line_station),with_labels=True)

nx.draw(nx.Graph())


G = nx.Graph()
G.add_nodes_from(line_station['1号线'])
#G.add_edges_from(station_change)
nx.draw(G,with_labels=True,node_size=600)


    

#breath first, 广度优先遍历        
def breadth_search(start,end):
    pathes=[[start]]
    print(pathes)
    visited = set{}
    while pathes:
        
    







print(line_station_data['人民广场'])
    
    
    
    max_number = pattern.findall(station_info)
    
    metro_list[-1]
#    print(line_label.find('终点站',1))
    line_label[0]
    if line_label:
        line_length = line_label.get_text()
    
    line_info = line_Soup.find('div',class_='bus_line_site').find_all('a')
    for station in line_info:
        station_href = station['href']
        station_html = all_url + station_href
        station_html = requests.get(station_html)
        station_soup = BeautifulSoup(station_html.text,'lxml')
        station_name = station_soup.find('div',class_='bus_i_t3').find('h1').get_text()
        station_name =
        
        
        
    
string ='tensorflow:Final best valid 0 loss=0.20478513836860657 norm_loss=0.767241849151384 roc=0.8262403011322021 pr=0.39401692152023315 calibration=0.9863265752792358 rate=0.0'
   
pattern = re.compile(r'(?:norm_loss=)\d+\.?\d*')

print( pattern.findall(string))


start_html = requests.get(all_url)
Soup = BeautifulSoup(start_html.text,'lxml')
all_lines = Soup.find('div',class_='stie_list').find_all('a')

for line in all_lines:
    href = line['href']
    html = all_url+href
    second_html = requests.get(html)
    Soup2 = BeautifulSoup(second_html.text,'lxml')
    all_lines_detail = requests.get()



all_a = Soup.find('div',class_='bus_kt_r1').find_all('a')





import requests ##导入requests
from bs4 import BeautifulSoup ##导入bs4中的BeautifulSoup
import os

headers =  {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
all_url = 'http://beijing.8684.cn'  ##开始的URL地址
start_html = requests.get(all_url, headers=headers) 
Soup = BeautifulSoup(start_html.text, 'lxml')
all_a = Soup.find('div',class_='bus_kt_r1').find_all('a')

Network_list = []
for a in all_a:
    href = a['href'] #取出a标签的href 属性
    html = all_url + href
