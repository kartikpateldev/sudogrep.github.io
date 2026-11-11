/**
 * SudoGrep Technology Studio — Hero Systems Architecture Visual Controller
 * Interactive layer inspector for #heroArchitectureVisual with reduced-motion support.
 */
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('heroArchitectureVisual');
  if (!container) return;

  const nodes = Array.from(container.querySelectorAll('.arch-node[data-layer]'));
  const detailEl = document.getElementById('heroArchDetail');
  const statusEl = document.getElementById('heroArchStatusText');
  if (!nodes.length || !detailEl) return;

  const layerDescriptions = {
    mobile: 'Mobile & Client Layer — Cross-platform Flutter & native Android engineering designed for responsive, offline-capable everyday use.',
    ai: 'AI & Retrieval Layer — Retrieval-Augmented Generation (RAG) workflows, on-device OCR extraction, and grounded LLM automation.',
    web: 'Web Platforms Layer — Fast web applications, SEO-resilient publishing pipelines, and zero-upload browser computing via Web APIs.',
    cloud: 'Backend & Release Layer — Structured APIs, cloud synchronization, automated static builds, and end-to-end Google Play delivery.'
  };

  const layerStatuses = {
    mobile: 'LAYER 01 · CLIENT SYSTEMS',
    ai: 'LAYER 02 · INTELLIGENCE',
    web: 'LAYER 03 · WEB PLATFORMS',
    cloud: 'LAYER 04 · INFRASTRUCTURE'
  };

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let activeIndex = 0;
  let userPinned = false;
  let cycleTimer = null;

  function setActiveLayer(index) {
    activeIndex = index;
    container.classList.add('has-active');

    nodes.forEach((node, idx) => {
      const isSelected = idx === index;
      node.classList.toggle('is-active', isSelected);
      node.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
    });

    const activeNode = nodes[index];
    const key = activeNode.getAttribute('data-layer');
    if (key && layerDescriptions[key]) {
      detailEl.textContent = layerDescriptions[key];
    }
    if (statusEl && key && layerStatuses[key]) {
      statusEl.textContent = layerStatuses[key];
    }
  }

  function startAutoCycle() {
    if (prefersReducedMotion || userPinned || cycleTimer) return;
    cycleTimer = window.setInterval(() => {
      if (document.hidden || userPinned) return;
      setActiveLayer((activeIndex + 1) % nodes.length);
    }, 4200);
  }

  function stopAutoCycle() {
    if (cycleTimer) {
      window.clearInterval(cycleTimer);
      cycleTimer = null;
    }
  }

  nodes.forEach((node, index) => {
    node.addEventListener('mouseenter', () => {
      stopAutoCycle();
      setActiveLayer(index);
    });

    node.addEventListener('focus', () => {
      stopAutoCycle();
      setActiveLayer(index);
    });

    node.addEventListener('click', () => {
      userPinned = true;
      stopAutoCycle();
      setActiveLayer(index);
    });
  });

  container.addEventListener('mouseleave', () => {
    if (!userPinned) {
      startAutoCycle();
    }
  });

  setActiveLayer(0);
  startAutoCycle();
});
