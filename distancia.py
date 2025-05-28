
import pandas as pd
import os
from haversine import haversine # biblioteca para calcular a distancia, precisa ser baixada

def calcular_distancia(input1: str, input2: str, output_dir: str = None):
    df1 = pd.read_csv(input1)
    df2 = pd.read_csv(input2)

    if output_dir is None:
        output_dir = os.path.dirname(input1)

            
    df1['Distância'] = None
    df2['Distância'] = None


    df1['chave'] = df1['Match_Type'].astype(str) + '_' + df1['Match_ID'].astype(str) # para garantir a conta com os match T1_1...
    df2['chave'] = df2['Match_Type'].astype(str) + '_' + df2['Match_ID'].astype(str)


    common_chaves = set(df1['chave']).intersection(set(df2['chave']))
    for chave in common_chaves:
        if chave == 0:
            continue
        try:
            ponto1 = df1[df1['chave'] == chave].iloc[0]
            ponto2 = df2[df2['chave'] == chave].iloc[0]

            lat1, lon1 = float(ponto1['Latitude']), float(ponto1['Longitude'])
            lat2, lon2 = float(ponto2['Latitude']), float(ponto2['Longitude'])

            distancia = round(haversine((lat1, lon1), (lat2, lon2)) * 1000, 2) # *1000 Para metro

            df1.loc[df1['chave'] == chave, 'Distância'] = distancia
            df2.loc[df2['chave'] == chave, 'Distância'] = distancia
        except:
            continue

    df1 = df1.drop(columns=['chave'])
    df2 = df2.drop(columns=['chave'])
    
    output1 = os.path.join(output_dir, os.path.basename(input1).replace('_match1.csv', '_match1_distancia.csv')) #deixar _match para salvar na mesma tabela de entrada
    output2 = os.path.join(output_dir, os.path.basename(input2).replace('_match2.csv', '_match2_distancia.csv'))

    df1.to_csv(output1, index=False, encoding='utf-8', errors='replace')
    df2.to_csv(output2, index=False, encoding='utf-8', errors='replace')


    print(f"✅ Arquivos salvos")
    return df1, df2



if __name__ == "__main__":
    calcular_distancia(
        input1='logs/test_1_match1.csv',
        input2='logs/test_2_match2.csv'
    )
