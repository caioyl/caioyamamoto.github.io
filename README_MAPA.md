# Plano de Fundo com Mapa de São Paulo - Sistema Multi-Imagem

## Implementação

Foi implementado um plano de fundo dinâmico com múltiplas imagens de mapa que se conectam sequencialmente, criando uma jornada contínua pelo estado de São Paulo.

### Características:
- **Múltiplas imagens sequenciais**: Sistema que troca automaticamente entre diferentes imagens de mapa
- **Movimento vertical contínuo**: Cada imagem se move para baixo conforme o scroll
- **Transição suave entre imagens**: Efeito de fade suave ao mudar de uma imagem para outra
- **Zoom fixo configurável**: Zoom constante de 400% (ajustável)
- **Opacidade ajustável**: Configurada em 0.07 para se misturar com o fundo

### Como funciona:
1. **Detecção de fim da imagem**: Cada imagem desce até um ponto específico configurável (endPoint)
2. **Movimento contínuo**: A imagem se move para baixo conforme o scroll do usuário
3. **Transição automática**: Ao atingir o endPoint da imagem atual, faz fade para a próxima
4. **Pontos de parada individuais**: Cada imagem pode ter seu próprio limite de descida (0-100%)

### Arquivos modificados:
1. **css/styles.css**: Estilos para `.map-background` com suporte a transições
2. **index.html**: Elemento `<div class="map-background"></div>`
3. **js/scripts.js**: Função `initializeMapZoom()` com sistema multi-imagem

### Configurações do JavaScript:
```javascript
const mapImages = [
    {
        src: '../assets/mapas-sp/mapa-sp-base.jpg',
        zoom: 400,        // Zoom individual para esta imagem (%)
        startPoint: 0,    // Ponto de início (%)
        endPoint: 85      // Ponto de fim (%)
    },
    {
        src: '../assets/mapas-sp/folha.jpg',
        zoom: 600,        // Zoom diferente para esta imagem
        startPoint: 0,    // Começa do topo
        endPoint: 90      // Vai até 90%
    }
    // Adicione quantas imagens quiser! Sistema totalmente flexível
];

const config = {
    scrollSensitivity: 0.5,  // Sensibilidade do scroll (quanto move por px)
    transitionDelay: 500      // Tempo de transição entre imagens em ms
};
```

### Como adicionar novas imagens:
1. **Adicione o arquivo**: Coloque a imagem em `assets/mapas-sp/`
2. **Atualize a lista**: Adicione o objeto no array `mapImages`
3. **Exemplo completo**:
   ```javascript
   {
       src: '../assets/mapas-sp/nova-imagem.jpg',
       zoom: 500,        // Zoom individual (100-1000%)
       startPoint: 10,   // Onde começa (0-100%)
       endPoint: 80      // Onde termina (0-100%)
   }
   ```

### Sistema totalmente flexível:
- **Quantidade ilimitada** de imagens
- **Zoom individual** para cada imagem
- **Start point** personalizado por imagem
- **End point** personalizado por imagem
- **Funciona com qualquer número** de imagens (1, 2, 10, 50...)

### Sugestões de sequência de imagens:
- **Mapa geral do estado** -> **Região norte** -> **Região sul** -> **Litoral**
- **Mapa político** -> **Mapa topográfico** -> **Mapa rodoviário** -> **Mapa de satélite**
- **Visão ampla** -> **Detalhes de cidades** -> **Regiões metropolitanas**

### Ajustes recomendados:
- **Opacidade**: Altere `opacity: 0.07` no CSS
- **Velocidade das transições**: Modifique `transition: opacity 0.5s ease-in-out`
- **Zoom individual**: Ajuste `zoom` de cada imagem (100-1000%)
- **Sensibilidade do scroll**: Modifique `scrollSensitivity` (0.1 = lento, 1.0 = rápido)
- **Pontos de início**: Ajuste `startPoint` de cada imagem (0-100%) para onde ela começa
- **Pontos de fim**: Ajuste `endPoint` de cada imagem (0-100%) para onde ela para
- **Tempo de transição**: Altere `transitionDelay` para controlar a duração do fade entre imagens

### Arquivos criados:
- `assets/mapas-sp/mapa-sp-base.jpg` (imagem principal)
- `assets/mapas-sp/mapa-sp-regiao-norte.jpg` (placeholder)
- `assets/mapas-sp/mapa-sp-regiao-sul.jpg` (placeholder)
- `assets/mapas-sp/mapa-sp-litoral.jpg` (placeholder)

**Substitua os placeholders com suas imagens reais!**
