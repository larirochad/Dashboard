import pandas as pd
import os

def calcular_diferenca_velocidade(input1: str, input2: str, output_dir: str = None):
    df1 = pd.read_csv(input1)
    df2 = pd.read_csv(input2)

    if output_dir is None:
        output_dir = os.path.dirname(input1)

    if 'Velocidade' not in df1.columns or 'Velocidade' not in df2.columns:
        raise ValueError("error")

    df1['chave'] = df1['Match_Type'].astype(str) + '_' + df1['Match_ID'].astype(str) # para garantir a conta com os match T1_1...
    df2['chave'] = df2['Match_Type'].astype(str) + '_' + df2['Match_ID'].astype(str)

    ref_dict = df2.set_index('chave')['Velocidade'].to_dict()

    # df1['Diferença de Velocidade'] = None
    # df2['Diferença de Velocidade'] = None

    for idx, row in df1.iterrows():
        chave = row['chave']
        vel_teste = row['Velocidade']

        if chave in ref_dict:
            vel_ref = ref_dict[chave]
            diferenca = vel_ref - vel_teste
            df1.at[idx, 'Diferença de Velocidade'] = round(diferenca, 2)
            # Para df2, encontra o índice correspondente
            idx2 = df2.index[df2['chave'] == chave]
            df2.loc[idx2, 'Diferença de Velocidade'] = round(diferenca, 2)

    df1 = df1.drop(columns=['chave'])
    df2 = df2.drop(columns=['chave'])

    output1 = os.path.join(output_dir, os.path.basename(input1).replace('_match1.csv', '_match1_velocidade.csv'))
    output2 = os.path.join(output_dir, os.path.basename(input2).replace('_match2.csv', '_match2_velocidade.csv'))

    df1.to_csv(output1, index=False, encoding='utf-8', errors='replace')
    df2.to_csv(output2, index=False, encoding='utf-8', errors='replace')

    print(f"✅ Arquivos salvos")

    return df1, df2

if __name__ == "__main__":
    calcular_diferenca_velocidade(
        input1='logs/test_1_match1.csv',
        input2='logs/test_2_match2.csv'
    )
