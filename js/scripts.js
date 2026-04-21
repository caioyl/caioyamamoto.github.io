document.addEventListener('DOMContentLoaded', function() {
    const hiddenProjects = document.querySelectorAll('.project-item.hidden');
    const verMaisBtn = document.getElementById('ver-mais');
    let isExpanded = false;

    // Inicializa o efeito de zoom do mapa
    initializeMapZoom();

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
        const zoomCounts = img.getAttribute('data-zoom-counts');
        
        try {
            const images = JSON.parse(imagesData);
            let zoomCountsArray = [];
            
            // Parse zoom counts configuration
            if (zoomCounts) {
                zoomCountsArray = JSON.parse(zoomCounts);
            } else if (enableZoom) {
                // Se zoom está habilitado mas não há configuração específica, usa 1 zoom por padrão
                zoomCountsArray = images.map(() => 1);
            } else {
                // Se zoom não está habilitado, usa 0 zooms
                zoomCountsArray = images.map(() => 0);
            }
            
            // Inicia o slideshow mesmo se há apenas uma imagem (para permitir zoom)
            if (images && images.length > 0) {
                startSlideshow(img, images, interval, zoomCountsArray, zoomDuration);
            }
        } catch (e) {
            console.error('Erro ao processar imagens do slideshow:', e);
        }
    });
}

function startSlideshow(imgElement, images, interval, zoomCountsArray, zoomDuration) {
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
        img.onerror = function() {
            console.error('Erro ao carregar imagem para zoom:', src);
            // Chama callback com null para indicar falha
            callback(null);
        };
        // Normaliza o caminho removendo ./ se presente
        const normalizedSrc = src.startsWith('./') ? src.substring(2) : src;
        img.src = normalizedSrc;
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
        img.onerror = function() {
            console.error('Erro ao carregar imagem para redução:', src);
            // Chama callback com null para indicar falha
            callback(null);
        };
        // Normaliza o caminho removendo ./ se presente
        const normalizedSrc = src.startsWith('./') ? src.substring(2) : src;
        img.src = normalizedSrc;
    }
    
    // Pré-carrega todas as imagens e seus zooms
    const processedImages = [];
    let loadedCount = 0;
    
    // Calcula o total de imagens (principais + zooms)
    const totalImages = images.length + zoomCountsArray.reduce((sum, count) => sum + count, 0);
    console.log('Iniciando slideshow para', images.length, 'imagens, total a carregar:', totalImages);
    
    images.forEach((imageSrc, index) => {
        // Carrega a imagem principal reduzida
        createReducedImage(imageSrc, (reducedUrl) => {
            console.log('Imagem principal carregada:', index, imageSrc, 'sucesso:', !!reducedUrl);
            if (!processedImages[index]) {
                processedImages[index] = {
                    main: null,
                    zooms: []
                };
            }
            // Só adiciona se a imagem foi carregada com sucesso
            if (reducedUrl) {
                processedImages[index].main = reducedUrl;
            }
            loadedCount++;
            
            // Cria os zooms para esta imagem
            const zoomCount = zoomCountsArray[index] || 0;
            if (zoomCount > 0) {
                let zoomsLoaded = 0;
                
                for (let i = 0; i < zoomCount; i++) {
                    createRandomZoom(imageSrc, (zoomUrl) => {
                        console.log('Zoom carregado para imagem', index, 'sucesso:', !!zoomUrl);
                        // Só adiciona se o zoom foi carregado com sucesso
                        if (zoomUrl) {
                            processedImages[index].zooms.push(zoomUrl);
                        }
                        zoomsLoaded++;
                        loadedCount++;
                        
                        // Verifica se todos os zooms desta imagem foram carregados
                        if (zoomsLoaded === zoomCount && loadedCount === totalImages) {
                            console.log('Todas as imagens carregadas, iniciando rotação');
                            startImageRotation();
                        }
                    });
                }
            } else {
                // Se não há zooms, verifica se pode iniciar
                if (loadedCount === totalImages) {
                    console.log('Todas as imagens carregadas (sem zooms), iniciando rotação');
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
            
            if (currentImageData.zooms && currentImageData.zooms.length > 0) {
                // Mostra a imagem principal primeiro
                showImage(currentImageData.main);
                
                // Cria uma sequência de zooms
                let zoomIndex = 0;
                
                function showNextZoom() {
                    if (zoomIndex < currentImageData.zooms.length) {
                        setTimeout(() => {
                            showImage(currentImageData.zooms[zoomIndex]);
                            zoomIndex++;
                            showNextZoom();
                        }, interval);
                    } else {
                        // Após todos os zooms, avança para a próxima imagem
                        setTimeout(() => {
                            currentIndex = (currentIndex + 1) % processedImages.length;
                            changeImage();
                        }, zoomDuration);
                    }
                }
                
                showNextZoom();
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

// Função simples para controlar o movimento vertical do mapa
function initializeMapZoom() {
    const mapBackground = document.querySelector('.map-background');
    if (!mapBackground) return;

    // Configurações simples
    const zoomLevel = 400; // Zoom da imagem (quão próximo está)

    let scrollPosition = 0; // Posição vertical atual

    // Função sincronizada com o scroll normal da página
    function handleScroll() {
        const currentScroll = window.scrollY;

        // Scroll extremamente devagar: mapa se move muito lentamente
        // Quanto maior o zoomLevel, mais próximo o mapa parece estar
        scrollPosition = currentScroll * 0.010; // Movimento 20x mais devagar

        // Aplica movimento sincronizado (só muda posição, não a imagem)
        mapBackground.style.backgroundSize = `${zoomLevel}% auto`;
        mapBackground.style.backgroundPosition = `center ${scrollPosition}%`;
    }

    // Event listener
    window.addEventListener('scroll', handleScroll);
}

// Form submission handling for Formspree
function initializeContactForm() {
    const form = document.getElementById('services-contact-form');
    const successMessage = document.getElementById('form-success-message');
    
    if (!form || !successMessage) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        
        // Disable button during submission
        submitButton.disabled = true;
        submitButton.textContent = 'Enviando...';
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                // Hide form and show success message
                form.style.display = 'none';
                successMessage.style.display = 'block';
                
                // Reset form
                form.reset();
            } else {
                throw new Error('Erro no envio');
            }
        }).catch(error => {
            alert('Ocorreu um erro ao enviar a mensagem. Por favor, tente novamente.');
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        });
    });
}

// Initialize form handling when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeContactForm();
});

