import pymongo
import requests
from bs4 import BeautifulSoup
import re

def insert_stations(stations):
    url = "https://www.ndbc.noaa.gov/to_station.shtml"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    station_lists = soup.find_all("div", class_="station-list")
    for station_list in station_lists:
        all_stations = station_list.contents
        for station in all_stations:
            if not isinstance(station, str):
                document = {"id": station.text}
                stations.insert_one(document)

def insert_coordinates(stations):
    for doc in stations.find():
        station = doc["id"]
        url = f"https://www.ndbc.noaa.gov/station_page.php?station={station}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        link_tag = soup.find('link', {'rel': 'alternate', 'type': 'application/rss+xml', 'href': re.compile(r'^/rss/ndbc_obs_search.php')})
        if link_tag and 'title' in link_tag.attrs:
            title_value = link_tag['title']
            coordinates_match = re.search(r'near ([0-9.]+[A-Z]{1}) ([0-9.]+[A-Z]{1})', title_value)
            if coordinates_match:
                latitude = coordinates_match.group(1)
                longitude = coordinates_match.group(2)
                latitude_value = float(latitude[:-1])
                latitude_direction = latitude[-1]
                longitude_value = float(longitude[:-1])
                longitude_direction = longitude[-1]
                if latitude_direction == "S":
                    latitude_value *= -1
                if longitude_direction == "W":
                    longitude_value *= -1
                update_values = {"$set": {"lat": latitude_value, "long": longitude_value}}
                stations.update_one(doc, update_values)

def insert_measurements(stations, section):
    if section == 0:
        s = stations.find().limit(302)
    elif section == 1:
        s = stations.find().skip(302).limit(302)
    elif section == 2:
        s = stations.find().skip(604).limit(301)
    elif section == 3:
        s = stations.find().skip(905).limit(301)
    elif section == 4:
        s = stations.find().skip(1206).limit(301)
    else:
        s = stations.find().skip(1507)
    for doc in s:
        station = doc["id"]
        url = f"https://www.ndbc.noaa.gov/station_page.php?station={station}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        theads = soup.find_all("thead")
        tbodies = soup.find_all("tbody")
        measurements = {}
        try:
            trs = theads[0].contents
            i = 0
            while trs[i].name != "tr":
                i += 1
            ths = trs[i].contents
            j = 0
            labels = []
            for th in ths:
                if th.name == "th":
                    if j > 0:
                        labels.append(th.text.strip())
                    j += 1
            trs = tbodies[1].contents
            i = 0
            while trs[i].name != "tr":
                i += 1
            tds = trs[i].contents
            j = 0
            for td in tds:
                if td.name == "td":
                    label = labels[j]
                    measurements[label] = td.text.strip()
                    j += 1
        except:
            pass
        update_values = {"$set": measurements}
        stations.update_one(doc, update_values)

def insert_powers(stations, section):
    if section == 0:
        s = stations.find().limit(302)
    elif section == 1:
        s = stations.find().skip(302).limit(302)
    elif section == 2:
        s = stations.find().skip(604).limit(301)
    elif section == 3:
        s = stations.find().skip(905).limit(301)
    elif section == 4:
        s = stations.find().skip(1206).limit(301)
    else:
        s = stations.find().skip(1507)
    for doc in s:
        if "WVHTft" in doc and "DPDsec" in doc:
            wvht = doc["WVHTft"]
            dpd = doc["DPDsec"]
            if wvht != "-" and dpd != "-":
                p = round(58.42 * float(wvht) * float(wvht) * float(dpd), 2)
                update_values = {"$set": {"wave power": p}}
                stations.update_one(doc, update_values)
        if "WSPDkts" in doc:
            wspd = doc["WSPDkts"]
            if wspd != "-":
                p = round(8.39 * float(wspd) * float(wspd) * float(wspd), 2)
                update_values = {"$set": {"wind power": p}}
                stations.update_one(doc, update_values)

def insert_emissions(stations, section):
    if section == 0:
        s = stations.find().limit(302)
    elif section == 1:
        s = stations.find().skip(302).limit(302)
    elif section == 2:
        s = stations.find().skip(604).limit(301)
    elif section == 3:
        s = stations.find().skip(905).limit(301)
    elif section == 4:
        s = stations.find().skip(1206).limit(301)
    else:
        s = stations.find().skip(1507)
    for doc in s:
        if "wave power" in doc:
            wave_power = doc["wave power"]
            e = round(0.0009 * float(wave_power), 2)
            update_values = {"$set": {"emissions avoided w/ waves": e}}
            stations.update_one(doc, update_values)
        if "wind power" in doc:
            wind_power = doc["wind power"]
            e = round(0.0009 * float(wind_power), 2)
            update_values = {"$set": {"emissions avoided w/ wind": e}}
            stations.update_one(doc, update_values)

def lambda_handler(event, context):
    client = pymongo.MongoClient("mongodb+srv://projecttidal:sHf2O4p2qv8jgpJ3@projecttidal.q0fm5uw.mongodb.net/?retryWrites=true&w=majority")
    db = client["ProjectTidal"]
    stations = db["Stations"]
    section = db["Section"].find_one()["section"]
    insert_measurements(stations, section)
    insert_powers(stations, section)
    insert_emissions(stations, section)
    section += 1
    section %= 6
    db["Section"].update_one(db["Section"].find_one(), {"$set": {"section": section}})