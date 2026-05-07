"""
Script para unir dados da malha censitária (área e população) com setores existentes

Fonte: Dicionario_de_dados_malha_agregados.xlsx
Colunas: CD_SETOR, AREA_KM2, V0001 (população)
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import sys

def unir_dados_malha():
    """Unir dados de área e população da malha censitária"""
    
    # Caminhos dos arquivos
    base_path = Path("C:/Users/caioy/Documents/GitHub/caioyamamoto.github.io/assets/data")
    
    excel_path = base_path / "Dicionario_de_dados_malha_agregados.xlsx"
    geojson_path = base_path / "setores_sp_com_renda_2010.geojson"
    output_path = base_path / "setores_sp_completo.geojson"
    
    print("=== Unindo dados da malha censitária (área e população) ===\n")
    
    # Verificar se arquivos existem
    for path in [excel_path, geojson_path]:
        if not path.exists():
            print(f"✗ Arquivo não encontrado: {path}")
            sys.exit(1)
        print(f"✓ Encontrado: {path.name}")
    
    # Ler planilha Excel
    print("\n1. Lendo planilha Excel...")
    try:
        df_excel = pd.read_excel(excel_path)
        print(f"   ✓ Planilha lida: {len(df_excel)} registros")
        print(f"   Colunas: {list(df_excel.columns)}")
    except Exception as e:
        print(f"   ✗ Erro ao ler Excel: {e}")
        sys.exit(1)
    
    # Identificar colunas necessárias
    # Procurar por CD_SETOR ou similar
    cod_col = None
    for col in df_excel.columns:
        if 'cd' in col.lower() and 'setor' in col.lower():
            cod_col = col
            break
        elif col.lower() in ['cd_setor', 'cd_geocodi', 'geocodigo']:
            cod_col = col
            break
    
    if not cod_col:
        print("\n✗ Coluna de código do setor não encontrada!")
        print(f"Colunas disponíveis: {list(df_excel.columns)}")
        sys.exit(1)
    
    print(f"\n✓ Coluna de código: {cod_col}")
    
    # Verificar colunas AREA_KM2 e V0001
    area_col = None
    pop_col = None
    
    for col in df_excel.columns:
        col_lower = col.lower()
        if 'area' in col_lower and 'km' in col_lower:
            area_col = col
        elif col_lower == 'area_km2':
            area_col = col
        elif col_lower in ['v0001', 'v001', 'populacao', 'pop']:
            pop_col = col
    
    if not area_col:
        print("\n⚠ Coluna AREA_KM2 não encontrada, procurando alternativas...")
        for col in df_excel.columns:
            if 'area' in col.lower():
                area_col = col
                print(f"   Usando: {area_col}")
                break
    else:
        print(f"✓ Coluna de área: {area_col}")
    
    if not pop_col:
        print("\n⚠ Coluna V0001 não encontrada, procurando alternativas...")
        for col in df_excel.columns:
            if 'v001' in col.lower() or 'pop' in col.lower():
                pop_col = col
                print(f"   Usando: {pop_col}")
                break
    else:
        print(f"✓ Coluna de população: {pop_col}")
    
    # Selecionar e renomear colunas
    cols_selecionadas = [cod_col]
    if area_col:
        cols_selecionadas.append(area_col)
    if pop_col:
        cols_selecionadas.append(pop_col)
    
    df_merge = df_excel[cols_selecionadas].copy()
    
    # Renomear para nomes padronizados
    df_merge = df_merge.rename(columns={
        cod_col: 'CD_SETOR_EXCEL',
        area_col: 'AREA_KM2_EXCEL' if area_col else None,
        pop_col: 'POPULACAO_EXCEL' if pop_col else None
    })
    
    # Limpar colunas None
    df_merge = df_merge[[c for c in df_merge.columns if c is not None]]
    
    # Converter código para string
    df_merge['CD_SETOR_EXCEL'] = df_merge['CD_SETOR_EXCEL'].astype(str).str.strip()
    df_merge['CD_SETOR_EXCEL'] = df_merge['CD_SETOR_EXCEL'].str.replace(r'\.0$', '', regex=True)
    
    print(f"\n2. Dados da planilha preparados:")
    print(f"   Registros: {len(df_merge)}")
    if 'AREA_KM2_EXCEL' in df_merge.columns:
        print(f"   Área (amostra): {df_merge['AREA_KM2_EXCEL'].dropna().head(3).tolist()}")
    if 'POPULACAO_EXCEL' in df_merge.columns:
        print(f"   População (amostra): {df_merge['POPULACAO_EXCEL'].dropna().head(3).tolist()}")
    
    # Ler GeoJSON existente
    print(f"\n3. Lendo GeoJSON existente...")
    gdf = gpd.read_file(geojson_path)
    print(f"   ✓ GeoJSON: {len(gdf)} setores")
    print(f"   Colunas: {list(gdf.columns)}")
    
    # Identificar coluna de código no GeoJSON
    cod_col_geo = None
    for col in gdf.columns:
        if col.lower() in ['cd_geocodi', 'cd_setor', 'geocodigo']:
            cod_col_geo = col
            break
    
    if not cod_col_geo:
        cod_col_geo = gdf.columns[0]
        print(f"\n⚠ Usando primeira coluna como código: {cod_col_geo}")
    else:
        print(f"\n✓ Coluna de código no GeoJSON: {cod_col_geo}")
    
    # Limpar código no GeoJSON
    gdf[cod_col_geo] = gdf[cod_col_geo].astype(str).str.strip()
    gdf[cod_col_geo] = gdf[cod_col_geo].str.replace(r'\.0$', '', regex=True)
    
    # Fazer merge
    print(f"\n4. Unindo dados...")
    gdf_final = gdf.merge(
        df_merge,
        left_on=cod_col_geo,
        right_on='CD_SETOR_EXCEL',
        how='left'
    )
    
    # Estatísticas do merge
    if 'AREA_KM2_EXCEL' in gdf_final.columns:
        com_area = gdf_final['AREA_KM2_EXCEL'].notna().sum()
        print(f"   Setores com área da planilha: {com_area} ({com_area/len(gdf_final)*100:.1f}%)")
    
    if 'POPULACAO_EXCEL' in gdf_final.columns:
        com_pop = gdf_final['POPULACAO_EXCEL'].notna().sum()
        print(f"   Setores com população da planilha: {com_pop} ({com_pop/len(gdf_final)*100:.1f}%)")
    
    # Atualizar colunas existentes ou criar novas
    print(f"\n5. Atualizando colunas no GeoDataFrame...")
    
    if 'AREA_KM2_EXCEL' in gdf_final.columns:
        # Priorizar área da planilha, usar existente como fallback
        if 'AREA_KM2' in gdf_final.columns:
            gdf_final['AREA_KM2'] = gdf_final['AREA_KM2_EXCEL'].fillna(gdf_final['AREA_KM2'])
        else:
            gdf_final['AREA_KM2'] = gdf_final['AREA_KM2_EXCEL']
        print(f"   ✓ AREA_KM2 atualizada")
    
    if 'POPULACAO_EXCEL' in gdf_final.columns:
        # Priorizar população da planilha, usar existente como fallback
        if 'POPULACAO' in gdf_final.columns:
            gdf_final['POPULACAO'] = gdf_final['POPULACAO_EXCEL'].fillna(gdf_final['POPULACAO'])
        else:
            gdf_final['POPULACAO'] = gdf_final['POPULACAO_EXCEL']
        print(f"   ✓ POPULACAO atualizada")
    
    # Calcular densidade se tivermos população e área
    if 'POPULACAO' in gdf_final.columns and 'AREA_KM2' in gdf_final.columns:
        gdf_final['DENSIDADE'] = gdf_final['POPULACAO'] / gdf_final['AREA_KM2'].replace(0, float('nan'))
        print(f"   ✓ DENSIDADE calculada")
    
    # Remover colunas temporárias
    cols_remover = [c for c in gdf_final.columns if c.endswith('_EXCEL') or c == 'CD_SETOR_EXCEL']
    gdf_final = gdf_final.drop(columns=cols_remover)
    
    # Salvar resultado
    print(f"\n6. Salvando resultado...")
    gdf_final.to_file(output_path, driver='GeoJSON')
    print(f"   ✓ Arquivo salvo: {output_path}")
    print(f"   Tamanho: {output_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Estatísticas finais
    print(f"\n=== Resumo ===")
    print(f"   Total de setores: {len(gdf_final)}")
    if 'POPULACAO' in gdf_final.columns:
        pop_total = gdf_final['POPULACAO'].sum()
        print(f"   População total: {pop_total:,.0f}")
    if 'AREA_KM2' in gdf_final.columns:
        area_total = gdf_final['AREA_KM2'].sum()
        print(f"   Área total: {area_total:,.2f} km²")
    if 'DENSIDADE' in gdf_final.columns:
        dens_media = gdf_final['DENSIDADE'].mean()
        print(f"   Densidade média: {dens_media:,.0f} hab/km²")
    
    print("\n=== Processo concluído com sucesso! ===")
    return gdf_final

if __name__ == "__main__":
    unir_dados_malha()
