document.addEventListener('DOMContentLoaded', function() {
    const hiddenProjects = document.querySelectorAll('.project-item.hidden');
    const verMaisBtn = document.getElementById('ver-mais');
    let isExpanded = false;

    verMaisBtn.addEventListener('click', function() {
        if (!isExpanded) {
            hiddenProjects.forEach((project) => {
                project.classList.remove('hidden');
                project.style.display = 'block';
            });
            verMaisBtn.textContent = 'Ver menos';
            isExpanded = true;
        } else {
            hiddenProjects.forEach((project) => {
                project.classList.add('hidden');
                project.style.display = 'none';
            });
            verMaisBtn.textContent = 'Ver mais';
            isExpanded = false;
            
        // Scroll back to the top of the projects section
        document.querySelector('#projects').scrollIntoView({ behavior: 'smooth' });
        }
    });

    // Sistema de slideshow para imagens de projetos
    initializeImageSlideshow();
});

function initializeImageSlideshow() {
    // Encontra todas as imagens que têm o atributo data-images
    const slideshowImages = document.querySelectorAll('.slideshow-image[data-images]');
    
    slideshowImages.forEach(img => {
        const imagesData = img.getAttribute('data-images');
        const interval = parseInt(img.getAttribute('data-interval')) || 3000;
        const enableZoom = img.getAttribute('data-enable-zoom') === 'true';
        const zoomDuration = parseInt(img.getAttribute('data-zoom-duration')) || 2000;
        
        try {
            const images = JSON.parse(imagesData);
            
            // Só inicia o slideshow se há mais de uma imagem
            if (images && images.length > 1) {
                startSlideshow(img, images, interval, enableZoom, zoomDuration);
            }
        } catch (e) {
            console.error('Erro ao processar imagens do slideshow:', e);
        }
    });
}

function startSlideshow(imgElement, images, interval, enableZoom, zoomDuration) {
    let currentIndex = 0;
    
    // Cria uma segunda imagem para transições suaves
    const imgElement2 = imgElement.cloneNode(true);
    imgElement2.style.position = 'absolute';
    imgElement2.style.top = '0';
    imgElement2.style.left = '0';
    imgElement2.style.opacity = '0';
    imgElement2.style.zIndex = '1';
    
    // Ajusta z-index da imagem original
    imgElement.style.zIndex = '2';
    
    // Insere a segunda imagem no container, mas antes do overlay
    const container = imgElement.parentNode;
    const overlay = container.querySelector('.project-overlay');
    
    if (overlay) {
        container.insertBefore(imgElement2, overlay);
        overlay.style.zIndex = '3';
    } else {
        container.insertBefore(imgElement2, imgElement);
    }
    
    // Função para criar zoom aleatório de uma área da imagem
    function createRandomZoom(src, callback) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Dimensões da imagem original
            const imgWidth = this.width;
            const imgHeight = this.height;
            
            // Define o tamanho do zoom (40% a 60% da imagem original)
            const zoomFactor = 0.4 + Math.random() * 0.2; // 40% a 60%
            const zoomWidth = imgWidth * zoomFactor;
            const zoomHeight = imgHeight * zoomFactor;
            
            // Posição aleatória para o zoom (garantindo que não saia da imagem)
            const maxX = imgWidth - zoomWidth;
            const maxY = imgHeight - zoomHeight;
            const startX = Math.random() * maxX;
            const startY = Math.random() * maxY;
            
            // Configura o canvas com dimensões reduzidas
            canvas.width = imgWidth * 0.5;
            canvas.height = imgHeight * 0.5;
            
            // Desenha a área selecionada ampliada no canvas
            ctx.drawImage(
                this,
                startX, startY, zoomWidth, zoomHeight, // Área de origem
                0, 0, canvas.width, canvas.height // Área de destino (canvas inteiro)
            );
            
            // Converte para URL
            const zoomImageUrl = canvas.toDataURL('image/jpeg', 0.8);
            callback(zoomImageUrl);
        };
        img.src = src;
    }
    
    // Função para reduzir resolução da imagem
    function createReducedImage(src, callback) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Reduz dimensões para 50%
            canvas.width = this.width * 0.5;
            canvas.height = this.height * 0.5;
            
            // Desenha a imagem reduzida
            ctx.drawImage(this, 0, 0, canvas.width, canvas.height);
            
            // Converte para URL
            const reducedImageUrl = canvas.toDataURL('image/jpeg', 0.8);
            callback(reducedImageUrl);
        };
        img.src = src;
    }
    
    // Pré-carrega todas as imagens e seus zooms
    const processedImages = [];
    let loadedCount = 0;
    const totalImages = images.length * (enableZoom ? 2 : 1);
    
    images.forEach((imageSrc, index) => {
        // Carrega a imagem principal reduzida
        createReducedImage(imageSrc, (reducedUrl) => {
            if (!processedImages[index]) {
                processedImages[index] = {};
            }
            processedImages[index].main = reducedUrl;
            loadedCount++;
            
            // Se zoom está habilitado, cria o zoom aleatório
            if (enableZoom) {
                createRandomZoom(imageSrc, (zoomUrl) => {
                    processedImages[index].zoom = zoomUrl;
                    loadedCount++;
                    
                    // Quando todas estiverem carregadas, inicia o slideshow
                    if (loadedCount === totalImages) {
                        startImageRotation();
                    }
                });
            } else {
                // Se não há zoom, verifica se pode iniciar
                if (loadedCount === totalImages) {
                    startImageRotation();
                }
            }
        });
    });
    
    function startImageRotation() {
        // Configura a transição CSS
        imgElement.style.transition = 'opacity 0.8s ease-in-out';
        imgElement2.style.transition = 'opacity 0.8s ease-in-out';
        
        // Define a primeira imagem
        if (processedImages[0]) {
            imgElement.src = processedImages[0].main;
        }
        
        // Função para trocar a imagem
        function changeImage() {
            const currentImageData = processedImages[currentIndex];
            
            if (enableZoom && currentImageData.zoom) {
                // Mostra a imagem principal primeiro
                showImage(currentImageData.main);
                
                // Depois mostra o zoom
                setTimeout(() => {
                    showImage(currentImageData.zoom);
                    
                    // Volta para a próxima imagem após o zoom
                    setTimeout(() => {
                        currentIndex = (currentIndex + 1) % processedImages.length;
                        changeImage();
                    }, zoomDuration);
                }, interval);
            } else {
                // Só mostra a imagem principal
                showImage(currentImageData.main);
                
                setTimeout(() => {
                    currentIndex = (currentIndex + 1) % processedImages.length;
                    changeImage();
                }, interval);
            }
        }
        
        function showImage(imageSrc) {
            // Determina qual imagem está visível e qual está escondida
            const visibleImg = imgElement.style.opacity !== '0' ? imgElement : imgElement2;
            const hiddenImg = imgElement.style.opacity !== '0' ? imgElement2 : imgElement;
            
            // Pré-carrega a imagem na imagem escondida
            hiddenImg.src = imageSrc;
            
            // Aguarda um breve momento para garantir que a imagem foi carregada
            setTimeout(() => {
                // Aplica crossfade suave
                visibleImg.style.opacity = '0';
                hiddenImg.style.opacity = '1';
            }, 50);
        }
        
        // Inicia o slideshow
        changeImage();
    }
}

function toggleMenu() {
    const menu = document.querySelector(".menu-links");
    const icon = document.querySelector(".hamburger-icon");
    menu.classList.toggle("open");
    icon.classList.toggle("open");
}

