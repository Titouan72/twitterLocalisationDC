import os
import tweepy
from dotenv import load_dotenv
import requests
import csv
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt
import math
from collections import Counter
import folium

load_dotenv()
client = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAAN54kAEAAAAAoCYGzLAcIaG7PjD%2FiThZNl7Purc%3DF6BV2zTXHDPAef6CfOtgUrAnJKIb2GRhr1rzPih6pw48WRZANX')
print(r"""
        _____          
    ,-:` \; ,` -,      
  . -;_,;   :-;_, .    
 /;    /    ,  _`.-\   
|  `. (`     /` ` \`|  
|:.  `\`-.   \_   / |  
|     (   `,  .`\ ; |  
 \     | .      `- /   
  `.   ;/        .     
    ` -._____.          
  _______       _ _   _             _____            _                
 |__   __|     (_) | | |           / ____|          | |               
    | |_      ___| |_| |_ ___ _ __| |  __  ___  ___ | |     ___   ___ 
    | \ \ /\ / / | __| __/ _ \ '__| | |_ |/ _ \/ _ \| |    / _ \ / __|
    | |\ V  V /| | |_| ||  __/ |  | |__| |  __/ (_) | |___| (_) | (__ 
    |_| \_/\_/ |_|\__|\__\___|_|   \_____|\___|\___/|______\___/ \___|

                """)
print('Write the twitter id of the person you want the geolocation:')
username = input()
print('Please wait few seconde')
response = client.get_user(username=username, user_fields='location')
id_of_user = response.data.id
df = pd.DataFrame({'id': 0, 'city': 0, 'long': 0, 'lat': 0, 'geoPlot': 0}, index=[0])
headers = {"Authorization": os.environ["BEARER_TOKEN"]}

def make_request(id):
    send_url = "https://api.twitter.com/2/users/" + id + "?user.fields=location"
    r =requests.get(send_url, headers=headers)
    j = r.json()
    if 'detail' in j:
        print('API is on fire pls wait 15 minutes and retry. Sorry !!!')
    else:
        if 'location' in j['data']:
            if ',' in j['data']['location']:
                city = j['data']['location'].split(',', 1)[0]
                ifile  = open('city.csv', "r", encoding="utf8")
                read = csv.reader(ifile)
                for row in read :
                    if city in row:
                        return city
            else:
                city = j['data']['location']
                ifile  = open('city.csv', "r", encoding="utf8")
                read = csv.reader(ifile)
                for row in read :
                    if city in row:
                        return city

make_request(str(id_of_user))
city_of_init_user = make_request(str(id_of_user))

############### PREDICTION USING FOLLOWERS LOC ################

send_url2 = "https://api.twitter.com/2/users/" + str(id_of_user) + "/followers"
r2 = requests.get(send_url2, headers=headers)
id_of_followers = []
city_of_followers = []
for e in r2.json()['data']:
    id_of_followers.append(e['id'])
for f in id_of_followers:
    so = make_request(f)
    if so != None: 
        city_of_followers.append(so)

geolocator = Nominatim(user_agent="twitterLocation")
sum_to_do_long = []
sum_to_do_lat = []
R_sum_to_do_long = []
R_sum_to_do_lat = []
for z in city_of_followers:
    location = geolocator.geocode(z)
    df.loc[len(df)] = {'id': id_of_user, 'city': city_of_init_user, 'long': location.longitude, 'lat': location.latitude, 'geoPlot': round(location.longitude - location.latitude, 2)}
    sum_to_do_long.append(location.longitude)
    sum_to_do_lat.append(location.latitude)
    R_sum_to_do_long.append(math.ceil(location.longitude / 10)*10)
    R_sum_to_do_lat.append(math.ceil(location.latitude / 10)*10)

sumLongOfFollowers= (sum(sum_to_do_lat))/len(sum_to_do_lat)
sumLatOfFollowers= (sum(sum_to_do_long))/len(sum_to_do_long)

counterLong = Counter(R_sum_to_do_long)
counterLat = Counter(R_sum_to_do_lat)
counterLongNotR = Counter(sum_to_do_long)
counterLatNotR = Counter(sum_to_do_lat)
most_common_counterLong = counterLong.most_common(1)
most_common_counterLat = counterLat.most_common(1)
percent_of_same_long = counterLong.most_common(1)[0][1] * 100 / len(R_sum_to_do_long)
percent_of_same_lat =  counterLat.most_common(1)[0][1] * 100 / len(R_sum_to_do_lat)
percent_of_same_long_notR = counterLongNotR.most_common(1)[0][1] * 100 / len(sum_to_do_long)
percent_of_same_lat_notR =  counterLatNotR.most_common(1)[0][1] * 100 / len(sum_to_do_lat)

def_long = []
def_lat = []

if percent_of_same_long > 50:
    for x in sum_to_do_long:
        if x > counterLongNotR.most_common(1)[0][0] - 5 and x < counterLongNotR.most_common(1)[0][0] + 5:
            def_long.append(x)
else:
    def_long = sumLongOfFollowers    
    
if percent_of_same_lat > 50:
    for y in sum_to_do_lat:
        if y > counterLatNotR.most_common(1)[0][0] - 5 and y < counterLatNotR.most_common(1)[0][0] + 5:
            def_lat.append(y)
else:
    def_lat = sumLatOfFollowers 

############## FINAL PREDICTED LOC #######################
def_lat = (sum(def_lat))/len(def_lat)
def_long = (sum(def_long))/len(def_long)

############## DISPLAY MAP LOC ON HTML FILE ##############

print('Latitude: ', def_lat)
print('Longitude: ',def_long)
m = folium.Map(location=[def_lat, def_long], zoom_start=3, tiles="Stamen Toner")

folium.Circle(
    radius=100,
    location=[def_lat, def_long],
    popup="The Waterfront",
    color="crimson",
    fill=False,
).add_to(m)

folium.CircleMarker(
    location=[def_lat, def_long],
    radius=50,
    popup=username + ' is here !',
    color="#FF0000",
    fill=True,
    fill_color="#FF0000",
).add_to(m)

m.save("index.html")
print('Oof thats done at least check the map on html file')
############### ANALYSIS PLOT FIGURE ###############
""" df = df.iloc[1: , :]
df.sort_values(['geoPlot'], inplace=True)
df['index'] = list(range(len(df.index)))
print(df)
df.plot(x='index', y='geoPlot')
plt.show() """