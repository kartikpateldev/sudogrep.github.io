document.addEventListener('DOMContentLoaded', function() {

  // Sticky Header Scroll Observer
  const header = document.getElementById('mainHeader');

  function handleScroll() {
    if (!header) return;
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }

  if (header) {
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  // Products Desktop Dropdown Toggle
  const dropdowns = document.querySelectorAll('[data-nav-dropdown]');

  function closeAllDropdowns(exceptDropdown = null) {
    dropdowns.forEach((dropdown) => {
      if (dropdown === exceptDropdown) return;
      dropdown.classList.remove('open');
      const toggle = dropdown.querySelector('.nav-dropdown-toggle');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    });
  }

  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector('.nav-dropdown-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const willOpen = !dropdown.classList.contains('open');
      closeAllDropdowns(willOpen ? dropdown : null);
      dropdown.classList.toggle('open', willOpen);
      toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    });
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('[data-nav-dropdown]')) {
      closeAllDropdowns();
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeAllDropdowns();
    }
  });

  // Same-page hash navigation: guarantee smooth scroll even when URL hash matches
  document.addEventListener('click', function(e) {
    const anchor = e.target.closest('a[href*="#"]');
    if (!anchor) return;

    const rawHref = anchor.getAttribute('href');
    if (!rawHref || rawHref === '#') return;

    let parsedUrl;
    try {
      parsedUrl = new URL(anchor.href, window.location.href);
    } catch (_) {
      return;
    }

    const sameOrigin = parsedUrl.origin === window.location.origin;
    const samePath =
      parsedUrl.pathname.replace(/\/index\.html$/, '/') ===
      window.location.pathname.replace(/\/index\.html$/, '/');
    if (!sameOrigin || !samePath || !parsedUrl.hash || parsedUrl.hash === '#') return;

    const targetId = decodeURIComponent(parsedUrl.hash.slice(1));
    const targetEl = document.getElementById(targetId);
    if (!targetEl) return;

    e.preventDefault();
    closeAllDropdowns();
    closeMobileDrawer(false);

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    targetEl.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    if (window.location.hash !== parsedUrl.hash && window.history && window.history.pushState) {
      window.history.pushState(null, '', parsedUrl.hash);
    }
  });

  // Accessible Mobile Navigation (<dialog> Drawer + Legacy Fallback)
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mainNav = document.getElementById('mainNav');
  const mobileDrawer = document.getElementById('mobileNavDrawer');
  const mobileDrawerPanel = mobileDrawer ? mobileDrawer.querySelector('.nav-drawer-panel') : null;
  const mobileDrawerCloseBtn = document.getElementById('mobileNavCloseBtn');
  let restoreFocusOnClose = true;

  function syncMenuTriggerState(isOpen) {
    if (!mobileMenuBtn) return;
    mobileMenuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    mobileMenuBtn.classList.toggle('active', isOpen);
  }

  function closeMobileDrawer(restoreFocus = true) {
    if (mobileDrawer && typeof mobileDrawer.showModal === 'function') {
      restoreFocusOnClose = restoreFocus;
      if (mobileDrawer.open) {
        mobileDrawer.close();
      }
      return;
    }

    if (mainNav && mainNav.classList.contains('active')) {
      mainNav.classList.remove('active');
      syncMenuTriggerState(false);
      if (restoreFocus && mobileMenuBtn) {
        mobileMenuBtn.focus();
      }
    }
  }

  function openMobileDrawer() {
    if (mobileDrawer && typeof mobileDrawer.showModal === 'function') {
      if (!mobileDrawer.open) {
        restoreFocusOnClose = true;
        mobileDrawer.showModal();
        syncMenuTriggerState(true);
      }
      return;
    }

    if (mainNav && !mainNav.classList.contains('active')) {
      mainNav.classList.add('active');
      syncMenuTriggerState(true);
    }
  }

  if (mobileDrawer && typeof mobileDrawer.showModal === 'function' && mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      if (mobileDrawer.open) {
        closeMobileDrawer(true);
      } else {
        openMobileDrawer();
      }
    });

    if (mobileDrawerCloseBtn) {
      mobileDrawerCloseBtn.addEventListener('click', function() {
        closeMobileDrawer(true);
      });
    }

    mobileDrawer.addEventListener('click', function(e) {
      if (mobileDrawerPanel && !mobileDrawerPanel.contains(e.target)) {
        closeMobileDrawer(true);
      }
    });

    mobileDrawer.addEventListener('cancel', function(e) {
      e.preventDefault();
      closeMobileDrawer(true);
    });

    mobileDrawer.addEventListener('close', function() {
      syncMenuTriggerState(false);
      if (restoreFocusOnClose && mobileMenuBtn) {
        mobileMenuBtn.focus();
      }
      restoreFocusOnClose = true;
    });

    const drawerLinks = mobileDrawer.querySelectorAll('a');
    drawerLinks.forEach((link) => {
      link.addEventListener('click', () => {
        closeMobileDrawer(false);
      });
    });

    const desktopMq = window.matchMedia('(min-width: 961px)');
    const handleDesktopBreakpoint = (mqEvent) => {
      if (mqEvent.matches && mobileDrawer.open) {
        closeMobileDrawer(false);
      }
    };
    if (typeof desktopMq.addEventListener === 'function') {
      desktopMq.addEventListener('change', handleDesktopBreakpoint);
    }
  } else if (mobileMenuBtn && mainNav) {
    mobileMenuBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const isExpanded = mobileMenuBtn.getAttribute('aria-expanded') === 'true';
      if (isExpanded) {
        closeMobileDrawer(true);
      } else {
        openMobileDrawer();
      }
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeMobileDrawer(true);
      }
    });

    document.addEventListener('click', function(e) {
      if (mainNav.classList.contains('active') && !mainNav.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
        closeMobileDrawer(true);
      }
    });

    const navLinks = document.querySelectorAll('.nav-link, .btn-cta-header');
    navLinks.forEach((link) => {
      link.addEventListener('click', () => {
        closeMobileDrawer(false);
      });
    });
  }

  // Contact Form Submission (integrated with Web3Forms)
  const contactForm = document.getElementById('contactForm');
  
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(contactForm);
      const submitButton = contactForm.querySelector('button[type="submit"]');
      const responseContainer = contactForm.querySelector('.form-response');
      const originalText = submitButton.textContent;
      
      // Clear previous response status
      if (responseContainer) {
        responseContainer.style.display = 'none';
        responseContainer.textContent = '';
      }
      
      submitButton.textContent = 'Sending...';
      submitButton.disabled = true;
      
      try {
        const response = await fetch('https://api.web3forms.com/submit', {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
          submitButton.textContent = 'Message Sent! ✓';
          submitButton.style.backgroundColor = 'var(--accent-green)';
          submitButton.style.color = 'var(--text-white)';
          
          if (responseContainer) {
            responseContainer.style.display = 'block';
            responseContainer.style.backgroundColor = 'var(--accent-green-subtle)';
            responseContainer.style.color = '#065f46';
            responseContainer.textContent = "Thanks — your message has been sent. We'll get back to you soon.";
          }
          
          contactForm.reset();
          
          setTimeout(() => {
            submitButton.textContent = originalText;
            submitButton.disabled = false;
            submitButton.style.backgroundColor = '';
            submitButton.style.color = '';
            if (responseContainer) {
              responseContainer.style.display = 'none';
            }
          }, 5000);
        } else {
          submitButton.textContent = 'Failed to Send';
          submitButton.style.backgroundColor = '#ef4444';
          submitButton.style.color = 'var(--text-white)';
          
          if (responseContainer) {
            responseContainer.style.display = 'block';
            responseContainer.style.backgroundColor = '#fef2f2';
            responseContainer.style.color = '#ef4444';
            responseContainer.textContent = "We couldn't send your message. Please try again.";
          }
          
          setTimeout(() => {
            submitButton.textContent = originalText;
            submitButton.disabled = false;
            submitButton.style.backgroundColor = '';
            submitButton.style.color = '';
          }, 3000);
        }
      } catch (error) {
        console.error('Error:', error);
        submitButton.textContent = 'Error Occurred';
        submitButton.style.backgroundColor = '#ef4444';
        submitButton.style.color = 'var(--text-white)';
        
        if (responseContainer) {
          responseContainer.style.display = 'block';
          responseContainer.style.backgroundColor = '#fef2f2';
          responseContainer.style.color = '#ef4444';
          responseContainer.textContent = "We couldn't send your message. Please try again.";
        }
        
        setTimeout(() => {
          submitButton.textContent = originalText;
          submitButton.disabled = false;
          submitButton.style.backgroundColor = '';
          submitButton.style.color = '';
        }, 3000);
      }
    });
  }
});
