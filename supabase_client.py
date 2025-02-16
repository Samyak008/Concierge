import requests
from config import supabase_url, supabase_key

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

def fetch_table_data(table_name: str):
    url = f"{supabase_url}/rest/v1/{table_name}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_table_data(table_name: str, record_id: int, data: dict):
    url = f"{supabase_url}/rest/v1/{table_name}?id=eq.{record_id}"
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def insert_table_data(table_name: str, data: dict):
    url = f"{supabase_url}/rest/v1/{table_name}"
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()