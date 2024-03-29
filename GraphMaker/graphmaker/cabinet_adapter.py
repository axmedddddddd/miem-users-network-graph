import datetime
import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Any, Optional, Dict
import requests
from tqdm import tqdm
import pandas as pd
from footprint_dftools import clickhouse as ch

from config import BaseConfig
config = BaseConfig()

import logging
logging.basicConfig(filename='backend.log', level=logging.INFO)
logger = logging.getLogger(name)


def api_call(method: str, str_param: str="") -> Optional[Dict[str, Any]]:
    """Accessing the Cabinet API"""
    if str_param:
        url = f"{base_url}/{method}/{str_param}"
    else:
        url = f"{base_url}/{method}"
    r = requests.get(url)
    json = r.json()
    if json["message"] == "OK":
        return json["data"]
    else:
        return None


def parse_projects() -> dict:
    """Getting project data"""
    response = api_call("projects?statusIds[]=2&limit=1000")
    return response["projects"]


def project_team(project_id: int) -> Tuple[int, dict]:
    """Getting data about project teams"""
    team = api_call("project/students", str_param=project_id)
    team = team["activeMembers"]
    return project_id, team


def detailed_project_info(pid: str, return_field: Optional[str] = None) -> Tuple[str, Any]:
    """Details of project data"""
    r = requests.get(f"https://cabinet.miem.hse.ru/public-api/project/body/{pid}")
    data = r.json()["data"]
    if return_field is None:
        return pid, data
    else:
        return pid, data[return_field]


def parse_from_cabinet() -> Dict[str, Any]:
    """Details of project data"""
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


def json_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """Creating a dataframe to upload to ClickHouse"""
    if json_data:
        data_list = []
        for project in json_data:
            project_dict = {}
            for key, value in project.items():
                if isinstance(value, (list, dict)):
                    value = str(value)
                project_dict[key] = value
            data_list.append(project_dict)

        df = pd.DataFrame(data_list).astype(str)
        
        return df

    else:
        logger.warning("adapter input JSON is empty")
        return pd.DataFrame()


if __name__ == "__main__":
    df = json_to_dataframe(parse_from_cabinet())
        
    client = ch.ClickHouseConnection(host=config.ch_host, port=config.ch_port, username=config.ch_user, password=config.ch_pass)

    client.read_database('TRUNCATE TABLE sandbox.ongoing_projects')

    client.write_database(df=df, table='ongoing_projects', schema='sandbox')
