import json

# file_path = "countries.json"
# with open(file_path, 'r') as json_file:
#     countries = json.load(json_file)
    
# file_path = "combined_updated_countries.geojson"
# with open(file_path, 'r') as json_file:
#     data = json.load(json_file)
    
# features = data["features"]

# for i in range(len(features)):
#     properties = features[i]["properties"]
#     if "Country" not in properties:
#         continue
#     if properties["Country"] in countries:
#         for key, value in countries[properties["Country"]].items():
#             data["features"][i]["properties"][key] = float(value)
# file_path = "test.json"
# with open(file_path, 'w') as json_file:
#     json.dump(data, json_file)

file_path = "test.json"
with open(file_path, 'r') as json_file:
    data = json.load(json_file)
print(type(data["features"][0]["properties"]["Oil Cost"]))