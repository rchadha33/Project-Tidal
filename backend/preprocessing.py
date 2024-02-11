import requests
from bs4 import BeautifulSoup
import json
import re

def get_stations():
    url = "https://www.ndbc.noaa.gov/to_station.shtml"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    station_lists = soup.find_all("div", class_="station-list")
    all_stations = {}
    for station_list in station_lists:
        stations = station_list.contents
        for station in stations:
            if not isinstance(station, str):
                all_stations[station.text] = {}

    file_path = "stations.json"
    with open(file_path, 'w') as json_file:
        json.dump(all_stations, json_file)


def get_coordinates():
    file_path = "stations.json"
    with open(file_path, 'r') as json_file:
        stations = json.load(json_file)

    for station in stations:
        url = f"https://www.ndbc.noaa.gov/station_page.php?station={station}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        link_tag = soup.find('link', {'rel': 'alternate',
                                      'type': 'application/rss+xml',
                                      'href': re.compile(r'^/rss/ndbc_obs_search.php')})
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
                stations[station]["lat"] = latitude_value
                stations[station]["long"] = longitude_value

    file_path = "stations.json"
    with open(file_path, 'w') as json_file:
        json.dump(stations, json_file)
