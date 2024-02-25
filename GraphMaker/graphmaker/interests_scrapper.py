import pandas as pd
import ast
import re
import requests
from bs4 import BeautifulSoup
import clickhouse_connect
import config
import clickhouse_connection

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


def extract_email_prefixes(df, column_name='leaders'):
    """
    Extract email prefixes from DataFrame based on specific column containing leaders' information.
    """
    email_dict = {}
    for row in df[column_name]:
        leader_list = ast.literal_eval(row)
        for leader in leader_list:
            # Check if 'email' is present and is a list. If so, take the first item; otherwise, use it directly.
            email = leader.get('email')
            if isinstance(email, list) and email:  # If email is a non-empty list
                first_email = email[0]  # Take the first item
            elif isinstance(email, str):  # If email is already a string
                first_email = email
            else:  # If there is no email or it's not in an expected format
                first_email = None
            
            if first_email:  # Only proceed if there's an email to process
                email_prefix = first_email.split('@')[0]
                email_dict[leader['id']] = email_prefix
            else:  # Handle cases with no valid email
                email_dict[leader['id']] = None
    return email_dict


def enrich_with_interests(email_prefixes):
    """
    Enrich email prefixes with professional interests.
    """
    updated_dict = {}
    for id, email_prefix in email_prefixes.items():
        if email_prefix:
            interests = fetch_professional_interests(email_prefix)
            updated_dict[id] = interests
        else:
            updated_dict[id] = []
    return updated_dict


def prepare_dataframe(interests_dict):
    """
    Prepare the DataFrame from the interests dictionary.
    """
    data_for_df = [{'teacher_id': id, 'professional_interests': ', '.join(interests) if interests else ''} for id, interests in interests_dict.items()]
    df = pd.DataFrame(data_for_df)
    df['professional_interests'] = df['professional_interests'].apply(lambda x: re.sub(r'\b\d{2}\.\d{2}\.\d{2}\b[^,]*', '', x).replace(' , ', ', ').strip(', '))
    return df


def main():
    connection_manager = clickhouse_connection.ClickHouseConnection(host=config.ch_host, username=config.ch_username, password=config.ch_password)
    
    df = connection_manager.read_sql("SELECT * FROM sandbox.ongoing_projects")
    
    email_prefixes = extract_email_prefixes(df)
    interests_dict = enrich_with_interests(email_prefixes)
    final_df = prepare_dataframe(interests_dict)
    
    client = clickhouse_connect.get_client(host=config.ch_host, port=config.ch_port, username=config.ch_username, password=config.ch_password)
    
    client.command('DROP TABLE IF EXISTS sandbox.professional_interests')
    client.command("""
    CREATE TABLE sandbox.professional_interests
    (
        teacher_id UInt64,
        professional_interests String
    )
    ENGINE = MergeTree 
    ORDER BY teacher_id
    """)
    client.insert_df('sandbox.professional_interests', final_df)


if __name__ == "__main__":
    main()
