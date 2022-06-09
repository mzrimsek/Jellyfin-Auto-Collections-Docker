'''Downloads BFI 'Mark Kermode Reviews' video to related films'''
#
# Requires the movies_dir path to be set to your movies library
#
import os
import glob
import json
import re
import requests
import configparser

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')
server_url = config["main"]["server_url"]
user_id = config["main"]["user_id"]
movies_dir = config["main"]["movies_dir"]
headers = {'X-Emby-Token': config["main"]["jellyfin_api_key"]}

def find_movie(title, year=None):
    params = {
        "searchTerm": title,
        "includeItemTypes": "Movie",
        "Recursive": "true",
        "enableTotalRecordCount": "false",
        "enableImages": "false",
    }
    if year is not None:
        params["years"] = year
    while True:
        try:
            res = requests.get(f'{server_url}/Users/{user_id}/Items',headers=headers, params=params)
            if len(res.json()["Items"]) > 0:
                return res.json()["Items"][0]
            else:
                return None
        except:
            pass

# Download playlist titles
if not os.path.exists("bfi"):
    os.mkdir("/tmp/bfi")
    os.system("cd /tmp/bfi && youtube-dl --ignore-errors --write-info-json --skip-download 'https://www.youtube.com/playlist?list=PLXvkgGofjDzhx-h7eexfVbH3WslWrBXE9'")

for fn in glob.glob("/tmp/bfi/*.json"):
    data = json.load(open(fn))
    movie_title = data["title"]
    movie_title = movie_title.split("|")[0]
    movie_title = movie_title.replace("BFI Player", "")
    movie_title = re.split(r'Reviews|reviews|reviews:|introduces', movie_title)[-1].strip()
    year_search = re.search(r'\((.*?)\)',movie_title)
    movie_year = None
    if year_search is not None:
        movie_year = year_search.group(1)
    movie_title = re.sub(r'\(.+\)', '', movie_title).strip()
    movie = None
    search_str = movie_title
    while movie is None:
        movie = find_movie(search_str, movie_year)
        if " " not in search_str:
            break
        search_str = search_str.split(" ", 1)[-1]
    if movie is not None:
        if movie["Name"].lower() not in movie_title.lower():
            movie = None

    print(movie_title, movie_year)
    if movie is not None:
        print("\tDownloading", movie["Name"], movie["Id"])
        movie_filepath = movies_dir + "/" + movie["Name"] + " (" + str(movie["ProductionYear"]) + ")/extras"
        if not os.path.exists(movie_filepath):
            # os.mkdir(movie_filepath)
            print("yt -i https://youtube.com/watch?v="+data["id"] + " --output '" + movie_filepath + "/Mark Kermode Introduces'")
