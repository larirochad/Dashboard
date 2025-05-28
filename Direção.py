import pandas as pd
import os

def direcao(input1, input2, output_dir=None):
    df1 = pd.read_csv(input1)
    df2 = pd.read_csv(input2)

    if output_dir is None:
        output_dir = os.path.dirname(input1)

    dir_col1 = None # para os nomes de colunas diferentes
    for col in ['Azimuth', 'Heading']:
        if col in df1.columns:
            dir_col1 = col
            break
    if dir_col1 is None:
        raise ValueError("error")

    dir_col2 = None
    for col in ['Azimuth', 'Heading']:
        if col in df2.columns:
            dir_col2 = col
            break
    if dir_col2 is None:
        raise ValueError("error")
    
    df1['chave'] = df1['Match_Type'].astype(str) + '_' + df1['Match_ID'].astype(str) # para garantir a conta com os match T1_1...
    df2['chave'] = df2['Match_Type'].astype(str) + '_' + df2['Match_ID'].astype(str)


    # df1['Diferença Angular'] = None
    # df2['Diferença Angular'] = None

    #common_ids = set(df1['Match_ID']).intersection(set(df2['Match_ID']))
    common_chaves = set(df1['chave']).intersection(set(df2['chave']))


    for chave in common_chaves:
        if chave == '0_0':  # se quiser excluir chave nula
            continue
        try:
            ponto1 = df1[df1['chave'] == chave].iloc[0]
            ponto2 = df2[df2['chave'] == chave].iloc[0]

            ang1 = float(ponto1[dir_col1])
            ang2 = float(ponto2[dir_col2])

            if ang1 > ang2:
                diff_ang = (ang1 - ang2) % 360
            elif ang1 < ang2:
                diff_ang = (ang2 - ang1) % 360
            else:
                diff_ang = 0

            if diff_ang > 180: # para ter o menor caminho 
                diff_ang = 360 - diff_ang

            df1.loc[df1['chave'] == chave, 'Diferença Angular'] = diff_ang
            df2.loc[df2['chave'] == chave, 'Diferença Angular'] = diff_ang

        except Exception as e:
            print(f"Erro ao processar chave {chave}: {e}")
            continue

    df1 = df1.drop(columns=['chave'])
    df2 = df2.drop(columns=['chave'])
        
    output1 = os.path.join(output_dir, os.path.basename(input1).replace('_match1.csv', '_match1_direcao.csv'))
    output2 = os.path.join(output_dir, os.path.basename(input2).replace('_match2.csv', '_match2_direcao.csv'))

    df1.to_csv(output1, index=False, encoding='utf-8', errors='replace')
    df2.to_csv(output2, index=False, encoding='utf-8', errors='replace')


    print(f"✅ Arquivos salvos")
    return df1, df2

if __name__ == "__main__":
    direcao(
        input1 ='logs/test_1_match1.csv',
        input2 ='logs/test_2_match2.csv'
    )
