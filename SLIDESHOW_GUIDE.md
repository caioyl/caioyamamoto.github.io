# Guia do Sistema de Slideshow para Capas de Projetos

## Como Funciona

O sistema permite alternar automaticamente entre múltiplas imagens para as capas dos projetos, substituindo os GIFs. Você pode configurar:
- Quais imagens mostrar
- O tempo entre cada troca
- Quais projetos usam slideshow e quais mantêm imagem fixa

## Lógica do Sistema

O slideshow foi implementado especificamente para **substituir os GIFs existentes** por imagens estáticas que alternam automaticamente. Isso oferece várias vantagens:

- ✅ **Performance melhorada** - Imagens estáticas são mais leves que GIFs
- ✅ **Controle total** - Você define exatamente quais imagens mostrar e por quanto tempo
- ✅ **Flexibilidade** - Pode usar quantas imagens quiser para cada projeto
- ✅ **Compatibilidade** - Funciona em todos os navegadores
- ✅ **Transições suaves** - Efeito fade in/out entre as imagens
- ✅ **Proporção consistente** - Todas as imagens mantêm a proporção 3507x3158 (1.11:1)
- ✅ **Otimização automática** - Imagens do slideshow são reduzidas a 50% da resolução original
- ✅ **Ajuste sem recorte** - Imagens são ajustadas para caber sem serem cortadas

### Estratégia de Implementação:
1. **Projetos com GIFs** → Convertidos para slideshow com imagens individuais
2. **Projetos sem GIFs** → Mantêm imagem fixa original
3. **Projetos especiais** → Alguns podem manter GIF se preferir

## Como Configurar

### Para Projetos com Slideshow (múltiplas imagens)

No arquivo `index.html`, na tag `<img>` do projeto, adicione:

```html
<img src="./assets/gifs/nome_do_gif.gif" 
     alt="Project Image" 
     class="project-image slideshow-image" 
     data-images='["./caminho/imagem1.jpg", "./caminho/imagem2.jpg", "./caminho/imagem3.jpg"]'
     data-interval="3000">
```

**Parâmetros:**
- `slideshow-image`: Classe necessária para ativar o slideshow
- `data-images`: Array JSON com os caminhos das imagens (entre aspas duplas)
- `data-interval`: Tempo em milissegundos entre cada troca (3000 = 3 segundos)

### Para Projetos com Imagem Fixa

Mantenha o HTML normal, sem as classes e atributos especiais:

```html
<img src="./assets/imagens/imagem_fixa.jpg" alt="Project Image" class="project-image">
```

## Exemplos Configurados (com imagens reais dos projetos)

### 1. Mapas para Colorir
- **Imagens:** 2 imagens dos mapas da América
- **Intervalo:** 2 segundos (2000ms)
- **Caminho:** `["./assets/imagens/MAPA AMÉRICA DO SUL.jpg", "./assets/imagens/ENSINO MÉDIO _ AMÉRICA CENTRAL.jpg"]`

### 2. Parque Estadual da Serra do Mar
- **Imagens:** 2 imagens do projeto de climatologia
- **Intervalo:** 3 segundos (3000ms)
- **Caminho:** `["./assets/imagens/capa_clima.jpg", "./assets/imagens/trilha_clima.png"]`

### 3. Mapas do Estado de São Paulo
- **Imagens:** 5 imagens (3 mapas temáticos + 2 recortes geológicos)
- **Intervalo:** 2.5 segundos (2500ms)
- **Caminho:** `["./assets/imagens/mapa-geologico_v3.jpg", "./assets/imagens/mapa-geomorfologico_v3.jpg", "./assets/imagens/mapa-pedologico_v3.jpg", "./assets/imagens/mapa-geologico_recorte1.jpg", "./assets/imagens/mapa-geologico_recorte2.jpg"]`

### 4. Direito à Cidade
- **Imagens:** 7 imagens do trabalho de cartografia temática
- **Intervalo:** 3.5 segundos (3500ms)
- **Caminho:** `["./assets/imagens/hipsometrico.jpg", "./assets/imagens/hexagonos_teste.jpg", "./assets/imagens/mapalocalizacao.jpg", "./assets/imagens/escolas.jpg", "./assets/imagens/gruposrenda.jpg", "./assets/imagens/percentual_popnegra.jpg", "./assets/imagens/homicidios.jpg"]`

### 5. Carta Topográfica de Extrema
- **Imagens:** 2 imagens (com e sem curvas de nível)
- **Intervalo:** 4 segundos (4000ms)
- **Caminho:** `["./assets/imagens/extrema_com.jpg", "./assets/imagens/extrema_sem.jpg"]`

### 6. Projeto Soviético
- **Imagens:** 2 imagens (renderizada e não renderizada)
- **Intervalo:** 3 segundos (3000ms)
- **Caminho:** `["./assets/imagens/renderizado.jpg", "./assets/imagens/naorenderizado.jpg"]`

### 7. Laboratório de Geografia (exemplo de imagem fixa)
- Mantém a imagem original sem slideshow

## Como Adicionar Mais Projetos

1. **Prepare as imagens:** Salve suas imagens na pasta `./assets/imagens/`

2. **Edite o HTML:** No arquivo `index.html`, encontre o projeto desejado e modifique a tag `<img>`:

```html
<!-- Antes (com GIF) -->
<img src="./assets/gifs/meu_gif.gif" alt="Project Image" class="project-image">

<!-- Depois (com slideshow) -->
<img src="./assets/gifs/meu_gif.gif" 
     alt="Project Image" 
     class="project-image slideshow-image" 
     data-images='["./assets/imagens/img1.jpg", "./assets/imagens/img2.jpg"]'
     data-interval="2000">
```

3. **Ajuste os parâmetros:**
   - **Mais imagens:** Adicione mais caminhos no array `data-images`
   - **Mais rápido:** Diminua o valor de `data-interval`
   - **Mais lento:** Aumente o valor de `data-interval`

## Dicas

- **Formato das imagens:** Use JPG ou PNG
- **Tamanho:** Mantenha as imagens com tamanhos similares para melhor aparência
- **Performance:** Muitas imagens ou intervalos muito rápidos podem impactar a performance
- **Teste:** Sempre teste após fazer alterações

## Troubleshooting

- **Slideshow não funciona:** Verifique se a classe `slideshow-image` está presente
- **Imagens não carregam:** Confirme se os caminhos estão corretos
- **JSON inválido:** Certifique-se de usar aspas duplas no array `data-images`

## Características Técnicas

### Proporção das Imagens
- **Proporção fixa**: 3507x2480 (aproximadamente 1.41:1)
- **Comportamento**: Todas as imagens mantêm esta proporção específica
- **Ajuste**: Imagens são ajustadas para caber no container sem serem recortadas
- **Preenchimento**: Espaços vazios são transparentes (fundo da página visível)

### Otimização de Performance
- **Redução automática**: Imagens do slideshow são reduzidas a 50% da resolução original
- **Pré-carregamento**: Todas as imagens são processadas antes do início do slideshow
- **Compressão**: Imagens reduzidas são comprimidas com qualidade 80%
- **Canvas**: Utiliza HTML5 Canvas para processamento de imagem no cliente

### Transições
- **Duração**: 0.8 segundos para crossfade suave
- **Tipo**: ease-in-out para transição natural
- **Método**: Crossfade entre duas imagens sobrepostas (sem flash branco)
- **Loop infinito**: Após a última imagem, volta suavemente para a primeira
- **Intervalo mínimo**: 4 segundos entre trocas
- **Técnica**: Sistema de duas imagens com z-index alternado para transição perfeita

## Projetos Que Usam Slideshow vs Imagem Fixa

### ✅ Com Slideshow (substituindo GIFs):
- **Mapas para Colorir** - Usa imagens dos mapas da América Central e do Sul
- **Parque Estadual da Serra do Mar** - Usa imagens do projeto de climatologia
- **Mapas do Estado de São Paulo** - Usa mapas pedológico, geológico e geomorfológico
- **Direito à cidade** - Usa imagens do trabalho de cartografia temática
- **Projeto Soviético** - Usa versões renderizada e não renderizada

### 🔒 Com Imagem Fixa (não têm GIFs):
- **Visualizando 1km² em São Paulo - Escola Móbile** - Projeto web sem GIF
- **Laboratório de Geografia** - Site externo sem GIF
- **Mapa do Litoral Norte de São Paulo** - Em desenvolvimento
- **Maquete Hidrográfica do Rio Grande do Sul** - Projeto físico
- **Mapa - BNH Alto de Pinheiros** - Mapa único
- **Mapas para Estudo do Meio - Leme** - Mapas estáticos

### ⚠️ Projetos com GIF mas sem slideshow configurado:
- **Carta Topográfica de Extrema** - Ainda usa o GIF original (sem imagens estáticas separadas)
