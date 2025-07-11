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
        const interval = parseInt(img.getAttribute('data-interval')) || 3000; // default 3 segundos
        
        try {
            const images = JSON.parse(imagesData);
            
            // Só inicia o slideshow se há mais de uma imagem
            if (images && images.length > 1) {
                startSlideshow(img, images, interval);
            }
        } catch (e) {
            console.error('Erro ao processar imagens do slideshow:', e);
        }
    });
}

function startSlideshow(imgElement, images, interval) {
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
    
    // Insere a segunda imagem no container
    imgElement.parentNode.insertBefore(imgElement2, imgElement);
    
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
    
    // Pré-carrega todas as imagens reduzidas
    const reducedImages = [];
    let loadedCount = 0;
    
    images.forEach((imageSrc, index) => {
        createReducedImage(imageSrc, (reducedUrl) => {
            reducedImages[index] = reducedUrl;
            loadedCount++;
            
            // Quando todas estiverem carregadas, inicia o slideshow
            if (loadedCount === images.length) {
                startImageRotation();
            }
        });
    });
    
    function startImageRotation() {
        // Configura a transição CSS mais lenta para ambas as imagens
        imgElement.style.transition = 'opacity 0.8s ease-in-out';
        imgElement2.style.transition = 'opacity 0.8s ease-in-out';
        
        // Define a primeira imagem reduzida
        if (reducedImages[0]) {
            imgElement.src = reducedImages[0];
        }
        
        // Função para trocar a imagem com crossfade (loop infinito)
        function changeImage() {
            // Calcula o próximo índice (volta para 0 após a última imagem)
            const nextIndex = (currentIndex + 1) % reducedImages.length;
            
            // Determina qual imagem está visível e qual está escondida
            const visibleImg = imgElement.style.opacity !== '0' ? imgElement : imgElement2;
            const hiddenImg = imgElement.style.opacity !== '0' ? imgElement2 : imgElement;
            
            // Pré-carrega a próxima imagem na imagem escondida
            hiddenImg.src = reducedImages[nextIndex];
            
            // Aguarda um breve momento para garantir que a imagem foi carregada
            setTimeout(() => {
                // Aplica crossfade suave
                visibleImg.style.opacity = '0';
                hiddenImg.style.opacity = '1';
            }, 50);
            
            currentIndex = nextIndex;
        }
        
        // Inicia o timer com intervalos mais longos
        setInterval(changeImage, Math.max(interval, 4000)); // Mínimo de 4 segundos
    }
}

function toggleMenu() {
    const menu = document.querySelector(".menu-links");
    const icon = document.querySelector(".hamburger-icon");
    menu.classList.toggle("open");
    icon.classList.toggle("open");
}

