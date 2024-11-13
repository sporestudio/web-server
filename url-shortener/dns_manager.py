from dotenv import load_dotenv
import requests
import json
import os


load_dotenv(dotenv_path='.env')

IONOS_API_KEY = os.getenv('IONOS_API_KEY')
DOMAIN_NAME = os.getenv('DOMAIN_NAME')
IONOS_URL = os.getenv('IONOS_BASE_URL')
ID = os.getenv('DOMAIN_ID')


# Function to create the TXT in the IONOS DNS
def create_txt_record(short_url, original_url):
    url = f"{IONOS_URL}/zones/{ID}/records"
    headers = {
    'accept': 'application/json',
    'X-API-Key': IONOS_API_KEY,
    'Content-Type': 'application/json'
    }

    # Datos a enviar en la petición
    data = [
        {
            "name": f'{short_url}.{DOMAIN_NAME}',
            "type": "TXT",
            "content": original_url,
            "ttl": 3600,
            "prio": 0,
            "disabled": False
        }
    ]

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return True
    except requests.exceptions.RequestException as e:
        print("There was an error:", e)
        return False


def get_original_url(short_url):
    # Query to TXT register
    dns_query_url = f"https://dns.google/resolve?name={short_url}.{DOMAIN_NAME}&type=TXT"
    try:
        reponse = requests.get(dns_query_url)
        response_data = reponse.json()

        # If query is successful, extract the data of TXT register
        if reponse.status_code == 200 and 'Answer' in response_data:
            for record in response_data['Answer']:
                if record['type'] == 16: # 16 is TXT register code type
                    return record['data'].strip('"') # Strip remove double quotes
    except Exception as e:
        print ("Error query DNS: ", e)
    
    return None
