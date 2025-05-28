import numpy as np
import pandas as pd
import os
from distancia import *
from diff_vel import *
from Direção import *
from match import *


def filtro(teste, input1, input2, output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(input1)

    resultados = []
    dataframes = []
    
    # Padrão para todas
    operacoes = []
    if teste.lower() == 'todas':
        operacoes = ['velocidade', 'direção', 'distância']
    else:
        operacoes = [teste.lower()]
    
    for operacao in operacoes:
        if operacao == 'velocidade':
            df1, df2 = calcular_diferenca_velocidade(input1, input2)
            coluna_resultado = 'Diferença de Velocidade' #nome das novas colunas
        elif operacao == 'direção':
            df1, df2 = direcao(input1, input2)
            coluna_resultado = 'Diferença Angular'
        elif operacao == 'distância':
            df1, df2 = calcular_distancia(input1, input2)
            coluna_resultado = 'Distância'
        else:
            continue  

        df1 = df1[['Match_Type', 'Match_ID', coluna_resultado]]
        dataframes.append((df1, coluna_resultado))

    # Faz merge de todos os DataFrames
    df_merged = dataframes[0][0]
    for df, _ in dataframes[1:]:
        df_merged = pd.merge(df_merged, df, on=['Match_Type', 'Match_ID'], how='outer')

    # Cria coluna combinada
    df_merged['Match_Complete'] = df_merged['Match_Type'].astype(str) + "_" + df_merged['Match_ID'].astype(str)

    output_geral = os.path.join(output_dir, os.path.basename(input1).replace('.csv', '_outputGeral.csv'))
    df_merged.to_csv(output_geral, index=False, encoding='utf-8', errors='replace')

    print(f"✅ Arquivo consolidado salvo: {output_geral}")

    return output_geral, dataframes

def analise_por_match_complete(df, coluna_analise):
    resultados = {}
    grupos_base = sorted(set([m.split('_')[0] for m in df['Match_Complete']]))

    for grupo in grupos_base:
        filtro = df[df['Match_Complete'].str.startswith(grupo)]
        valores = pd.to_numeric(filtro[coluna_analise], errors='coerce').dropna()

        if len(valores) == 0:
            continue  

        media = valores.mean()
        desvio = valores.std()
        soma = valores.sum()
        quantidade = len(valores)

        resultados[grupo] = {
            'media': media,
            'desvio_padrao': desvio,
            'soma': soma,
            'quantidade': quantidade
        }
    
    return resultados

if __name__ == "__main__":

    match1, match2, counts = analisar_match(
        input1='logs/test_1.csv',
        input2='logs/test_2.csv'
    )

    output_geral, dataframes = filtro(
        teste='todas',
        input1= match1,
        input2= match2
    )

    df = pd.read_csv(output_geral)

    ####### transformar em um codigo a mais
    for _, coluna_resultado in dataframes:
        print(f"\n🔹 Análise estatística para {coluna_resultado}:")
        resultado = analise_por_match_complete(df, coluna_resultado) # passa o arquivo output_geral + as colunas que foram adicionadas

        for grupo, stats in resultado.items():
            print(f"\nGrupo: {grupo}")
            print(f"Média: {stats['media']}")
            print(f"Desvio Padrão: {stats['desvio_padrao']}")
            print(f"Soma: {stats['soma']}")
            print(f"Quantidade: {stats['quantidade']}")

    base1, ext1 = os.path.splitext(match1)
    base2, ext2 = os.path.splitext(match2)

    arquivos_temp = [match1,match2, base1 + '_velocidade.csv',base1 + '_direcao.csv',base1 + '_distancia.csv',base2 + '_velocidade.csv',base2 + '_direcao.csv',base2 + '_distancia.csv' ]

    for arq in arquivos_temp:
        if os.path.exists(arq):
            os.remove(arq)
            print(f"✅ Arquivo temporário deletado: {arq}")

