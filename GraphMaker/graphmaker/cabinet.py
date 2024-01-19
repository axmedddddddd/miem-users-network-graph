import datetime
import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

import requests
from tqdm import tqdm

import pandas as pd
import clickhouse_connect

BASE_URL = "https://cabinet.miem.hse.ru/public-api"

def api_call(method: str, str_param: str = ""):
    url = f"{BASE_URL}/{method}/{str_param}"
    r = requests.get(url)
    json = r.json()
    if json["message"] == "OK":
        return json["data"]
    else:
        return None


def parse_projects() -> dict:
    """Получение данных о проектах"""
    response = api_call("projects?statusIds[]=2&limit=1000")
    return response["projects"]

def project_team(project_id: int) -> Tuple[int, dict]:
    team = api_call("project/students", str_param=project_id)
    team = team["activeMembers"]
    return project_id, team


def detailed_project_info(pid: str, return_field: str = None):
    r = requests.get(f"https://cabinet.miem.hse.ru/public-api/project/body/{pid}")
    data = r.json()["data"]
    if return_field is None:
        return pid, data
    else:
        return pid, data[return_field]


def parse_from_cabinet():
    data = parse_projects()

    pids = [i["id"] for i in data]
    teams = {}
    detailed_infos = {}

    with ThreadPoolExecutor(max_workers=12) as executor:
        for pid, team in tqdm(executor.map(project_team, pids), total=len(pids)):
            teams[pid] = team

        for pid, info in tqdm(
            executor.map(detailed_project_info, pids), total=len(pids)
        ):
            detailed_infos[pid] = info

    for p in tqdm(data):
        pid = p["id"]
        p["detailed_team"] = teams[pid]
        detailed_info = detailed_infos[pid]
        p["projectIndustryLabel"] = detailed_info.get(
            "projectIndustryLabel", "Неизвестно"
        )
        p["typeDesc"] = detailed_info.get("typeDesc", "Неизвестно")
        p["leaders"] = detailed_info.get("leaders")

        for l in p["leaders"]:
            try:
                del l["pic"]
            except KeyError:
                continue

    return data
 
 def json_to_dataframe(json_data):
    # If input is not empty
    if json_data:
        # Initialize list for data
        data_list = []
        # Iterate through each project
        for project in json_data:
            # Initialize dict for project data
            project_dict = {}
            # Iterate through each attribute
            for key, value in project.items():
                # If attribute is a list or dict, convert to string
                if type(value) in [list, dict]:
                    value = str(value)
                # Add attribute to project dict
                project_dict[key] = value
            # Add project data to data list
            data_list.append(project_dict)

        # Create DataFrame
        df = pd.DataFrame(data_list).astype(str)
        
        return df
    
    # If input is empty
    else:
        print("Input JSON is empty")
        return pd.DataFrame()  # return an empty dataframe
    
df = json_to_dataframe(parse_from_cabinet())
    
host = "10.120.1.11"
username = "amarbuliev"
password = "KuUNgVlPQiSN6dRqk"

client = clickhouse_connect.get_client(host=host, port=8123, username=username, password=password)

client.command('DROP TABLE sandbox.ongoing_projects')

client.command("""
CREATE TABLE sandbox.ongoing_projects 
(
    id UInt64,
    status String,
    statusDesc String,
    nameRus String,
    head String,
    directionHead String,
    type String,
    typeDesc String,
    typeId UInt64,
    statusId UInt64,
    dateCreated String,
    vacancies UInt64,
    team String,
    vacancyData String,
    number UInt64,
    hoursCount UInt64,
    initiatorEmail String,
    payed Bool,
    projectOfficeControl Bool,
    studentsCount UInt64,
    searchString String,
    clientLogo String,
    detailed_team String,
    projectIndustryLabel String,
    leaders String,
    initiatorId Float64,
    thumbnail String
) 
ENGINE = MergeTree 
ORDER BY id
""")

client.insert_df(table='sandbox.ongoing_projects', df=df)