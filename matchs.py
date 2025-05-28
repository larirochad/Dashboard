import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Tuple
from haversine import haversine
import numpy as np

def load_file(path: str) -> pd.DataFrame:
    encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(
                path,
                encoding=encoding,
                on_bad_lines='warn',
                engine='python',
                dtype=str
            )
            
            if 'Data/Hora Evento' not in df.columns:
                continue

            if 'Event Code' in df.columns and 'Tipo Mensagem' not in df.columns:
                df['Tipo Mensagem'] = df['Event Code'].map({
                    '21': 'GTIGN',
                    '20': 'GTIGF',
                    '30': 'GTERI',
                    '27': 'GTERI'
                }).fillna('X')

            if 'Tipo Mensagem' not in df.columns:
                continue

            df['Data/Hora Evento'] = pd.to_datetime(
                df['Data/Hora Evento'],
                format='mixed',
                dayfirst=True,
                errors='coerce'
            )

            df = df[~df['Latitude'].isna()].copy()
            df = df[~df['Longitude'].isna()].copy()
            df = df[~df['Data/Hora Evento'].isna()].copy()

            if len(df.columns) > len(set(df.columns)):
                df = df.loc[:, ~df.columns.duplicated()]
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            print(f"Tentativa com encoding {encoding} falhou: {str(e)}")
            continue

    raise ValueError(f"Não foi possível ler o arquivo {path} corretamente")

def classify_message(message: str) -> str:
    """Classifica o tipo de mensagem de forma segura."""
    try:
        message = str(message).strip().upper()
        if message == "GTERI":
            return "T"
        elif message == "GTIGN":
            return "IGN"
        elif message == "GTIGF":
            return "IGF"
        return "X"
    except:
        return "X"

def time_difference_category(delta: float) -> str:
    try:
        delta = float(delta)
        if delta <= 1:
            return "1"
        elif delta <= 5:
            return "5"
        elif delta <= 10:
            return "10"
    except:
        pass
    return None

def find_matches(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    counters = {
        'T1': 0, 'T5': 0, 'T10': 0,
        'IGN1': 0, 'IGN5': 0, 'IGN10': 0,
        'IGF1': 0, 'IGF5': 0, 'IGF10': 0,
        'NA': 0
    }
    
    df1 = df1.copy()
    df2 = df2.copy()
    
    for df in [df1, df2]:
        df['Match_Type'] = 'NA'
        df['Match_ID'] = 0
        df['Distância'] = np.nan
        df['Message_Category'] = df['Tipo Mensagem'].apply(classify_message)
    
    msgs1 = df1[df1['Message_Category'].isin(['T', 'IGN', 'IGF'])].copy()
    msgs2 = df2[df2['Message_Category'].isin(['T', 'IGN', 'IGF'])].copy()
    
    list1 = msgs1.to_dict('records')
    list2 = msgs2.to_dict('records')
    
    used_indices = set()
    
    for i, msg1 in enumerate(list1):
        if i in used_indices:
            continue
        try:
            msg1_time = msg1['Data/Hora Evento'].timestamp()
            msg1_type = msg1['Message_Category']
            best_match = None
            min_diff = float('inf')
            for j, msg2 in enumerate(list2):
                if j in used_indices:
                    continue
                if msg2['Message_Category'] == msg1_type:
                    try:
                        time_diff = abs(msg2['Data/Hora Evento'].timestamp() - msg1_time)
                        if time_diff <= 10 and time_diff < min_diff:
                            min_diff = time_diff
                            best_match = (j, time_diff)
                    except:
                        continue
            if best_match:
                j, diff = best_match
                category = time_difference_category(diff)
                if category:
                    match_type = f"{msg1_type}{category}"
                    counters[match_type] += 1
                    match_id = counters[match_type]

                    # Calcular distância com 2 casas decimais
                    lat1 = float(msg1['Latitude'])
                    lon1 = float(msg1['Longitude'])
                    lat2 = float(list2[j]['Latitude'])
                    lon2 = float(list2[j]['Longitude'])
                    ponto1 = (lat1, lon1)
                    ponto2 = (lat2, lon2)
                    distancia = round(haversine(ponto1, ponto2) * 1000, 2)  # metros

                    # Atualizar listas
                    list1[i]['Match_Type'] = match_type
                    list1[i]['Match_ID'] = match_id
                    list1[i]['Distância'] = distancia
                    list2[j]['Match_Type'] = match_type
                    list2[j]['Match_ID'] = match_id
                    list2[j]['Distância'] = distancia

                    used_indices.add(i)
                    used_indices.add(j)
        except:
            continue
    
    df1.update(pd.DataFrame(list1))
    df2.update(pd.DataFrame(list2))
    
    counters['NA'] = len(df1[df1['Match_Type'] == 'NA']) + len(df2[df2['Match_Type'] == 'NA'])
    
    return df1, df2, counters

def analisar_match(input1: str, input2: str, output_dir: str = None) -> Dict[str, int]: # ""main principal"""
    df1 = load_file(input1) 
    df2 = load_file(input2)

    required = ['Tipo Mensagem', 'Data/Hora Evento', 'Latitude', 'Longitude']
    for df, path in [(df1, input1), (df2, input2)]:
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Arquivo {path} está faltando colunas: {missing}")

    df1, df2, counts = find_matches(df1, df2)

    # Remove 'Tipo Mensagem' antes de salvar - fui usando anteriomente para "normalizar o diferente padrão de mensagens do TM07"
    df1 = df1.drop(columns=['Tipo Mensagem'], errors='ignore')
    df2 = df2.drop(columns=['Tipo Mensagem'], errors='ignore')

    # Determina output
    if output_dir is None:
        output_dir = os.path.dirname(input1)
    output1 = os.path.join(output_dir, os.path.basename(input1).replace('.csv', '_match.csv'))
    output2 = os.path.join(output_dir, os.path.basename(input2).replace('.csv', '_match.csv'))

    df1.to_csv(output1, index=False, encoding='utf-8', errors='replace')
    df2.to_csv(output2, index=False, encoding='utf-8', errors='replace')

    # print(f"✅ Arquivos salvos:\n{output1}\n{output2}")
    # print("✅ Resumo de correspondências:")
    # for k in ['T1', 'T5', 'T10', 'IGN1', 'IGN5', 'IGN10', 'IGF1', 'IGF5', 'IGF10', 'NA']:
    #     print(f"{k}: {counts[k]}")

    return counts


if __name__ == "__main__":
    analisar_match(
        input1='logs/teste.csv',
        input2='logs/teste2.csv'
    )
