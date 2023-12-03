import datetime
import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

import requests
from tqdm import tqdm

from graphmaker import config


def api_call(method: str, dict_params: dict = {}, str_param: str = ""):
    url = f"{config.BASE_URL}/{method}/{str_param}"
    r = requests.get(
        url,
        headers={
            "accept": "application/json",
            "X-Auth-Token": config.CABINET_API_TOKEN,
        },
        params=dict_params,
    )
    json = r.json()
    if json["message"] == "OK":
        return json["data"]
    else:
        return None


def parse_projects() -> dict:
    """Получение данных о проектах"""
    response = api_call("projects")
    return response


def filter_by_working(data: dict) -> List[dict]:
    data = [p for p in data if p["statusDesc"] == "Рабочий"]
    return data


def project_team(project_id: int) -> Tuple[int, dict]:
    team = api_call("project/students", str_param=project_id, dict_params={})
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
    data = filter_by_working(data)

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


def get_projects():
    now = datetime.datetime.now()
    day = now.day
    month = now.month
    year = now.year

    projects_filename = f"projects_{day}_{month}_{year}.json"
    projects_filename_path = f"{config.ROOT_DIR}/data/{projects_filename}"
    if os.path.exists(projects_filename_path):
        with open(projects_filename_path, "r") as f:
            return json.load(f)

    # if todays file does not exist
    try:
        raise EnvironmentError
        data = parse_from_cabinet()
        with open(projects_filename_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        all_projects_caches = glob.glob(f"{config.ROOT_DIR}/data/projects*")
        with open(all_projects_caches[-1], "r") as f:
            return json.load(f)

    return data


if __name__ == "__main__":
    from pprint import pprint

    data = get_projects()
    print(data[0])
