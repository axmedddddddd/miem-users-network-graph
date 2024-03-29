import pandas as pd
import ast
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Any, Optional, Dict
from footprint_dftools import clickhouse as ch

from config import BaseConfig
config = BaseConfig()

import logging
logging.basicConfig(filename='backend.log', level=logging.INFO)
logger = logging.getLogger(name)

def fetch_professional_interests(email_prefix: str) -> List[str]:
    """Get interests info via provided teacher's page url"""
    try:
        url = f'https://www.hse.ru/staff/{email_prefix}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        target_div = soup.find("div", class_="b-person-data__inner b-person-data__tags")
        return [a_tag.text for a_tag in target_div.find_all("a", class_="tag tag_small")] if target_div else []
    except Exception as e:
        logger.error(f"Error fetching professional interests for {email_prefix}: {e}", exc_info=True)
        return []


def extract_email_prefixes_and_short_names(df: pd.DataFrame, column_name: str='leaders') -> Dict[int, Tuple[str, str]]:
    """Extract email prefixes and short names from DataFrame based on a specific column containing leaders' information"""
    result_dict = {}
    for row in df[column_name]:
        leader_list = ast.literal_eval(row)
        for leader in leader_list:
            short_name = f"{leader['last_name']}"
            if leader["middle_name"] and leader["first_name"]:
                short_name = f"{leader['last_name']} {leader['first_name'][0]}.{leader['middle_name'][0]}."
            elif leader["first_name"]:
                short_name = f"{leader['last_name']} {leader['first_name'][0]}."

            email = leader.get('email')
            if isinstance(email, list) and email:
                first_email = email[0]
            elif isinstance(email, str):
                first_email = email
            else:
                first_email = None
            
            if first_email:
                email_prefix = first_email.split('@')[0]
            else:
                email_prefix = None
            
            result_dict[leader['id']] = (email_prefix, short_name)

    return result_dict


def enrich_with_interests(email_prefixes_and_short_names: Dict[int, Tuple[str, str]]) -> Dict[str, List[str]]:
    """Enrich email prefixes with professional interests"""
    updated_dict = {}
    for _, (email_prefix, short_name) in email_prefixes_and_short_names.items():
        if email_prefix:
            interests = fetch_professional_interests(email_prefix)
            updated_dict[short_name] = interests
        else:
            updated_dict[short_name] = []
    return updated_dict


def prepare_dataframe(interests_dict: Dict[str, List[str]]) -> pd.DataFrame:
    """Prepare the DataFrame from the interests dictionary"""
    data = [(name, ', '.join(interests) if interests else '') for name, interests in interests_dict.items()]
    df = pd.DataFrame(data, columns=['name', 'professional_interests'])
    df['professional_interests'] = df['professional_interests'].apply(lambda x: re.sub(r'\b\d{2}\.\d{2}\.\d{2}\b[^,]*', '', x).replace(' , ', ', ').strip(', '))
    return df


def main() -> None:
    client = ch.ClickHouseConnection(host=config.ch_host, port=config.ch_port, username=config.ch_user, password=config.ch_pass)
    
    df = client.read_database("SELECT * FROM sandbox.ongoing_projects")
    
    email_prefixes = extract_email_prefixes_and_short_names(df)
    interests_dict = enrich_with_interests(email_prefixes)
    final_df = prepare_dataframe(interests_dict)

    client.read_database('TRUNCATE TABLE sandbox.professional_interests')
    client.write_database(df=final_df, table='professional_interests', schema='sandbox')
    
    final_df.set_index('name', inplace=True)
    path_to_cache = os.path.join("/code/public/data", f"teacher_interests.json")
    with open(path_to_cache, 'w', encoding='utf-8') as json_file:
        json.dump(final_df['professional_interests'].to_dict(), json_file, ensure_ascii=False, indent=4)
    
    return

if __name__ == "__main__":
    main()
