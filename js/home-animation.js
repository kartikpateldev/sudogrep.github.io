document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('heroAnimationContainer');
  if (!container) return;

  // 1. Accessibility: Check prefers-reduced-motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) {
    container.classList.add('reduced-motion');
    // Set cards to static layout positions and terminate
    initializeStaticLayout();
    return;
  }

  // 2. Select card elements
  const cards = {
    compressor: container.querySelector('.card-compressor'),
    resizer: container.querySelector('.card-resizer'),
    pdf: container.querySelector('.card-pdf'),
    ai: container.querySelector('.card-ai'),
    apps: container.querySelector('.card-apps'),
    emblem: container.querySelector('.anim-emblem')
  };

  // Select card sub-elements for micro-animations
  const subElements = {
    compressBar: container.querySelector('.compress-bar-fill'),
    compressStats: container.querySelector('.compress-stats'),
    resizeBox: container.querySelector('.resize-box'),
    resizeText: container.querySelector('.resize-text'),
    pdfLayers: container.querySelectorAll('.pdf-layer'),
    pdfCompiled: container.querySelector('.pdf-compiled'),
    aiStatus: container.querySelector('.ai-status'),
    aiPulse: container.querySelector('.ai-pulse-node'),
    aiRing: container.querySelector('.node-ring'),
    appIcons: container.querySelectorAll('.mini-app-icon')
  };

  // Define layout configurations for desktop and mobile
  const layouts = {
    mobile: {
      emblem: { x: 0, y: -90, scale: 0.9, pFactor: 0.05 },
      compressor: { x: -20, y: -30, scale: 0.8, pFactor: 0.08, hoverClass: 'hover-compressor' },
      resizer: { x: 20, y: -10, scale: 0.8, pFactor: 0.08, hoverClass: 'hover-resizer' },
      pdf: { x: -20, y: 15, scale: 0.8, pFactor: 0.08, hoverClass: 'hover-pdf' },
      ai: { x: 20, y: 35, scale: 0.8, pFactor: 0.08, hoverClass: 'hover-ai' },
      apps: { x: 0, y: 65, scale: 0.85, pFactor: 0.08, hoverClass: 'hover-apps' }
    },
    desktop: {
      emblem: { x: 0, y: -5, scale: 1.0, pFactor: 0.03 },
      compressor: { x: -165, y: -110, scale: 1.0, pFactor: 0.1, hoverClass: 'hover-compressor' },
      resizer: { x: 165, y: -110, scale: 1.0, pFactor: 0.1, hoverClass: 'hover-resizer' },
      pdf: { x: -165, y: 100, scale: 1.0, pFactor: 0.1, hoverClass: 'hover-pdf' },
      ai: { x: 165, y: 100, scale: 1.0, pFactor: 0.1, hoverClass: 'hover-ai' },
      apps: { x: 0, y: 125, scale: 1.0, pFactor: 0.08, hoverClass: 'hover-apps' }
    }
  };

  // Maintain runtime animation states for each card
  const animationStates = {
    emblem: { currentX: 0, currentY: 0, currentScale: 0.3, opacity: 0, hoverValue: 0, floatOffset: 0 },
    compressor: { currentX: 0, currentY: 0, currentScale: 0, opacity: 0, hoverValue: 0, floatOffset: 0, delay: 100, phase: 0 },
    resizer: { currentX: 0, currentY: 0, currentScale: 0, opacity: 0, hoverValue: 0, floatOffset: 0, delay: 250, phase: 1.5 },
    pdf: { currentX: 0, currentY: 0, currentScale: 0, opacity: 0, hoverValue: 0, floatOffset: 0, delay: 400, phase: 3 },
    ai: { currentX: 0, currentY: 0, currentScale: 0, opacity: 0, hoverValue: 0, floatOffset: 0, delay: 550, phase: 4.5 },
    apps: { currentX: 0, currentY: 0, currentScale: 0, opacity: 0, hoverValue: 0, floatOffset: 0, delay: 700, phase: 0.8 }
  };

  // Mouse Parallax coordinates
  let mouseTargetX = 0;
  let mouseTargetY = 0;
  let mouseCurrentX = 0;
  let mouseCurrentY = 0;

  // Track hovers
  let hoveredCard = null;

  // Track page load time to drive animations
  let startTime = Date.now();
  let entryComplete = false;

  // Check if current viewport is mobile
  function isMobile() {
    return window.innerWidth < 768;
  }

  // Set initial position layout statically if motion is disabled
  function initializeStaticLayout() {
    const config = isMobile() ? layouts.mobile : layouts.desktop;
    Object.keys(config).forEach(key => {
      const cardEl = cards[key];
      if (!cardEl) return;
      const target = config[key];
      cardEl.style.transform = `translate(-50%, -50%) translate(${target.x}px, ${target.y}px) scale(${target.scale})`;
      cardEl.style.opacity = '1';
      cardEl.style.pointerEvents = 'auto';
    });
  }

  // Set up hover event listeners on each card
  Object.keys(cards).forEach(key => {
    if (key === 'emblem') return;
    const cardEl = cards[key];
    if (!cardEl) return;

    cardEl.addEventListener('mouseenter', () => {
      hoveredCard = key;
      const config = isMobile() ? layouts.mobile : layouts.desktop;
      if (config[key] && config[key].hoverClass) {
        container.className = 'hero-animation-container ' + config[key].hoverClass;
      }
    });

    cardEl.addEventListener('mouseleave', () => {
      if (hoveredCard === key) {
        hoveredCard = null;
        container.className = 'hero-animation-container';
      }
    });
  });

  // Track mouse coordinates for parallax
  container.addEventListener('mousemove', (e) => {
    if (isMobile()) return; // Disable parallax on mobile touch sizes
    const rect = container.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    // Normalize coordinates from -1.0 to 1.0 (relative to center)
    mouseTargetX = (e.clientX - centerX) / (rect.width / 2);
    mouseTargetY = (e.clientY - centerY) / (rect.height / 2);

    // Limit maximum displacement to -15px to 15px
    mouseTargetX = Math.min(Math.max(mouseTargetX, -1), 1) * 15;
    mouseTargetY = Math.min(Math.max(mouseTargetY, -1), 1) * 15;
  });

  container.addEventListener('mouseleave', () => {
    mouseTargetX = 0;
    mouseTargetY = 0;
  });

  // Main high-performance render loop
  function tick() {
    const now = Date.now();
    const elapsed = now - startTime;
    const config = isMobile() ? layouts.mobile : layouts.desktop;

    // 1. Smoothly interpolate overall mouse coordinates
    mouseCurrentX += (mouseTargetX - mouseCurrentX) * 0.08;
    mouseCurrentY += (mouseTargetY - mouseCurrentY) * 0.08;

    // 2. Animate and update each card state
    Object.keys(animationStates).forEach(key => {
      const state = animationStates[key];
      const target = config[key];
      const cardEl = cards[key];
      if (!cardEl || !target) return;

      // Handle Staggered Entry Animation on load
      if (elapsed > state.delay) {
        // Calculate progress of entry fade/slide
        const entryProgress = Math.min((elapsed - state.delay) / 700, 1);
        const ease = easeOutBack(entryProgress);
        
        state.opacity += (1 - state.opacity) * 0.1;
        state.currentX = target.x * ease;
        state.currentY = target.y * ease;
        
        // Target scale is adjusted depending on hover state
        const targetScaleVal = hoveredCard === key ? (isMobile() ? target.scale * 1.1 : target.scale * 1.08) : target.scale;
        state.currentScale += (targetScaleVal - state.currentScale) * 0.1;
      } else {
        // Center hidden state prior to entry trigger
        state.currentX = 0;
        state.currentY = 0;
        state.currentScale = 0;
        state.opacity = 0;
      }

      // Handle Float animation in standard loop
      if (elapsed > 1000) {
        entryComplete = true;
        // Damping float amplitude to 0 on hover
        const floatAmp = hoveredCard === key ? 0 : (key === 'emblem' ? 3 : 6);
        const floatPeriod = key === 'emblem' ? 0.001 : 0.0015;
        state.floatOffset = Math.sin(now * floatPeriod + state.phase) * floatAmp;
      }

      // Calculate final coordinates including float & parallax shifts
      const finalX = state.currentX + (mouseCurrentX * target.pFactor);
      const finalY = state.currentY + state.floatOffset + (mouseCurrentY * target.pFactor);

      // Render styles
      cardEl.style.transform = `translate(-50%, -50%) translate(${finalX}px, ${finalY}px) scale(${state.currentScale})`;
      cardEl.style.opacity = state.opacity;
      cardEl.style.pointerEvents = state.opacity > 0.5 ? 'auto' : 'none';
    });

    // 3. Update continuous micro previews within cards
    updateCardPreviews(now);

    requestAnimationFrame(tick);
  }

  // Interpolation helper function: Back-out bounce easing
  function easeOutBack(x) {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
  }

  // Manage individual card internal preview cycles
  function updateCardPreviews(time) {
    // A. Card 1: Compressor (4000ms loop)
    const compressCycle = time % 4000;
    if (subElements.compressBar && subElements.compressStats) {
      if (compressCycle < 1800) {
        // Phase 1: Compressing... (Progress fill)
        const prog = compressCycle / 1800;
        subElements.compressBar.style.width = `${prog * 75}%`;
        subElements.compressBar.style.backgroundColor = 'var(--accent)';
        
        const currentSize = Math.round(1200 - prog * 900);
        subElements.compressStats.innerHTML = `
          <span>1.2 MB</span>
          <span class="compress-arrow">→</span>
          <span class="highlight" style="color: var(--text-secondary);">${currentSize} KB</span>
        `;
      } else if (compressCycle < 3500) {
        // Phase 2: Completed compression
        subElements.compressBar.style.width = '75%';
        subElements.compressBar.style.backgroundColor = 'var(--accent-green)';
        subElements.compressStats.innerHTML = `
          <span>1.2 MB</span>
          <span class="compress-arrow">→</span>
          <span class="highlight" style="color: var(--accent-green);">300 KB (-75%)</span>
        `;
      } else {
        // Phase 3: Fading out to reset
        const fadeOutProg = (compressCycle - 3500) / 500;
        subElements.compressBar.style.width = '0%';
        subElements.compressStats.style.opacity = 1 - fadeOutProg;
        if (compressCycle > 3950) {
          subElements.compressStats.style.opacity = 1;
        }
      }
    }

    // B. Card 2: Resizer (4000ms loop)
    const resizeCycle = time % 4000;
    if (subElements.resizeBox && subElements.resizeText) {
      if (resizeCycle < 1800) {
        // Resizing down
        const prog = resizeCycle / 1800;
        const width = 80 - (prog * 35);
        const height = 60 - (prog * 25);
        subElements.resizeBox.style.width = `${width}px`;
        subElements.resizeBox.style.height = `${height}px`;
        subElements.resizeBox.style.borderColor = 'var(--accent-green)';
        subElements.resizeText.textContent = '1200 × 900';
        subElements.resizeText.style.color = 'var(--text-secondary)';
      } else if (resizeCycle < 3500) {
        // Hold resized state
        subElements.resizeBox.style.width = '45px';
        subElements.resizeBox.style.height = '35px';
        subElements.resizeBox.style.borderColor = 'var(--accent)';
        subElements.resizeText.textContent = '400 × 300';
        subElements.resizeText.style.color = 'var(--accent)';
      } else {
        // Stretch back to original
        const prog = (resizeCycle - 3500) / 500;
        const width = 45 + (prog * 35);
        const height = 35 + (prog * 25);
        subElements.resizeBox.style.width = `${width}px`;
        subElements.resizeBox.style.height = `${height}px`;
        subElements.resizeBox.style.borderColor = 'var(--accent-green)';
        subElements.resizeText.textContent = '1200 × 900';
        subElements.resizeText.style.color = 'var(--text-secondary)';
      }
    }

    // C. Card 3: PDF (5000ms loop)
    const pdfCycle = time % 5000;
    if (subElements.pdfLayers.length >= 2 && subElements.pdfCompiled) {
      if (pdfCycle < 1000) {
        // Reset state: Hide layers
        subElements.pdfLayers[0].style.transform = 'translateY(30px) rotate(15deg)';
        subElements.pdfLayers[0].style.opacity = '0';
        subElements.pdfLayers[1].style.transform = 'translateY(20px) rotate(-10deg)';
        subElements.pdfLayers[1].style.opacity = '0';
        subElements.pdfCompiled.style.opacity = '0';
        subElements.pdfCompiled.style.transform = 'scale(0.8)';
      } else if (pdfCycle < 2000) {
        // Layer 1 enters
        const prog = (pdfCycle - 1000) / 1000;
        subElements.pdfLayers[0].style.transform = `translateY(${30 - prog * 30}px) rotate(${15 - prog * 15}deg)`;
        subElements.pdfLayers[0].style.opacity = prog;
      } else if (pdfCycle < 3000) {
        // Layer 2 enters
        const prog = (pdfCycle - 2000) / 1000;
        subElements.pdfLayers[1].style.transform = `translateY(${20 - prog * 20}px) rotate(${-10 + prog * 10}deg)`;
        subElements.pdfLayers[1].style.opacity = prog;
      } else if (pdfCycle < 4500) {
        // Compile to PDF
        subElements.pdfCompiled.style.opacity = '1';
        subElements.pdfCompiled.style.transform = 'scale(1)';
        subElements.pdfLayers[0].style.opacity = '0';
        subElements.pdfLayers[1].style.opacity = '0';
      } else {
        // Fade out compiled PDF
        const prog = (pdfCycle - 4500) / 500;
        subElements.pdfCompiled.style.opacity = 1 - prog;
        subElements.pdfCompiled.style.transform = `scale(${1 - prog * 0.2})`;
      }
    }

    // D. Card 4: AI Agent (6000ms loop)
    const aiCycle = time % 6000;
    if (subElements.aiStatus && subElements.aiRing && subElements.aiPulse) {
      if (aiCycle < 1500) {
        // State 1: Standby
        subElements.aiStatus.textContent = 'Standby';
        subElements.aiStatus.style.color = 'var(--text-secondary)';
        subElements.aiRing.style.animationDuration = '2s';
        subElements.aiPulse.style.boxShadow = '0 0 4px rgba(124, 58, 237, 0.2)';
      } else if (aiCycle < 3000) {
        // State 2: Query Analyzing
        subElements.aiStatus.textContent = 'Analyzing...';
        subElements.aiStatus.style.color = 'var(--accent)';
        subElements.aiRing.style.animationDuration = '1s';
        subElements.aiPulse.style.boxShadow = '0 0 10px rgba(37, 99, 235, 0.4)';
      } else if (aiCycle < 4800) {
        // State 3: Code Executing
        subElements.aiStatus.textContent = 'Executing...';
        subElements.aiStatus.style.color = 'var(--accent-purple)';
        subElements.aiRing.style.animationDuration = '0.5s';
        subElements.aiPulse.style.boxShadow = '0 0 16px rgba(124, 58, 237, 0.7)';
      } else {
        // State 4: Task Solved!
        subElements.aiStatus.textContent = 'Task Solved!';
        subElements.aiStatus.style.color = 'var(--accent-green)';
        subElements.aiRing.style.animationDuration = '1.5s';
        subElements.aiPulse.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.9)';
      }
    }

    // E. Card 5: Apps Mockup (5000ms loop)
    const appsCycle = time % 5000;
    if (subElements.appIcons.length > 0) {
      subElements.appIcons.forEach((icon, idx) => {
        const staggerStart = idx * 400 + 500;
        const staggerEnd = staggerStart + 800;
        
        if (appsCycle < staggerStart) {
          icon.style.opacity = '0';
          icon.style.transform = 'scale(0.5) rotate(15deg)';
        } else if (appsCycle < staggerEnd) {
          const prog = (appsCycle - staggerStart) / 800;
          const scale = 0.5 + prog * 0.5;
          const rotate = (1 - prog) * 15;
          icon.style.opacity = prog;
          icon.style.transform = `scale(${scale}) rotate(${rotate}deg)`;
        } else if (appsCycle < 4300) {
          icon.style.opacity = '1';
          icon.style.transform = 'scale(1) rotate(0deg)';
        } else {
          // Fade/scale down to reset
          const prog = (appsCycle - 4300) / 700;
          icon.style.opacity = 1 - prog;
          icon.style.transform = `scale(${1 - prog * 0.5})`;
        }
      });
    }
  }

  // Kickstart loop
  tick();
});
