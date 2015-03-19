# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:16:31 2015

@author: dpryce
"""

import urllib2
import json
import pandas as pd
import numpy as np
import sys

if sys.version_info.major < 3:
    from urllib2 import quote, URLError, urlopen
else:
    from urllib.error import URLError
    from urllib.parse import quote
    from urllib.request import urlopen

END_POINT = 'http://www.uk-postcodes.com'

key = "p85jfyuezn4f34ftj6yxtgj5"
base_url = "http://api.zoopla.co.uk/api/v1/property_listings.js?"
lat = 51.487753
lon = -0.111691
rad = 15
max_price = 250000
min_beds = 1
max_beds = 3
page_size_max = 100




def api_call_per_page(pagenum,page_size):

    url = base_url + "latitude="+str(lat)+"&longitude="+str(lon)+"&radius="+str(rad) \
                    +"&listing_status="+"sale"+"&maximum_price="+str(max_price)+"&maximum_beds="+str(max_beds)+\
                        "&page_size="+str(page_size)+"&page_number="+str(pagenum)+\
                       "&api_key="+str(key)

    
    json_string = urllib2.urlopen(url).read()
    the_data = json.loads(json_string)
    all_results=the_data['result_count']
    posttown = []
    status = []
    rooms = np.zeros(page_size)
    list_lat = np.zeros(page_size)
    list_lon = np.zeros(page_size)
    for i in range(0,page_size):
        status.append(the_data['listing'][i]['status'])
        posttown.append(the_data['listing'][i]['outcode'])
        
        
    for j in range(0,page_size-1):
        rooms[j] = the_data['listing'][j]['num_bedrooms']
        list_lat[j] = the_data['listing'][j]['latitude']
        list_lon[j] = the_data['listing'][j]['longitude']
        
    df = pd.DataFrame({'Status': status,'Number_of_room': rooms,\
                        'Latitude': list_lat,'Longitude': list_lon,'Postcode':posttown}) 
    df = df[df.Number_of_room != 0]
#    df = df[df.Status == 'for_sale']    
    
    df = df.reset_index(drop=True)
    return df,all_results

def _get_json_resp(url):
    try:
        resp = urlopen(url)
    except URLError as e:
        if e.code == 404: # no available data   
            return None
    else:
        return json.loads(resp.read().decode('utf-8'))
        
def get_nearest(lat, lng):
    """
    Request the nearest `postcode` to a geographical point, 
    specified by `lat` and `lng`.
    :param lat: latitude of point.
    :param lng: longitude of point.
    :returns: a dict of the nearest postcode's data.
    """
    url = '%s/latlng/%s,%s.json' % (END_POINT, lat, lng)
    return _get_json_resp(url)
    
    
def get_conts_title(lat,lng):
    detail = get_nearest(lat,lng)
    conts_title = detail['administrative']['constituency']['title']
    return conts_title


data,results = api_call_per_page(1,page_size_max)

loopnumber = (results-page_size_max)/page_size_max+1

for p in range(2,loopnumber):
    data2,_ = api_call_per_page(p,page_size_max)
    data = data.append(data2)

leftovers = results-page_size_max*loopnumber
data_final,_=api_call_per_page(loopnumber+1,leftovers)
data = data.append(data_final)

data = data.reset_index(drop=True)
data['Area name']=0
data['1 bed']=0
data['2 bed']=0
data['3 bed']=0

for j in range(1,4):
    data.loc[(data['Number_of_room']==j),'{} bed'.format(j)]=1


#for i in range(0,len(data)-1):
#
#        
#    lat = data['Latitude'][i]
#    lon = data['Longitude'][i]
#    data['Area name'][i] = get_conts_title(lat,lon)
#
#group = data.groupby(data['Area name'])
#table = group['1 bed', '2 bed', '3 bed'].sum()

group = data.groupby(data['Postcode'])
table = group['1 bed', '2 bed', '3 bed'].sum()


'''ADD loop to create all data for entire dataset'''

