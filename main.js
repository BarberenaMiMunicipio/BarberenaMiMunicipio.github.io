document.addEventListener('DOMContentLoaded', () => {
  
  // --- COMPONENTE 1: MENÚ HAMBURGUESA ACCESIBLE ---
  const burger = document.querySelector('.nav-burger');
  const mobileMenu = document.querySelector('.nav-links-mobile');

  if (burger && mobileMenu) {
    burger.addEventListener('click', () => {
      const isOpen = burger.classList.toggle('open');
      mobileMenu.classList.toggle('open');
      burger.setAttribute('aria-expanded', isOpen);
      mobileMenu.setAttribute('aria-hidden', !isOpen);
    });

    // Cerrar menú al hacer click en un enlace interno
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        burger.classList.remove('open');
        mobileMenu.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        mobileMenu.setAttribute('aria-hidden', 'true');
      });
    });
  }

  // --- COMPONENTE 2: CARRUSEL EDITORIAL AVANZADO (PROPIOS Y TÁCTILES) ---
  const track = document.getElementById('carousel-track');
  const dots = document.querySelectorAll('.pilares-dots .dot');
  const slides = document.querySelectorAll('.pilar');
  
  if (track && slides.length > 0 && dots.length > 0) {
    let currentIndex = 0;
    let autoplayTimer = null;
    let startX = 0;
    let isSwiping = false;

    function updateCarousel(index) {
      if (index >= slides.length) currentIndex = 0;
      else if (index < 0) currentIndex = slides.length - 1;
      else currentIndex = index;

      track.style.transform = `translateX(-${currentIndex * 100}%)`;
      
      dots.forEach((dot, idx) => {
        const isActive = idx === currentIndex;
        dot.classList.toggle('active', isActive);
        dot.setAttribute('aria-selected', isActive);
      });
    }

    function startAutoplay() {
      stopAutoplay();
      autoplayTimer = setInterval(() => {
        updateCarousel(currentIndex + 1);
      }, 5000);
    }

    function stopAutoplay() {
      if (autoplayTimer) clearInterval(autoplayTimer);
    }

    // Eventos para los indicadores inferiores (dots)
    dots.forEach((dot, idx) => {
      dot.addEventListener('click', () => {
        updateCarousel(idx);
        stopAutoplay();
        startAutoplay(); // Reanuda temporizador tras interacción
      });
    });

    // Pausa por interacción del ratón (Escritorios)
    track.addEventListener('mouseenter', stopAutoplay);
    track.addEventListener('mouseleave', startAutoplay);

    // Control de gestos táctiles (Swipe)
    track.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isSwiping = true;
      stopAutoplay();
    }, { passive: true });

    track.addEventListener('touchmove', (e) => {
      if (!isSwiping) return;
      let diffX = e.touches[0].clientX - startX;
      // Umbral de sensibilidad de desplazamiento rápido de 60px
      if (Math.abs(diffX) > 60) {
        if (diffX > 0) updateCarousel(currentIndex - 1);
        else updateCarousel(currentIndex + 1);
        isSwiping = false;
      }
    }, { passive: true });

    track.addEventListener('touchend', () => {
      isSwiping = false;
      startAutoplay();
    });

    // Inicialización del proceso cíclico automático
    startAutoplay();
  }
});
