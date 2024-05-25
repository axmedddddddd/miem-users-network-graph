import requests
from typing import Optional, List, Dict

from logger_config import setup_logger
logger = setup_logger()

cache = {}  # Shared cache dictionary


def make_cache_key(namespace, *args):
    return namespace + ":" + ":".join(map(str, args))


def get_access_token(base_url, username, password) -> Optional[str]:
    
    global cache
    namespace = "get_access_token"
    key = make_cache_key(namespace, username, password)
    url = base_url + "/authentication_token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"username": username, "password": password}
    
    try:
        auth_response = requests.post(url, headers=headers, data=data)
        if auth_response.status_code == 200:
            token = auth_response.json().get('access_token', None)
            cache[key] = token
            return token
        else:
            logging.info("API error with status code: {}".format(auth_response.status_code))
            return cache.get(key, None)
    except requests.RequestException as e:
        logging.error("Request failed: {}".format(e))
        return cache.get(key, None)


def fetch_table_data(base_url, access_token, source) -> Optional[List[Dict]]:
    
    global cache
    namespace = source
    cache_key = make_cache_key(namespace, access_token, source)
    
    if cache_key in cache:
        logger.info(f"Returning cached data for source: {source}")
        return cache[cache_key]
    
    url = base_url + "/graph/tables_data"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "source": source
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        source_data = response.json().get('source_data', None)
        if source_data:
            cache[cache_key] = source_data
            return source_data
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return cache.get(cache_key, None)
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return cache.get(cache_key, None)
    except ValueError:
        logger.error("Failed to decode JSON from response")
        return cache.get(cache_key, None)
    
    return None
