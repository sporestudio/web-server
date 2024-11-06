import requests
import json
import os

IONOS_API_KEY = os.getenv('IONOS_API_KEY')
DOMAIN_NAME = os.getenv('DOMAIN_NAME')
IONOS_URL = os.getenv('IONOS_BASE_URL')

def create_txt_record(subdomain, original_url):
    url = f"{IONOS_URL}/zones/{DOMAIN_NAME}/records"
    headers = {
        'Authorization': f'Bearer {IONOS_API_KEY}',
        'Content_Type': 'application/json'
    }
    data = {
        'type': 'TXT',
        'name': f'{short_url}.{DOMAIN_NAME}', # TODO: Remember to add the subdomain varibale before the domain
        'value': original_url,
        'ttl': 3600
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        return True
    else:
        return False