#!/usr/bin/env python3
"""
Script para comprimir mapas do Museu da Pessoa.
Redimensiona para largura máxima 1920px mantendo proporção.
"""

from PIL import Image
import os

# Aumenta o limite de pixels para imagens grandes (desativa proteção de decompression bomb)
Image.MAX_IMAGE_PIXELS = None

# Configurações
IMAGENS_ORIGINAIS = [
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\1965_Azul.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\1975_Azul.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\1985_Azul.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\1995_Azul.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\2005_Azul.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\2015_Azul.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\2015_Azul_Nomes.png",
    r"G:\Meu Drive\2026\openhistoricalmaps\MAPAS - Museu da Pessoa\mapas\2025_Azul.png",
]

PASTA_DESTINO = r"C:\Users\caioy\Documents\GitHub\caioyamamoto.github.io\assets\imagens"
LARGURA_MAXIMA = 1920
QUALIDADE_JPEG = 85

def comprimir_imagem(caminho_origem, pasta_destino, largura_maxima=1920):
    """Redimensiona uma imagem mantendo proporção."""
    try:
        nome_arquivo = os.path.basename(caminho_origem)
        nome_base, extensao = os.path.splitext(nome_arquivo)
        
        # Para PNG, mantém formato PNG (sem perda)
        # Para outros, converte para JPEG
        if extensao.lower() == '.png':
            caminho_destino = os.path.join(pasta_destino, nome_arquivo)
        else:
            caminho_destino = os.path.join(pasta_destino, f"{nome_base}.jpg")
        
        with Image.open(caminho_origem) as img:
            largura_original, altura_original = img.size
            print(f"\n📷 {nome_arquivo}")
            print(f"   Original: {largura_original}x{altura_original} px")
            
            # Se já está dentro do limite, apenas copia
            if largura_original <= largura_maxima:
                if extensao.lower() == '.png':
                    img.save(caminho_destino, optimize=True)
                else:
                    img = img.convert('RGB')
                    img.save(caminho_destinho, quality=QUALIDADE_JPEG, optimize=True)
                print(f"   ✓ Copiado (já está dentro do limite)")
                return
            
            # Calcula novas dimensões
            proporcao = largura_maxima / largura_original
            nova_largura = largura_maxima
            nova_altura = int(altura_original * proporcao)
            
            # Redimensiona com alta qualidade
            img_resized = img.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
            
            # Salva
            if extensao.lower() == '.png':
                img_resized.save(caminho_destino, optimize=True)
            else:
                if img_resized.mode in ('RGBA', 'P'):
                    img_resized = img_resized.convert('RGB')
                img_resized.save(caminho_destino, quality=QUALIDADE_JPEG, optimize=True)
            
            # Estatísticas
            tamanho_orig = os.path.getsize(caminho_origem) / (1024 * 1024)
            tamanho_novo = os.path.getsize(caminho_destino) / (1024 * 1024)
            
            print(f"   ✓ Redimensionado: {nova_largura}x{nova_altura} px")
            print(f"   ✓ Tamanho: {tamanho_orig:.1f} MB → {tamanho_novo:.1f} MB")
            print(f"   ✓ Salvo em: {caminho_destino}")
            
    except Exception as e:
        print(f"   ✗ Erro em {caminho_origem}: {e}")

def main():
    print("=" * 60)
    print("COMPRESSÃO DE MAPAS - MUSEU DA PESSOA")
    print("=" * 60)
    print(f"Destino: {PASTA_DESTINO}")
    print(f"Largura máxima: {LARGURA_MAXIMA}px")
    print("=" * 60)
    
    # Verifica se pasta destino existe
    if not os.path.exists(PASTA_DESTINO):
        print(f"✗ Pasta destino não existe: {PASTA_DESTINO}")
        return
    
    # Processa cada imagem
    for caminho in IMAGENS_ORIGINAIS:
        if os.path.exists(caminho):
            comprimir_imagem(caminho, PASTA_DESTINO, LARGURA_MAXIMA)
        else:
            print(f"\n✗ Arquivo não encontrado: {caminho}")
    
    print("\n" + "=" * 60)
    print("Processamento concluído!")
    print("=" * 60)

if __name__ == "__main__":
    main()
