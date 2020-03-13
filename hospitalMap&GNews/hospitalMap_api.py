import json
import os
import requests
import shutil
import csv

city = 820000
# while city < 660000:
OUT_PATH = 'outMapData/'
OUT_FILE = 'outMapData/' + str(city)

# if os.path.exists(OUT_PATH):
#     shutil.rmtree(OUT_PATH)
# os.mkdir(OUT_PATH)

page = 1
keywords = 'keywords=医院'

pagestr = 'page=' + str(page)
isEmptyPois = True

myPois = []
keysIWant = ['timestamp', 'name', 'type', 'location', 'cityname', 'adname', 'address']

while isEmptyPois:
    pagestr = '&page=' + str(page)
    print('current in page: ' + str(page))
    url = r'https://restapi.amap.com/v3/place/text?' + keywords + '&city=' + str(city) + '&citylimit=true' \
          + '&output=json&offset=20' + pagestr + \
          '&key=<User GaoDe map key>&extensions=all'
    session = requests.session()
    res = session.get(url)
    content = json.loads(res.text)
    pois = content['pois']
    for item in pois:
        myItem = {myKey: item[myKey] for myKey in keysIWant}
        myPois.append(myItem)
    # only 5 page test
    # if page == 5:
    #     break
    if len(pois) > 0:
        page = page + 1
    else:
        isEmptyPois = False

# writing to csv file
with open(OUT_FILE, 'w') as csvfile:
    # creating a csv dict writer object
    writer = csv.DictWriter(csvfile, fieldnames=keysIWant)

    # writing headers (field names)
    writer.writeheader()

    # writing data rows
    writer.writerows(myPois)











