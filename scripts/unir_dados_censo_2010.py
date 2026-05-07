"""
Script para unir dados do Censo 2010 (renda) com geometria dos setores censitários 2022

União dos arquivos:
- Basico_SP1.csv (São Paulo Capital) - Censo 2010
- Basico_SP2.csv (SP Exceto Capital) - Censo 2010
- SP_setores_CD2022.gpkg - Geometria dos setores 2022

A coluna V05 contém o valor da renda mensal média.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import sys

def unir_dados_censo():
    """Unir dados de renda do Censo 2010 com geometria dos setores 2022"""
    
    # Caminhos dos arquivos
    base_path = Path("C:/Users/caioy/Documents/GitHub/caioyamamoto.github.io/assets/data")
    
    csv1_path = base_path / "SP_Capital_20231030/Base informaçoes setores2010 universo SP_Capital/CSV/Basico_SP1.csv"
    csv2_path = base_path / "SP_Exceto_Capital_20231030/Base informaçoes setores2010 universo SP_Exceto_Capital/CSV/Basico_SP2.csv"
    # Usar setores de 2010 para melhor compatibilidade com dados do Censo 2010
    shp_path = base_path / "sp_setores_censitarios/35SEE250GC_SIR.shp"
    output_path = base_path / "setores_sp_com_renda_2010.gpkg"
    
    print("=== Unindo dados do Censo 2010 com geometria dos setores 2010 ===\n")
    
    # Verificar se arquivos existem
    for path in [csv1_path, csv2_path, shp_path]:
        if not path.exists():
            print(f"✗ Arquivo não encontrado: {path}")
            sys.exit(1)
        print(f"✓ Encontrado: {path.name}")
    
    # Ler CSVs do Censo 2010
    print("\n1. Lendo dados do Censo 2010...")
    
    # Ler CSVs (encoding latin-1 é comum em arquivos do IBGE)
    try:
        df1 = pd.read_csv(csv1_path, encoding='latin-1', sep=';')
        print(f"   ✓ Basico_SP1.csv: {len(df1)} registros")
    except Exception as e:
        print(f"   ✗ Erro ao ler Basico_SP1.csv: {e}")
        df1 = pd.read_csv(csv1_path, encoding='utf-8', sep=';')
        print(f"   ✓ Basico_SP1.csv (UTF-8): {len(df1)} registros")
    
    try:
        df2 = pd.read_csv(csv2_path, encoding='latin-1', sep=';')
        print(f"   ✓ Basico_SP2.csv: {len(df2)} registros")
    except Exception as e:
        print(f"   ✗ Erro ao ler Basico_SP2.csv: {e}")
        df2 = pd.read_csv(csv2_path, encoding='utf-8', sep=';')
        print(f"   ✓ Basico_SP2.csv (UTF-8): {len(df2)} registros")
    
    # Unir os dois DataFrames
    print("\n2. Unindo dados da Capital e Interior...")
    df_total = pd.concat([df1, df2], ignore_index=True)
    print(f"   Total de registros: {len(df_total)}")
    
    # Mostrar colunas disponíveis
    print(f"\n3. Colunas disponíveis no CSV:")
    for i, col in enumerate(df_total.columns):
        print(f"   {i+1}. {col}")
    
    # Identificar coluna de código do setor e V05 (renda)
    # Normalmente o código está na coluna 'Cod_setor' ou similar
    cod_col = None
    for col in df_total.columns:
        if 'cod' in col.lower() and 'setor' in col.lower():
            cod_col = col
            break
        elif col.lower() in ['cd_setor', 'cd_setor_censitario', 'id_setor']:
            cod_col = col
            break
    
    if not cod_col:
        cod_col = df_total.columns[0]  # Primeira coluna como fallback
        print(f"\n⚠ Usando primeira coluna como código do setor: {cod_col}")
    else:
        print(f"\n✓ Coluna de código do setor: {cod_col}")
    
    # Verificar se colunas V002 (população) e V005 (renda) existem
    if 'V002' not in df_total.columns:
        print("\n✗ Coluna V002 (população) não encontrada!")
        print("Colunas disponíveis:", df_total.columns.tolist())
        sys.exit(1)
    
    if 'V005' not in df_total.columns:
        print("\n✗ Coluna V005 (renda) não encontrada!")
        print("Colunas disponíveis:", df_total.columns.tolist())
        sys.exit(1)
    
    print(f"✓ Coluna de população (V002) encontrada")
    print(f"✓ Coluna de renda (V005) encontrada")
    
    # Limpar e converter código do setor
    print("\n4. Processando códigos dos setores...")
    df_total[cod_col] = df_total[cod_col].astype(str).str.strip()
    
    # Remover possíveis .0 no final (quando número é lido como float)
    df_total[cod_col] = df_total[cod_col].str.replace(r'\.0$', '', regex=True)
    
    # Converter V002 e V005 para número
    print("\n5. Processando valores de população e renda...")
    
    # V002 = População
    df_total['V002'] = df_total['V002'].astype(str).str.replace(',', '.')
    df_total['POPULACAO'] = pd.to_numeric(df_total['V002'], errors='coerce')
    
    # V005 = Renda
    df_total['V005'] = df_total['V005'].astype(str).str.replace(',', '.')
    df_total['RENDA_MEDIA_2010'] = pd.to_numeric(df_total['V005'], errors='coerce')
    
    # Estatísticas da população
    valid_pop = df_total['POPULACAO'].dropna()
    print(f"   População - Registros válidos: {len(valid_pop)}/{len(df_total)}")
    if len(valid_pop) > 0:
        print(f"   População total: {valid_pop.sum():,.0f}")
        print(f"   Média por setor: {valid_pop.mean():.0f}")
    
    # Estatísticas da renda
    valid_renda = df_total['RENDA_MEDIA_2010'].dropna()
    print(f"\n   Renda - Registros válidos: {len(valid_renda)}/{len(df_total)}")
    if len(valid_renda) > 0:
        print(f"   Renda média: R$ {valid_renda.mean():.2f}")
        print(f"   Renda mediana: R$ {valid_renda.median():.2f}")
        print(f"   Mín: R$ {valid_renda.min():.2f} | Máx: R$ {valid_renda.max():.2f}")
    
    # Ler shapefile dos setores 2010
    print(f"\n6. Lendo geometria dos setores 2010...")
    gdf_setores = gpd.read_file(shp_path)
    print(f"   ✓ Setores 2010: {len(gdf_setores)} registros")
    print(f"   Colunas: {list(gdf_setores.columns)}")
    
    # Identificar coluna de código no GPKG
    cod_col_gpkg = None
    for col in gdf_setores.columns:
        if 'cod' in col.lower() and 'setor' in col.lower():
            cod_col_gpkg = col
            break
        elif col.lower() in ['cd_setor', 'cd_setor_censitario', 'id_setor', 'cd_geocodi']:
            cod_col_gpkg = col
            break
    
    if not cod_col_gpkg:
        cod_col_gpkg = gdf_setores.columns[0]
        print(f"\n⚠ Usando primeira coluna como código: {cod_col_gpkg}")
    else:
        print(f"\n✓ Coluna de código no GPKG: {cod_col_gpkg}")
    
    # Limpar código no GPKG
    gdf_setores[cod_col_gpkg] = gdf_setores[cod_col_gpkg].astype(str).str.strip()
    gdf_setores[cod_col_gpkg] = gdf_setores[cod_col_gpkg].str.replace(r'\.0$', '', regex=True)
    
    # Fazer o merge
    print(f"\n7. Unindo dados de renda com geometria...")
    
    # Selecionar apenas colunas necessárias do CSV
    df_merge = df_total[[cod_col, 'POPULACAO', 'RENDA_MEDIA_2010']].copy()
    df_merge = df_merge.dropna(subset=['RENDA_MEDIA_2010'])
    
    print(f"   Registros CSV com renda válida: {len(df_merge)}")
    print(f"   Registros shapefile 2010: {len(gdf_setores)}")
    
    # Merge
    gdf_final = gdf_setores.merge(
        df_merge,
        left_on=cod_col_gpkg,
        right_on=cod_col,
        how='left'
    )
    
    # Calcular área em km²
    print(f"\n8. Calculando área dos setores...")
    # Verificar e converter CRS se necessário
    if gdf_final.crs is None:
        print("   ⚠ CRS não definido, assumindo SIRGAS 2000 (EPSG:4674)")
        gdf_final = gdf_final.set_crs(epsg=4674)
    
    # Converter para CRS projetado para cálculo de área (UTM zona 23S)
    gdf_final_utm = gdf_final.to_crs(epsg=31983)
    # Calcular área em km²
    gdf_final_utm['AREA_KM2'] = gdf_final_utm['geometry'].area / 1_000_000
    
    # Copiar área para o GeoDataFrame original
    gdf_final['AREA_KM2'] = gdf_final_utm['AREA_KM2']
    
    print(f"   ✓ Área calculada para {gdf_final['AREA_KM2'].notna().sum()} setores")
    print(f"   Área total: {gdf_final['AREA_KM2'].sum():.2f} km²")
    
    # Calcular densidade demográfica
    print(f"\n9. Calculando densidade demográfica...")
    gdf_final['DENSIDADE'] = gdf_final['POPULACAO'] / gdf_final['AREA_KM2']
    # Substituir inf/NaN por 0
    gdf_final['DENSIDADE'] = gdf_final['DENSIDADE'].replace([float('inf'), -float('inf')], float('nan'))
    
    valid_densidade = gdf_final['DENSIDADE'].notna().sum()
    print(f"   ✓ Densidade calculada para {valid_densidade} setores")
    if valid_densidade > 0:
        print(f"   Densidade média: {gdf_final['DENSIDADE'].mean():.0f} hab/km²")
        print(f"   Densidade mediana: {gdf_final['DENSIDADE'].median():.0f} hab/km²")
    
    # Estatísticas do merge
    com_renda = gdf_final['RENDA_MEDIA_2010'].notna().sum()
    sem_renda = gdf_final['RENDA_MEDIA_2010'].isna().sum()
    
    print(f"\n10. Resultado do merge:")
    print(f"   ✓ Setores com renda: {com_renda} ({com_renda/len(gdf_final)*100:.1f}%)")
    print(f"   ✗ Setores sem renda: {sem_renda} ({sem_renda/len(gdf_final)*100:.1f}%)")
    
    # Calcular estatísticas de renda nos setores que deram match
    if com_renda > 0:
        renda_match = gdf_final[gdf_final['RENDA_MEDIA_2010'].notna()]['RENDA_MEDIA_2010']
        print(f"\n   Estatísticas de renda (setores com match):")
        print(f"   - Média: R$ {renda_match.mean():.2f}")
        print(f"   - Mediana: R$ {renda_match.median():.2f}")
        print(f"   - Desvio padrão: R$ {renda_match.std():.2f}")
    
    # Estatísticas de população
    com_pop = gdf_final['POPULACAO'].notna().sum()
    if com_pop > 0:
        pop_match = gdf_final[gdf_final['POPULACAO'].notna()]['POPULACAO']
        print(f"\n   Estatísticas de população (setores com match):")
        print(f"   - Total: {pop_match.sum():,.0f}")
        print(f"   - Média por setor: {pop_match.mean():.0f}")
    
    # Salvar resultado
    print(f"\n11. Salvando resultado...")
    gdf_final.to_file(output_path, driver='GPKG')
    print(f"   ✓ Arquivo salvo: {output_path}")
    
    # Também salvar como GeoJSON para uso no mapa
    output_geojson = output_path.with_suffix('.geojson')
    
    # Simplificar geometria para GeoJSON
    print(f"\n12. Criando versão GeoJSON simplificada...")
    gdf_simplified = gdf_final.copy()
    gdf_simplified['geometry'] = gdf_simplified['geometry'].simplify(tolerance=0.0001, preserve_topology=True)
    
    # Selecionar apenas colunas essenciais para o GeoJSON
    cols_essenciais = [cod_col_gpkg, 'POPULACAO', 'RENDA_MEDIA_2010', 'AREA_KM2', 'DENSIDADE', 'geometry']
    cols_existentes = [c for c in cols_essenciais if c in gdf_simplified.columns]
    
    # Adicionar outras colunas úteis se existirem
    for col in ['CD_SETOR', 'NM_DISTRIT', 'NM_MUNICIP']:
        if col in gdf_simplified.columns and col not in cols_existentes:
            cols_existentes.append(col)
    
    gdf_geojson = gdf_simplified[cols_existentes].copy()
    
    # Remover geometrias nulas
    gdf_geojson = gdf_geojson[gdf_geojson['geometry'].notna()]
    
    gdf_geojson.to_file(output_geojson, driver='GeoJSON')
    print(f"   ✓ GeoJSON salvo: {output_geojson}")
    print(f"   Tamanho: {output_geojson.stat().st_size / (1024*1024):.1f} MB")
    
    print("\n=== Processo concluído com sucesso! ===")
    return gdf_final

if __name__ == "__main__":
    unir_dados_censo()
