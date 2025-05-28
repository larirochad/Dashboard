import pandas as pd
from datetime import datetime
import os
from typing import Dict, Tuple
# sem a distancia 
def match(path: str) -> pd.DataFrame:
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

            df = df.dropna(subset=['Latitude', 'Longitude', 'Data/Hora Evento'])

            if len(df.columns) > len(set(df.columns)):
                df = df.loc[:, ~df.columns.duplicated()]

            return df.reset_index(drop=True)
            
        except Exception as e:
            #print(f"Tentativa com encoding {encoding} falhou: {str(e)}")
            continue

    raise ValueError(f"Não foi possível ler o arquivo {path} corretamente")

def classify_message(message: str) -> str:
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

                    list1[i]['Match_Type'] = match_type
                    list1[i]['Match_ID'] = match_id
                    list2[j]['Match_Type'] = match_type
                    list2[j]['Match_ID'] = match_id

                    used_indices.add(i)
                    used_indices.add(j)
        except:
            continue
    
    df1.update(pd.DataFrame(list1))
    df2.update(pd.DataFrame(list2))
    
    counters['NA'] = len(df1[df1['Match_Type'] == 'NA']) + len(df2[df2['Match_Type'] == 'NA'])
    
    return df1, df2, counters

def analisar_match(input1: str, input2: str, output_dir: str = None) -> Dict[str, int]:
    df1 = match(input1)
    df2 = match(input2)

    required = ['Tipo Mensagem', 'Data/Hora Evento', 'Latitude', 'Longitude', 'GNSS UTC Time']
    for df, path in [(df1, input1), (df2, input2)]:
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Arquivo {path} está faltando colunas: {missing}")

    df1, df2, counts = find_matches(df1, df2)

    df1 = df1.drop(columns=['Tipo Mensagem'], errors='ignore')
    df2 = df2.drop(columns=['Tipo Mensagem'], errors='ignore')

   
    for df in [df1, df2]:
        df['GNSS UTC Time'] = pd.to_datetime(df['GNSS UTC Time'], errors='coerce')
        df['Tempo de fix'] = (df['Data/Hora Evento'] - df['GNSS UTC Time']).dt.total_seconds()

    # Criar chave para match
    df1['match_key'] = df1['Match_Type'].astype(str) + '_' + df1['Match_ID'].astype(str)
    df2['match_key'] = df2['Match_Type'].astype(str) + '_' + df2['Match_ID'].astype(str)

    # Merge dos matches
    matches = pd.merge(
        df1[['match_key', 'Tempo de fix']],
        df2[['match_key', 'Tempo de fix']],
        on='match_key',
        suffixes=('_1', '_2')
    )

    # Calcular delta
    matches['Delta Tempo de Fix'] = (matches['Tempo de fix_1'] - matches['Tempo de fix_2']).abs()

    df1 = df1.merge(matches[['match_key', 'Delta Tempo de Fix']], on='match_key', how='left')
    df2 = df2.merge(matches[['match_key', 'Delta Tempo de Fix']], on='match_key', how='left')



    if output_dir is None:
        output_dir = os.path.dirname(input1)
    output1 = os.path.join(output_dir, os.path.basename(input1).replace('.csv', '_match1.csv'))
    output2 = os.path.join(output_dir, os.path.basename(input2).replace('.csv', '_match2.csv'))

    df1.to_csv(output1, index=False, encoding='utf-8', errors='replace')
    df2.to_csv(output2, index=False, encoding='utf-8', errors='replace')

    print(f"✅ Arquivos salvos")

    return output1, output2, counts

if __name__ == "__main__":
    analisar_match(
        input1='logs/test_1.csv',
        input2='logs/test_2.csv'
    )
