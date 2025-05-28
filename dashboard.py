import pandas as pd
import requests
import time
import urllib.parse

# Configurações da Airtable
BASE_ID = 'appy1FWydl2FyBdJs'
TABLE_NAME = 'TM10'
API_URL = f'https://api.airtable.com/v0/appy1FWydl2FyBdJs/TM10'
API_TOKEN = 'patW0ar6vOitoWysr'
HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def enviar_dados_csv_para_airtable(csv_file):
    # Leitura da planilha
    df = pd.read_csv(csv_file)

    # Envio linha a linha
    for _, row in df.iterrows():
        payload = {
            'fields': {
                'Data': row['data'],
                'KM Rodados': row['km']
            }
        }
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        if response.status_code in [200, 201]:
            print(f"Enviado: {payload}")
        else:
            print(f"Erro: {response.status_code}, {response.text}")

if __name__ == "__main__":
    enviar_dados_csv_para_airtable('teste.csv')
