document.addEventListener('DOMContentLoaded', function() {
  
  // Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const toolWorkspace = document.getElementById('toolWorkspace');
  const previewImage = document.getElementById('previewImage');
  const originalName = document.getElementById('originalName');
  
  // Settings Controls
  const formatSelect = document.getElementById('formatSelect');
  const qualitySlider = document.getElementById('qualitySlider');
  const qualityValue = document.getElementById('qualityValue');
  const customTargetInput = document.getElementById('customTargetInput');
  const presetButtons = document.querySelectorAll('.preset-btn');
  
  // Results Metadata
  const origSizeVal = document.getElementById('origSizeVal');
  const compSizeVal = document.getElementById('compSizeVal');
  const reductionVal = document.getElementById('reductionVal');
  const dimensionsVal = document.getElementById('dimensionsVal');
  const reductionBarFill = document.getElementById('reductionBarFill');
  
  // Buttons
  const downloadBtn = document.getElementById('downloadBtn');
  const resetBtn = document.getElementById('resetBtn');
  const compressionIndicator = document.getElementById('compressionIndicator');

  // State
  let currentFile = null;
  let originalImage = null;
  let compressedBlob = null;
  let targetSizeKB = null; // null means manual quality control
  let activeQuality = 0.8;
  let currentObjectURL = null;
  
  // Drag & Drop Listeners
  if (dropZone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        handleFile(files[0]);
      }
    });

    dropZone.addEventListener('click', () => {
      fileInput.click();
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', function() {
      if (this.files.length > 0) {
        handleFile(this.files[0]);
      }
    });
  }

  // Pre-select target KB and format based on URL pathname
  const path = window.location.pathname;
  if (path.includes('compress-image-to-50kb') || path.includes('compress-jpg-to-50kb') || path.includes('compress-png-to-50kb')) {
    targetSizeKB = 50;
  } else if (path.includes('compress-image-to-100kb')) {
    targetSizeKB = 100;
  } else if (path.includes('compress-image-to-200kb')) {
    targetSizeKB = 200;
  }

  if (targetSizeKB) {
    presetButtons.forEach(btn => {
      if (btn.dataset.size === targetSizeKB.toString()) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    if (customTargetInput) customTargetInput.value = '';
  }

  // Pre-select format based on URL pathname
  if (formatSelect) {
    if (path.includes('to-png')) {
      formatSelect.value = 'image/png';
    } else if (path.includes('to-jpg')) {
      formatSelect.value = 'image/jpeg';
    } else if (path.includes('to-webp')) {
      formatSelect.value = 'image/webp';
    }
  }

  function handleFile(file) {
    if (!file.type.match('image.*')) {
      alert('Please select a valid image file (JPG, PNG, WebP).');
      return;
    }
    
    currentFile = file;
    originalName.textContent = file.name;
    
    const reader = new FileReader();
    reader.onload = function(e) {
      originalImage = new Image();
      originalImage.onload = function() {
        // Show workspace, hide dropzone
        dropZone.style.display = 'none';
        toolWorkspace.style.display = 'grid';
        resetBtn.style.display = 'inline-flex';
        
        origSizeVal.textContent = formatBytes(file.size);
        dimensionsVal.textContent = `${originalImage.naturalWidth} × ${originalImage.naturalHeight} px`;
        
        // Run initial compression
        compressImage();
      };
      originalImage.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Handle Settings Changes
  if (formatSelect) {
    formatSelect.addEventListener('change', compressImage);
  }

  if (qualitySlider) {
    qualitySlider.addEventListener('input', function() {
      qualityValue.textContent = `${Math.round(this.value * 100)}%`;
      activeQuality = parseFloat(this.value);
      
      // Deactivate target size presets since user is overriding quality manually
      presetButtons.forEach(btn => btn.classList.remove('active'));
      if (customTargetInput) customTargetInput.value = '';
      targetSizeKB = null;
      
      compressImage();
    });
  }

  // Preset Buttons click
  presetButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      presetButtons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      if (customTargetInput) customTargetInput.value = '';
      
      targetSizeKB = parseInt(this.dataset.size);
      compressImage();
    });
  });

  // Custom Target Size Input
  if (customTargetInput) {
    customTargetInput.addEventListener('input', function() {
      const val = parseInt(this.value);
      if (val > 0) {
        presetButtons.forEach(btn => btn.classList.remove('active'));
        targetSizeKB = val;
        compressImage();
      } else {
        targetSizeKB = null;
      }
    });
  }

  function showError(message) {
    let errorEl = document.getElementById('toolErrorMsg');
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.id = 'toolErrorMsg';
      errorEl.style.backgroundColor = '#fef2f2';
      errorEl.style.color = '#dc2626';
      errorEl.style.border = '1px solid #fecaca';
      errorEl.style.padding = '0.75rem 1rem';
      errorEl.style.borderRadius = 'var(--radius-md)';
      errorEl.style.fontSize = '0.9rem';
      errorEl.style.fontWeight = '500';
      errorEl.style.marginBottom = '1rem';
      
      const parentPanel = document.querySelector('.workspace-controls-panel');
      if (parentPanel) {
        parentPanel.insertBefore(errorEl, parentPanel.lastElementChild);
      }
    }
    errorEl.textContent = message;
    errorEl.style.display = 'block';
  }

  function clearError() {
    const errorEl = document.getElementById('toolErrorMsg');
    if (errorEl) {
      errorEl.style.display = 'none';
    }
  }

  // Dynamic binary search quality loop with dimension scaling fallback
  async function compressImage() {
    if (!originalImage) return;

    if (compressionIndicator) compressionIndicator.style.display = 'block';
    clearError();
    
    const format = formatSelect ? formatSelect.value : 'image/jpeg';
    
    let finalBlob = null;
    let finalWidth = originalImage.naturalWidth;
    let finalHeight = originalImage.naturalHeight;
    let finalQuality = activeQuality;

    if (targetSizeKB) {
      const targetBytes = targetSizeKB * 1024;
      const origWidth = originalImage.naturalWidth;
      const origHeight = originalImage.naturalHeight;
      const minDim = Math.min(origWidth, origHeight);
      
      let minScale = 0.1;
      if (minDim * minScale < 100) {
        minScale = Math.max(0.1, 100 / minDim);
      }
      if (minScale > 1.0) minScale = 1.0;

      // Try progressive scales: 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1
      const scales = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1].filter(s => s >= minScale);
      if (scales.length === 0 || scales[scales.length - 1] > minScale) {
        scales.push(minScale);
      }

      let found = false;

      // Helper to get blob at a specific scale and quality
      async function getBlobAt(scale, quality) {
        const w = Math.round(origWidth * scale);
        const h = Math.round(origHeight * scale);
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(originalImage, 0, 0, w, h);
        const q = (format === 'image/png') ? undefined : quality;
        const blob = await new Promise(resolve => canvas.toBlob(resolve, format, q));
        return { blob, w, h };
      }

      // Find first scale and quality combination that satisfies target size
      for (let s of scales) {
        if (format === 'image/png') {
          const res = await getBlobAt(s);
          if (res.blob && res.blob.size <= targetBytes) {
            finalBlob = res.blob;
            finalWidth = res.w;
            finalHeight = res.h;
            found = true;
            break;
          }
          finalBlob = res.blob;
          finalWidth = res.w;
          finalHeight = res.h;
        } else {
          // JPEG/WebP: check if fits at lowest quality threshold (0.05)
          const minQuality = 0.05;
          const resMin = await getBlobAt(s, minQuality);
          if (resMin.blob && resMin.blob.size <= targetBytes) {
            // Fits! Binary search quality in [0.05, 0.95] for best quality
            let lowQ = minQuality;
            let highQ = 0.95;
            let bestQ = minQuality;
            let bestBlobAtScale = resMin.blob;

            for (let iter = 0; iter < 7; iter++) {
              const testQ = (lowQ + highQ) / 2;
              const testRes = await getBlobAt(s, testQ);
              if (testRes.blob && testRes.blob.size <= targetBytes) {
                bestQ = testQ;
                bestBlobAtScale = testRes.blob;
                lowQ = testQ; // Try to get higher quality
              } else {
                highQ = testQ; // Decrease quality
              }
            }

            finalBlob = bestBlobAtScale;
            finalWidth = resMin.w;
            finalHeight = resMin.h;
            finalQuality = bestQ;
            found = true;
            break;
          }
          // Fallback if none fit
          finalBlob = resMin.blob;
          finalWidth = resMin.w;
          finalHeight = resMin.h;
          finalQuality = minQuality;
        }
      }

      compressedBlob = finalBlob;
      activeQuality = finalQuality;
      
      if (qualitySlider) {
        qualitySlider.value = activeQuality;
        qualityValue.textContent = `${Math.round(activeQuality * 100)}%`;
      }
    } else {
      // Manual mode: compress at activeQuality at full dimensions
      const quality = (format === 'image/png') ? undefined : activeQuality;
      const canvas = document.createElement('canvas');
      canvas.width = originalImage.naturalWidth;
      canvas.height = originalImage.naturalHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(originalImage, 0, 0);
      
      compressedBlob = await new Promise(resolve => canvas.toBlob(resolve, format, quality));
      finalWidth = originalImage.naturalWidth;
      finalHeight = originalImage.naturalHeight;
    }

    if (compressedBlob) {
      updateResultUI(finalWidth, finalHeight, format);
    }
  }

  function updateResultUI(w, h, format) {
    if (compressionIndicator) compressionIndicator.style.display = 'none';

    // Revoke previous object URL
    if (currentObjectURL) {
      URL.revokeObjectURL(currentObjectURL);
    }
    currentObjectURL = URL.createObjectURL(compressedBlob);
    previewImage.src = currentObjectURL;
    
    const compSize = compressedBlob.size;
    compSizeVal.textContent = formatBytes(compSize);
    dimensionsVal.textContent = `${w} × ${h} px`;
    
    // Calculate percentage reduction
    const origSize = currentFile.size;
    if (compSize < origSize) {
      const reduction = Math.round(((origSize - compSize) / origSize) * 100);
      reductionVal.textContent = `${reduction}%`;
      reductionBarFill.style.width = `${reduction}%`;
    } else {
      reductionVal.textContent = '0%';
      reductionBarFill.style.width = '0%';
    }
    
    // Check if target was set and exceeded
    if (targetSizeKB && compSize > (targetSizeKB * 1024)) {
      downloadBtn.disabled = true;
      downloadBtn.style.opacity = '0.5';
      downloadBtn.style.pointerEvents = 'none';
      showError(`Unable to reach the selected target size of ${targetSizeKB} KB while maintaining reasonable image quality.`);
    } else {
      downloadBtn.disabled = false;
      downloadBtn.style.opacity = '1';
      downloadBtn.style.pointerEvents = 'auto';
      clearError();
    }

    // Enable download link (downloads exact displayed blob)
    downloadBtn.onclick = function() {
      if (targetSizeKB && compSize > (targetSizeKB * 1024)) {
        return; // Guard
      }
      const link = document.createElement('a');
      link.href = currentObjectURL;
      
      // Filename construction
      const origNameNoExt = currentFile.name.substring(0, currentFile.name.lastIndexOf('.')) || currentFile.name;
      let ext = 'jpg';
      if (format === 'image/png') ext = 'png';
      else if (format === 'image/webp') ext = 'webp';
      
      link.download = `${origNameNoExt}_compressed.${ext}`;
      
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        document.body.removeChild(link);
      }, 100);
    };
  }

  // Reset tool
  if (resetBtn) {
    resetBtn.addEventListener('click', function() {
      currentFile = null;
      originalImage = null;
      compressedBlob = null;
      fileInput.value = '';
      previewImage.src = '';
      
      if (currentObjectURL) {
        URL.revokeObjectURL(currentObjectURL);
        currentObjectURL = null;
      }
      clearError();
      
      // Enable download btn states on reset
      downloadBtn.disabled = false;
      downloadBtn.style.opacity = '1';
      downloadBtn.style.pointerEvents = 'auto';

      // Default controls state
      if (qualitySlider) {
        qualitySlider.value = 0.8;
        qualityValue.textContent = '80%';
      }
      activeQuality = 0.8;
      
      presetButtons.forEach(btn => btn.classList.remove('active'));
      if (window.location.pathname.includes('compress-image-to-50kb')) {
        targetSizeKB = 50;
        presetButtons.forEach(btn => {
          if (btn.dataset.size === '50') btn.classList.add('active');
        });
      } else {
        targetSizeKB = null;
      }
      
      if (customTargetInput) customTargetInput.value = '';
      
      toolWorkspace.style.display = 'none';
      resetBtn.style.display = 'none';
      dropZone.style.display = 'flex';
    });
  }

  // Utilities
  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }
});
