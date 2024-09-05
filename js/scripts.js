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
            document.querySelector('.projects').scrollIntoView({ behavior: 'smooth' });
        }
    });


    // Novo código para o slideshow
    const imageContainers = document.querySelectorAll('.image-container');
        
    imageContainers.forEach(container => {
        const images = container.querySelectorAll('.project-image');
        
        if (images.length > 1) {
            // Adiciona a classe 'slideshow' ao container
            container.classList.add('slideshow');
            
            let currentIndex = 0;

            function showNextImage() {
                images[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % images.length;
                images[currentIndex].classList.add('active');
            }

            // Ativa a primeira imagem
            images[0].classList.add('active');

            setInterval(showNextImage, 3000); // Troca a imagem a cada 3 segundos
        }
    });
});

