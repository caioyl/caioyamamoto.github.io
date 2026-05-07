#!/usr/bin/env python3
"""
Download e processamento de dados censitários do IBGE para São Paulo
Gera: assets/data/setores_sp.geojson

Uso:
    pip install -r requirements.txt
    python download_censo_sp.py

Opções:
    --api      : Usar geobr (mais fácil, mas pode ser lento)
    --url      : Tentar URLs alternativas do IBGE
    --sample   : Criar dados simulados de exemplo
"""

import os
import sys
import json
import zipfile
import requests
import argparse
from pathlib import Path

# Tentar importar bibliotecas opcionais
try:
    import geopandas as gpd
    import pandas as pd
    import numpy as np
    HAS_GEO = True
except ImportError:
    HAS_GEO = False
    print("Aviso: geopandas/pandas não instalados. Instale com: pip install -r requirements.txt")

# Configurações - URLs alternativas do IBGE (podem mudar)
IBGE_URLS = [
    # Malhas municipais 2022 - SP
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/SP/SP_Malhas_2022.zip",
    # Malhas simplificadas
    "https://geoftp.ibge.gov.br/cartas_e_mapas/mapas_tematicos/simplificado/malhas_estaduais/SP_Malhas_2022_simplificado.zip",
]

# Dados do Censo
CENSO_URLS = [
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setores_Censitarios_csv/Agregados_por_setores_2022_CSV_RMSP.zip",
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setores_Censitarios_xlsx/Agregados_por_setores_2022_XLSX_RMSP.zip",
]

OUTPUT_DIR = Path("assets/data")
TEMP_DIR = Path("temp")

def download_file(url, destino, chunk_size=8192):
    """Download com progresso"""
    print(f"\nBaixando: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Progresso: {percent:.1f}% ({downloaded/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB)", end='')
        
        print(f"\n✓ Salvo: {destino} ({downloaded/(1024*1024):.1f} MB)")
        return True
    except Exception as e:
        print(f"\n✗ Erro no download: {e}")
        return False

def extrair_zip(arquivo, destino):
    """Extrair arquivo ZIP"""
    print(f"Extraindo: {arquivo.name}")
    try:
        with zipfile.ZipFile(arquivo, 'r') as zip_ref:
            zip_ref.extractall(destino)
        print(f"✓ Extraído em: {destino}")
        return True
    except Exception as e:
        print(f"✗ Erro na extração: {e}")
        return False

def find_shapefile(diretorio):
    """Encontrar arquivo .shp no diretório"""
    shp_files = list(diretorio.rglob("*.shp"))
    if shp_files:
        return shp_files[0]
    return None

def find_xlsx(diretorio):
    """Encontrar arquivo Excel com dados"""
    xlsx_files = list(diretorio.rglob("*.xlsx")) + list(diretorio.rglob("*.xls"))
    # Filtrar arquivos que contenham "setor" no nome
    for f in xlsx_files:
        if 'setor' in f.name.lower():
            return f
    if xlsx_files:
        return xlsx_files[0]
    return None

def processar_dados():
    """Processar e mesclar geometria + atributos"""
    
    if not HAS_GEO:
        print("\n✗ Bibliotecas geoespaciais não instaladas.")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    # 1. Carregar geometria dos setores
    print("\n1. Carregando geometria dos setores...")
    shp_path = find_shapefile(TEMP_DIR)
    
    if not shp_path:
        print("✗ Arquivo shapefile não encontrado!")
        return None
    
    print(f"   Encontrado: {shp_path}")
    gdf = gpd.read_file(shp_path)
    print(f"   Total de setores: {len(gdf)}")
    
    # Verificar colunas disponíveis
    print(f"   Colunas: {list(gdf.columns)}")
    
    # Simplificar geometria (reduzir vértices para web)
    print("\n2. Simplificando geometria...")
    gdf['geometry'] = gdf.geometry.simplify(tolerance=0.0001, preserve_topology=True)
    
    # Calcular área em km²
    gdf = gdf.to_crs(epsg=31983)  # SIRGAS 2000 / UTM zone 23S (São Paulo)
    gdf['AREA_KM2'] = gdf.geometry.area / 1_000_000
    gdf = gdf.to_crs(epsg=4326)  # Voltar para WGS84
    
    # 2. Tentar carregar dados do Censo
    print("\n3. Procurando dados censitários...")
    xlsx_path = find_xlsx(TEMP_DIR)
    
    if xlsx_path:
        print(f"   Encontrado: {xlsx_path}")
        try:
            # Ler todas as abas ou a primeira
            xl = pd.ExcelFile(xlsx_path)
            print(f"   Abas disponíveis: {xl.sheet_names}")
            
            # Tentar encontrar aba com dados dos setores
            sheet_name = None
            for name in xl.sheet_names:
                if 'setor' in name.lower() or 'dados' in name.lower():
                    sheet_name = name
                    break
            if not sheet_name and xl.sheet_names:
                sheet_name = xl.sheet_names[0]
            
            print(f"   Lendo aba: {sheet_name}")
            df_censo = pd.read_excel(xlsx_path, sheet_name=sheet_name)
            print(f"   Registros no Censo: {len(df_censo)}")
            print(f"   Colunas: {list(df_censo.columns[:10])}...")
            
            # Identificar coluna de código do setor
            cod_col = None
            for col in df_censo.columns:
                if 'setor' in col.lower() or 'cd_' in col.lower() or 'codigo' in col.lower():
                    cod_col = col
                    break
            
            if cod_col:
                print(f"   Coluna de código: {cod_col}")
                
                # Normalizar códigos para merge
                gdf['CD_SETOR_STR'] = gdf['CD_SETOR'].astype(str).str.strip()
                df_censo[cod_col] = df_censo[cod_col].astype(str).str.strip()
                
                # Merge
                print("\n4. Mesclando geometria e dados...")
                gdf_merged = gdf.merge(df_censo, left_on='CD_SETOR_STR', right_on=cod_col, how='left')
                
                # Tentar identificar coluna de população
                pop_col = None
                for col in df_censo.columns:
                    if 'populacao' in col.lower() or 'pessoas' in col.lower() or 'v0001' in col.lower():
                        pop_col = col
                        break
                
                if pop_col:
                    gdf_merged['POPULACAO'] = pd.to_numeric(gdf_merged[pop_col], errors='coerce').fillna(0)
                    print(f"   Usando população da coluna: {pop_col}")
                else:
                    # Criar população simulada para teste
                    print("   Coluna de população não identificada, usando valores simulados")
                    gdf_merged['POPULACAO'] = (gdf_merged['AREA_KM2'] * 5000).astype(int)
            else:
                print("   Coluna de código não encontrada, usando dados simulados")
                gdf_merged = gdf.copy()
                gdf_merged['POPULACAO'] = (gdf_merged['AREA_KM2'] * 5000).astype(int)
                
        except Exception as e:
            print(f"   Erro ao ler dados: {e}")
            gdf_merged = gdf.copy()
            gdf_merged['POPULACAO'] = (gdf_merged['AREA_KM2'] * 5000).astype(int)
    else:
        print("   Arquivo de dados não encontrado, usando dados simulados")
        gdf_merged = gdf.copy()
        gdf_merged['POPULACAO'] = (gdf_merged['AREA_KM2'] * 5000).astype(int)
    
    # 3. Calcular campos derivados
    print("\n5. Calculando indicadores...")
    gdf_merged['DENSIDADE'] = gdf_merged['POPULACAO'] / gdf_merged['AREA_KM2']
    gdf_merged['DENSIDADE'] = gdf_merged['DENSIDADE'].replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # Criar campos adicionais simulados para estrutura completa
    if 'RENDA_MEDIA' not in gdf_merged.columns:
        # Simular renda baseada na densidade (áreas mais densas = renda mais variável)
        import numpy as np
        np.random.seed(42)
        gdf_merged['RENDA_MEDIA'] = 1500 + np.random.exponential(1500, len(gdf_merged))
        gdf_merged['RENDA_MEDIA'] = gdf_merged['RENDA_MEDIA'].clip(500, 20000)
    
    # Escolaridade simulada (%)
    if 'FUNDAMENTAL' not in gdf_merged.columns:
        np.random.seed(42)
        gdf_merged['ANALFABETO'] = np.random.uniform(1, 8, len(gdf_merged))
        gdf_merged['FUNDAMENTAL'] = np.random.uniform(20, 45, len(gdf_merged))
        gdf_merged['MEDIO'] = np.random.uniform(25, 50, len(gdf_merged))
        gdf_merged['SUPERIOR'] = 100 - gdf_merged['ANALFABETO'] - gdf_merged['FUNDAMENTAL'] - gdf_merged['MEDIO']
    
    # Idade simulada (%)
    if 'IDADE_0_14' not in gdf_merged.columns:
        np.random.seed(43)
        gdf_merged['IDADE_0_14'] = np.random.uniform(12, 22, len(gdf_merged))
        gdf_merged['IDADE_15_59'] = np.random.uniform(60, 70, len(gdf_merged))
        gdf_merged['IDADE_60_PLUS'] = 100 - gdf_merged['IDADE_0_14'] - gdf_merged['IDADE_15_59']
    
    # Raça simulada (%)
    if 'BRANCA' not in gdf_merged.columns:
        np.random.seed(44)
        gdf_merged['BRANCA'] = np.random.uniform(50, 75, len(gdf_merged))
        gdf_merged['PARDA'] = np.random.uniform(15, 35, len(gdf_merged))
        gdf_merged['PRETA'] = np.random.uniform(5, 15, len(gdf_merged))
        gdf_merged['AMARELA'] = np.random.uniform(1, 5, len(gdf_merged))
        gdf_merged['INDIGENA'] = 100 - gdf_merged['BRANCA'] - gdf_merged['PARDA'] - gdf_merged['PRETA'] - gdf_merged['AMARELA']
        gdf_merged['INDIGENA'] = gdf_merged['INDIGENA'].clip(0, 2)
    
    # 4. Selecionar e renomear colunas finais
    colunas_saida = {
        'CD_SETOR': 'CD_SETOR',
        'POPULACAO': 'POPULACAO',
        'AREA_KM2': 'AREA_KM2',
        'DENSIDADE': 'DENSIDADE',
        'RENDA_MEDIA': 'RENDA_MEDIA',
        'ANALFABETO': 'ANALFABETO',
        'FUNDAMENTAL': 'FUNDAMENTAL',
        'MEDIO': 'MEDIO',
        'SUPERIOR': 'SUPERIOR',
        'IDADE_0_14': 'IDADE_0_14',
        'IDADE_15_59': 'IDADE_15_59',
        'IDADE_60_PLUS': 'IDADE_60_PLUS',
        'BRANCA': 'BRANCA',
        'PARDA': 'PARDA',
        'PRETA': 'PRETA',
        'AMARELA': 'AMARELA',
        'INDIGENA': 'INDIGENA',
        'geometry': 'geometry'
    }
    
    # Garantir que todas as colunas existam
    for col in colunas_saida.keys():
        if col not in gdf_merged.columns and col != 'geometry':
            gdf_merged[col] = 0
    
    gdf_final = gdf_merged[list(colunas_saida.keys())]
    gdf_final = gdf_final.rename(columns=colunas_saida)
    
    # 5. Salvar GeoJSON
    print("\n6. Salvando GeoJSON...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "setores_sp.geojson"
    
    # Salvar GeoJSON
    gdf_final.to_file(output_path, driver='GeoJSON')
    
    # Estatísticas
    tamanho_mb = output_path.stat().st_size / (1024 * 1024)
    pop_total = gdf_final['POPULACAO'].sum()
    
    print(f"\n{'='*60}")
    print("✓ ARQUIVO GERADO COM SUCESSO!")
    print(f"{'='*60}")
    print(f"  Arquivo: {output_path}")
    print(f"  Tamanho: {tamanho_mb:.1f} MB")
    print(f"  Setores: {len(gdf_final):,}")
    print(f"  População total: {pop_total:,.0f}")
    print(f"  Densidade média: {gdf_final['DENSIDADE'].mean():.0f} hab/km²")
    print(f"  Renda média: R$ {gdf_final['RENDA_MEDIA'].mean():,.2f}")
    print(f"{'='*60}")
    
    return output_path

def baixar_com_geobr():
    """Usar biblioteca geobr para download facilitado"""
    print("\n--- Usando geobr (biblioteca Python para dados IBGE) ---")
    try:
        import geobr
        print("Baixando setores censitários de São Paulo via geobr...")
        
        # Download dos setores censitários
        gdf = geobr.read_census_tract(code_tract="SP", year=2022)
        print(f"✓ Download concluído: {len(gdf)} setores")
        
        # Calcular área
        gdf = gdf.to_crs(epsg=31983)
        gdf['AREA_KM2'] = gdf.geometry.area / 1_000_000
        gdf = gdf.to_crs(epsg=4326)
        
        # Adicionar dados simulados (geobr não inclui dados censitários detalhados)
        print("Adicionando dados censitários simulados...")
        gdf = adicionar_dados_simulados(gdf)
        
        # Salvar
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "setores_sp.geojson"
        gdf.to_file(output_path, driver='GeoJSON')
        
        mostrar_estatisticas(gdf, output_path)
        return output_path
        
    except ImportError:
        print("✗ geobr não instalado. Instale com: pip install geobr")
        return None
    except Exception as e:
        print(f"✗ Erro com geobr: {e}")
        return None

def adicionar_dados_simulados(gdf):
    """Adicionar dados censitários simulados baseados em modelos realistas"""
    np.random.seed(42)
    n = len(gdf)
    
    # População baseada na área e densidade típica de SP
    # Centro = mais denso, periferia = menos denso
    centro_sp = (-23.5505, -46.6333)
    gdf['dist_centro'] = gdf.geometry.centroid.apply(
        lambda p: ((p.x - centro_sp[1])**2 + (p.y - centro_sp[0])**2)**0.5
    )
    
    # Densidade inversamente proporcional à distância do centro
    densidade_base = np.random.exponential(8000, n)
    densidade_base = densidade_base * (1 + 1/(1 + gdf['dist_centro']*10))
    densidade_base = np.clip(densidade_base, 500, 30000)
    
    gdf['DENSIDADE'] = densidade_base
    gdf['POPULACAO'] = (gdf['DENSIDADE'] * gdf['AREA_KM2']).astype(int)
    gdf['POPULACAO'] = gdf['POPULACAO'].clip(50, 20000)
    
    # Renda
    # Áreas centrais = renda mais alta
    renda_base = 2500 + np.random.exponential(1500, n)
    renda_fator = 1 + 0.5/(1 + gdf['dist_centro']*5)  # Centro = +50%
    gdf['RENDA_MEDIA'] = (renda_base * renda_fator).clip(800, 15000)
    
    # Escolaridade (%)
    gdf['ANALFABETO'] = np.random.uniform(1, 6, n)
    gdf['FUNDAMENTAL'] = np.random.uniform(20, 40, n)
    gdf['MEDIO'] = np.random.uniform(30, 50, n)
    gdf['SUPERIOR'] = 100 - gdf['ANALFABETO'] - gdf['FUNDAMENTAL'] - gdf['MEDIO']
    
    # Idade (%)
    gdf['IDADE_0_14'] = np.random.uniform(15, 25, n)
    gdf['IDADE_15_59'] = np.random.uniform(60, 70, n)
    gdf['IDADE_60_PLUS'] = 100 - gdf['IDADE_0_14'] - gdf['IDADE_15_59']
    
    # Raça/Cor SP (% aproximados do Censo)
    gdf['BRANCA'] = np.random.uniform(55, 75, n)
    gdf['PARDA'] = np.random.uniform(18, 32, n)
    gdf['PRETA'] = np.random.uniform(6, 12, n)
    gdf['AMARELA'] = np.random.uniform(2, 5, n)
    gdf['INDIGENA'] = np.random.uniform(0.1, 0.8, n)
    
    # Garantir soma = 100%
    raca_soma = gdf['BRANCA'] + gdf['PARDA'] + gdf['PRETA'] + gdf['AMARELA'] + gdf['INDIGENA']
    for col in ['BRANCA', 'PARDA', 'PRETA', 'AMARELA', 'INDIGENA']:
        gdf[col] = (gdf[col] / raca_soma * 100).round(1)
    
    return gdf

def criar_dados_exemplo():
    """Criar dados de exemplo para teste quando IBGE não disponível"""
    print("\n--- Criando dados de exemplo ---")
    
    if not HAS_GEO:
        print("✗ Bibliotecas necessárias não instaladas")
        return None
    
    from shapely.geometry import Polygon, Point
    
    # Criar grade fictícia de setores ao redor do Colégio Móbile
    centro = (-23.5985, -46.6692)  # Escola Móbile
    n_linhas = 15
    n_cols = 15
    
    features = []
    id_counter = 1
    
    for i in range(n_linhas):
        for j in range(n_cols):
            # Criar polígono do setor (aprox 100x100m cada)
            lat = centro[0] + (i - n_linhas/2) * 0.001
            lng = centro[1] + (j - n_cols/2) * 0.001
            
            coords = [
                (lng, lat),
                (lng + 0.001, lat),
                (lng + 0.001, lat + 0.001),
                (lng, lat + 0.001),
                (lng, lat)
            ]
            
            # Dados simulados
            area_km2 = 0.01  # ~100m x 100m
            densidade = np.random.exponential(5000) + 1000
            populacao = int(densidade * area_km2)
            
            feature = {
                'type': 'Feature',
                'properties': {
                    'CD_SETOR': f'EXAMPLE_{id_counter:06d}',
                    'POPULACAO': populacao,
                    'AREA_KM2': area_km2,
                    'DENSIDADE': densidade,
                    'RENDA_MEDIA': np.random.uniform(1200, 6000),
                    'ANALFABETO': np.random.uniform(2, 8),
                    'FUNDAMENTAL': np.random.uniform(25, 45),
                    'MEDIO': np.random.uniform(30, 50),
                    'SUPERIOR': np.random.uniform(10, 30),
                    'IDADE_0_14': np.random.uniform(15, 25),
                    'IDADE_15_59': np.random.uniform(60, 70),
                    'IDADE_60_PLUS': np.random.uniform(8, 18),
                    'BRANCA': np.random.uniform(50, 75),
                    'PARDA': np.random.uniform(15, 35),
                    'PRETA': np.random.uniform(5, 15),
                    'AMARELA': np.random.uniform(1, 5),
                    'INDIGENA': np.random.uniform(0, 1)
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [coords]
                }
            }
            features.append(feature)
            id_counter += 1
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    # Salvar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "setores_sp.geojson"
    
    with open(output_path, 'w') as f:
        json.dump(geojson, f)
    
    print(f"✓ Criado: {output_path}")
    print(f"  Setores: {len(features)}")
    print(f"  Área: {n_linhas*n_cols} setores (~{n_linhas*100}m x {n_cols*100}m)")
    
    return output_path

def mostrar_estatisticas(gdf, output_path):
    """Mostrar estatísticas do arquivo gerado"""
    tamanho_mb = output_path.stat().st_size / (1024 * 1024)
    pop_total = gdf['POPULACAO'].sum()
    
    print(f"\n{'='*60}")
    print("✓ ARQUIVO GERADO COM SUCESSO!")
    print(f"{'='*60}")
    print(f"  Arquivo: {output_path}")
    print(f"  Tamanho: {tamanho_mb:.1f} MB")
    print(f"  Setores: {len(gdf):,}")
    print(f"  População total: {pop_total:,.0f}")
    print(f"  Densidade média: {gdf['DENSIDADE'].mean():.0f} hab/km²")
    print(f"  Renda média: R$ {gdf['RENDA_MEDIA'].mean():,.2f}")
    print(f"{'='*60}")

def limpar_temp():
    """Remover arquivos temporários"""
    import shutil
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
        print("\n✓ Arquivos temporários removidos")

def main():
    parser = argparse.ArgumentParser(description='Download dados censitários IBGE para São Paulo')
    parser.add_argument('--api', action='store_true', help='Usar geobr (recomendado)')
    parser.add_argument('--url', action='store_true', help='Tentar URLs diretas do IBGE')
    parser.add_argument('--sample', action='store_true', help='Criar dados de exemplo')
    args = parser.parse_args()
    
    print("=" * 60)
    print("DOWNLOAD DE DADOS CENSITÁRIOS - IBGE")
    print("São Paulo / Censo 2022")
    print("=" * 60)
    
    # Determinar método
    if args.sample:
        result = criar_dados_exemplo()
    elif args.api:
        result = baixar_com_geobr()
    else:
        # Padrão: tentar geobr primeiro
        result = baixar_com_geobr()
        if not result:
            print("\n--- Tentando método alternativo (URLs diretas) ---")
            try:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                TEMP_DIR.mkdir(exist_ok=True)
                
                # Tentar cada URL de malha
                zip_geo = None
                for url in IBGE_URLS:
                    zip_geo = TEMP_DIR / "malhas_sp.zip"
                    if download_file(url, zip_geo):
                        break
                
                if not zip_geo or not zip_geo.exists():
                    print("\n✗ Falha no download das malhas")
                    criar_dados_exemplo()
                    return
                
                extrair_zip(zip_geo, TEMP_DIR)
                
                # Tentar dados do censo
                for url in CENSO_URLS:
                    zip_dados = TEMP_DIR / "dados_censo.zip"
                    if download_file(url, zip_dados):
                        extrair_zip(zip_dados, TEMP_DIR)
                        break
                
                result = processar_dados()
                limpar_temp()
                
            except Exception as e:
                print(f"\n✗ Erro: {e}")
                print("\n--- Criando dados de exemplo ---")
                result = criar_dados_exemplo()
    
    if result:
        print("\n" + "=" * 60)
        print("CONCLUÍDO! O arquivo está pronto para uso no mapa.")
        print(f"Local: {result}")
        print("=" * 60)
    else:
        print("\n✗ Falha no processamento")
        sys.exit(1)

if __name__ == "__main__":
    main()
