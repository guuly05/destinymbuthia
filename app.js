/* ==========================================================================
   DESTINY MBUTHIA — PORTFOLIO INTERACTION & CLEAN ROUTING ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* --------------------------------------------------------------------------
     1. Clean URL Route Active Link Highlighting & Data Passing
     -------------------------------------------------------------------------- */
  const path = window.location.pathname.replace('.html', '');

  // Active state styling based on current clean path
  const navRoutes = document.querySelectorAll('.nav-route');
  navRoutes.forEach(link => {
    const href = link.getAttribute('href').replace('.html', '');
    if (href === path || (path === '/' && href === '/') || (path === href && href !== '/')) {
      link.classList.add('active-nav');
    }
  });

  // Client-side navigation click listener
  document.addEventListener('click', (e) => {
    const targetLink = e.target.closest('.nav-route');
    if (!targetLink) return;

    const packageData = targetLink.getAttribute('data-package');
    if (packageData) {
      sessionStorage.setItem('selectedPackage', packageData);
    }
  });

  /* --------------------------------------------------------------------------
     2. Gallery Filter Engine
     -------------------------------------------------------------------------- */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const galleryCards = document.querySelectorAll('.gallery-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filterValue = btn.getAttribute('data-filter');

      galleryCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');

        if (filterValue === 'all' || cardCategory === filterValue) {
          card.style.display = 'block';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(10px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 300);
        }
      });
    });
  });

  /* --------------------------------------------------------------------------
     3. Interactive Lightbox Modal
     -------------------------------------------------------------------------- */
  const lightboxModal = document.getElementById('lightboxModal');
  const lightboxImg = document.getElementById('lightboxImg');
  const lbTitle = document.getElementById('lbTitle');
  const lbDesc = document.getElementById('lbDesc');
  const lbStock = document.getElementById('lbStock');
  const lightboxClose = document.getElementById('lightboxClose');
  const lightboxPrev = document.getElementById('lightboxPrev');
  const lightboxNext = document.getElementById('lightboxNext');

  let currentIndex = 0;
  const cardsArray = Array.from(galleryCards);

  function openLightbox(index) {
    currentIndex = index;
    const card = cardsArray[currentIndex];
    if (!card) return;

    if (lightboxImg) lightboxImg.src = card.getAttribute('data-src');
    if (lbTitle) lbTitle.textContent = card.getAttribute('data-title') || 'Untitled Frame';
    if (lbDesc) lbDesc.textContent = card.getAttribute('data-desc') || '';
    if (lbStock) lbStock.textContent = card.getAttribute('data-stock') || '';

    if (lightboxModal) {
      lightboxModal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeLightbox() {
    if (lightboxModal) {
      lightboxModal.classList.remove('active');
      document.body.style.overflow = 'auto';
    }
  }

  galleryCards.forEach((card, index) => {
    card.addEventListener('click', () => openLightbox(index));
  });

  if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);

  if (lightboxPrev) {
    lightboxPrev.addEventListener('click', () => {
      currentIndex = (currentIndex - 1 + cardsArray.length) % cardsArray.length;
      openLightbox(currentIndex);
    });
  }

  if (lightboxNext) {
    lightboxNext.addEventListener('click', () => {
      currentIndex = (currentIndex + 1) % cardsArray.length;
      openLightbox(currentIndex);
    });
  }

  window.addEventListener('keydown', (e) => {
    if (!lightboxModal || !lightboxModal.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft' && lightboxPrev) lightboxPrev.click();
    if (e.key === 'ArrowRight' && lightboxNext) lightboxNext.click();
  });

  /* --------------------------------------------------------------------------
     4. Before / After Retouching Slider
     -------------------------------------------------------------------------- */
  const baSlider = document.getElementById('baSlider');
  const baBefore = document.getElementById('baBefore');
  const baHandle = document.getElementById('baHandle');

  if (baSlider && baBefore && baHandle) {
    let isSliding = false;

    const setSliderPosition = (x) => {
      const rect = baSlider.getBoundingClientRect();
      let offsetX = x - rect.left;
      if (offsetX < 0) offsetX = 0;
      if (offsetX > rect.width) offsetX = rect.width;

      const percentage = (offsetX / rect.width) * 100;
      baBefore.style.width = `${percentage}%`;
      baHandle.style.left = `${percentage}%`;
    };

    baSlider.addEventListener('mousedown', (e) => {
      isSliding = true;
      setSliderPosition(e.clientX);
    });

    window.addEventListener('mouseup', () => isSliding = false);
    window.addEventListener('mousemove', (e) => {
      if (!isSliding) return;
      setSliderPosition(e.clientX);
    });

    baSlider.addEventListener('touchstart', (e) => {
      isSliding = true;
      setSliderPosition(e.touches[0].clientX);
    });
    window.addEventListener('touchend', () => isSliding = false);
    window.addEventListener('touchmove', (e) => {
      if (!isSliding) return;
      setSliderPosition(e.touches[0].clientX);
    });
  }

  /* --------------------------------------------------------------------------
     5. Pricing / Package Switcher Tabs
     -------------------------------------------------------------------------- */
  const pricingTabs = document.querySelectorAll('.pricing-tab');
  const pricingGrids = document.querySelectorAll('.pricing-grid');

  pricingTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      pricingTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const target = tab.getAttribute('data-target');

      pricingGrids.forEach(grid => {
        if (grid.id === `${target}Packages`) {
          grid.classList.add('active');
        } else {
          grid.classList.remove('active');
        }
      });
    });
  });

  /* --------------------------------------------------------------------------
     6. Appointment Request Pre-fill & Toast Handler
     -------------------------------------------------------------------------- */
  const selectedPackageSelect = document.getElementById('selectedPackage');
  const bookingForm = document.getElementById('bookingForm');
  const toastNotification = document.getElementById('toastNotification');

  const storedPackage = sessionStorage.getItem('selectedPackage');
  if (storedPackage && selectedPackageSelect) {
    selectedPackageSelect.value = storedPackage;
    sessionStorage.removeItem('selectedPackage');
  }

  if (bookingForm) {
    bookingForm.addEventListener('submit', (e) => {
      e.preventDefault();

      if (toastNotification) {
        toastNotification.classList.add('show');
        setTimeout(() => {
          toastNotification.classList.remove('show');
        }, 4500);
      }

      bookingForm.reset();
    });
  }

});
