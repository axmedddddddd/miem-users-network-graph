import pandas as pd
import ast
import re
import requests
from bs4 import BeautifulSoup
from footprint_dftools import clickhouse as ch

from config import BaseConfig
config = BaseConfig()

def fetch_professional_interests(email_prefix):
    """
    Fetch professional interests from the provided page.
    """
    try:
        url = f'https://www.hse.ru/staff/{email_prefix}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        target_div = soup.find("div", class_="b-person-data__inner b-person-data__tags")
        return [a_tag.text for a_tag in target_div.find_all("a", class_="tag tag_small")] if target_div else []
    except Exception as e:
        print(f"Error fetching professional interests for {email_prefix}: {e}")
        return []


def extract_email_prefixes_and_short_names(df, column_name='leaders'):
    """
    Extract email prefixes and short names from DataFrame based on a specific column containing leaders' information.
    """
    result_dict = {}
    for row in df[column_name]:
        leader_list = ast.literal_eval(row)
        for leader in leader_list:
            # Construct short_name
            short_name = f"{leader['last_name']}"
            if leader["middle_name"] and leader["first_name"]:
                short_name = f"{leader['last_name']} {leader['first_name'][0]}.{leader['middle_name'][0]}."
            elif leader["first_name"]:
                short_name = f"{leader['last_name']} {leader['first_name'][0]}."

            # Extract email
            email = leader.get('email')
            if isinstance(email, list) and email:  # If email is a non-empty list
                first_email = email[0]  # Take the first item
            elif isinstance(email, str):  # If email is already a string
                first_email = email
            else:  # If there is no email or it's not in an expected format
                first_email = None
            
            # Process email to get email prefix
            if first_email:
                email_prefix = first_email.split('@')[0]
            else:  # Handle cases with no valid email
                email_prefix = None
            
            # Update result dictionary with a tuple containing the email prefix and the short name
            result_dict[leader['id']] = (email_prefix, short_name)

    return result_dict


def enrich_with_interests(email_prefixes_and_short_names):
    """
    Enrich email prefixes with professional interests.
    
    Parameters:
    - email_prefixes_and_short_names: A dictionary where the key is id, and the value is a tuple of (email_prefix, short_name).

    Returns:
    - A dictionary with short_name as keys and their associated professional interests as values.
    """
    updated_dict = {}
    for _, (email_prefix, short_name) in email_prefixes_and_short_names.items():
        if email_prefix:
            interests = fetch_professional_interests(email_prefix)
            updated_dict[short_name] = interests
        else:
            updated_dict[short_name] = []
    return updated_dict


def prepare_dataframe(interests_dict):
    """
    Prepare the DataFrame from the interests dictionary.
    """
    data = [(name, ', '.join(interests) if interests else '') for name, interests in interests_dict.items()]
    df = pd.DataFrame(data, columns=['name', 'professional_interests'])
    df['professional_interests'] = df['professional_interests'].apply(lambda x: re.sub(r'\b\d{2}\.\d{2}\.\d{2}\b[^,]*', '', x).replace(' , ', ', ').strip(', '))
    return df


def main():
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

if __name__ == "__main__":
    main()
