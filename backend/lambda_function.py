import requests
from bs4 import BeautifulSoup
import json
import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket="tidalwaves", Key="stations")
    content = response['Body'].read().decode('utf-8')
    stations = json.loads(content)
    response = s3.get_object(Bucket="tidalwaves", Key="k")
    content = response['Body'].read().decode('utf-8')
    k = json.loads(content)["k"]

    station = list(stations)[k]

    url = f"https://www.ndbc.noaa.gov/station_page.php?station={station}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    theads = soup.find_all("thead")
    tbodies = soup.find_all("tbody")
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
                stations[station][label] = td.text.strip()
                j += 1
    except:
        pass

    measurements = stations[station]
    if "WVHTft" in measurements and "DPDsec" in measurements:
        wvht = measurements["WVHTft"]
        dpd = measurements["DPDsec"]
        if wvht != "-" and dpd != "-":
            p = round(58.42 * float(wvht) * float(wvht) * float(dpd), 2)
            stations[station]["wave power"] = p
    if "WSPDkts" in measurements:
        wspd = measurements["WSPDkts"]
        if wspd != "-":
            p = round(8.39 * float(wspd) * float(wspd) * float(wspd), 2)
            stations[station]["wind power"] = p

    measurements = stations[station]
    if "wave power" in measurements:
        wave_power = measurements["wave power"]
        e = round(0.0009 * float(wave_power), 2)
        stations[station]["emissions avoided w/ waves"] = e
    if "wind power" in measurements:
        wind_power = measurements["wind power"]
        e = round(0.0009 * float(wind_power), 2)
        stations[station]["emissions avoided w/ wind"] = e

    k += 1
    if k == len(stations):
        k = 0
    
    s3.put_object(Bucket="tidalwaves", Key="k", Body=json.dumps({"k": k}), ContentType='application/json')
    s3.put_object(Bucket="tidalwaves", Key="stations", Body=json.dumps(stations), ContentType='application/json')

    features = {"type": "FeatureCollection",
            "features": []}
    for station in stations:
        if "lat" in stations[station] and "long" in stations[station]:
            if "wave power" in stations[station] or "wind power" in stations[station]:
                feature = {"type": "Feature",
                           "geometry": {"type": "Point",
                                        "coordinates": [stations[station]["long"], stations[station]["lat"]]},
                                        "properties": {"id": station,
                                                       "wave power": stations[station].get("wave power", ""),
                                                       "wind power": stations[station].get("wind power", ""),
                                                       "emissions avoided w/ waves": stations[station].get("emissions avoided w/ waves", ""),
                                                       "emissions avoided w/ wind": stations[station].get("emissions avoided w/ wind", "")}}
                features["features"].append(feature)

    s3.put_object(Bucket="tidalwaves", Key="geo", Body=json.dumps(features), ContentType='application/json')