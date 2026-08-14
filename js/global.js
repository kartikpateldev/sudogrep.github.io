document.addEventListener('DOMContentLoaded', function() {
  
  // Sticky Header Scroll Observer
  const header = document.getElementById('mainHeader');
  
  function handleScroll() {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }
  
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // Initialize on page load
  
  // Mobile Navigation Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mainNav = document.getElementById('mainNav');
  
  function closeMobileMenu() {
    if (mainNav && mainNav.classList.contains('active')) {
      mainNav.classList.remove('active');
      mobileMenuBtn.setAttribute('aria-expanded', 'false');
      
      const spans = mobileMenuBtn.querySelectorAll('span');
      if (spans.length >= 3) {
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[2].style.transform = 'none';
      }
      mobileMenuBtn.focus();
    }
  }

  function openMobileMenu() {
    if (mainNav && !mainNav.classList.contains('active')) {
      mainNav.classList.add('active');
      mobileMenuBtn.setAttribute('aria-expanded', 'true');
      
      const spans = mobileMenuBtn.querySelectorAll('span');
      if (spans.length >= 3) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      }
    }
  }
  
  if (mobileMenuBtn && mainNav) {
    mobileMenuBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const isExpanded = mobileMenuBtn.getAttribute('aria-expanded') === 'true';
      if (isExpanded) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });

    // Close menu when pressing Escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeMobileMenu();
      }
    });

    // Close menu when clicking outside of nav drawer
    document.addEventListener('click', function(e) {
      if (mainNav.classList.contains('active') && !mainNav.contains(e.target) && e.target !== mobileMenuBtn) {
        closeMobileMenu();
      }
    });
  }
  
  // Close mobile navigation drawer when clicking links
  const navLinks = document.querySelectorAll('.nav-link, .btn-cta-header');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeMobileMenu();
    });
  });
  
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
