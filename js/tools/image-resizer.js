document.addEventListener('DOMContentLoaded', function() {
  
  // Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const toolWorkspace = document.getElementById('toolWorkspace');
  const previewImage = document.getElementById('previewImage');
  const originalName = document.getElementById('originalName');
  
  // Controls
  const widthInput = document.getElementById('widthInput');
  const heightInput = document.getElementById('heightInput');
  const lockAspectRatio = document.getElementById('lockAspectRatio');
  const percentageSlider = document.getElementById('percentageSlider');
  const percentageValue = document.getElementById('percentageValue');
  
  const formatSelect = document.getElementById('formatSelect');
  const qualitySlider = document.getElementById('qualitySlider');
  const qualityValue = document.getElementById('qualityValue');
  
  const presetButtons = document.querySelectorAll('.preset-btn');
  
  // Metadata Readouts
  const origSizeVal = document.getElementById('origSizeVal');
  const compSizeVal = document.getElementById('compSizeVal');
  const dimensionsVal = document.getElementById('dimensionsVal');
  
  // Buttons
  const downloadBtn = document.getElementById('downloadBtn');
  const resetBtn = document.getElementById('resetBtn');
  const resizeIndicator = document.getElementById('resizeIndicator');

  // State
  let currentFile = null;
  let originalImage = null;
  let resizedBlob = null;
  let originalAspectRatio = 1;
  let isUpdatingInputs = false;
  let currentObjectURL = null;

  // Drag & Drop
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

  function handleFile(file) {
    if (!file.type.match('image.*')) {
      alert('Please select a valid image file.');
      return;
    }
    
    currentFile = file;
    originalName.textContent = file.name;
    
    const reader = new FileReader();
    reader.onload = function(e) {
      originalImage = new Image();
      originalImage.onload = function() {
        dropZone.style.display = 'none';
        toolWorkspace.style.display = 'grid';
        resetBtn.style.display = 'inline-flex';
        
        origSizeVal.textContent = formatBytes(file.size);
        originalAspectRatio = originalImage.naturalWidth / originalImage.naturalHeight;
        
        isUpdatingInputs = true;
        widthInput.value = originalImage.naturalWidth;
        heightInput.value = originalImage.naturalHeight;
        if (percentageSlider) {
          percentageSlider.value = 100;
          percentageValue.textContent = '100%';
        }
        isUpdatingInputs = false;
        
        resizeImage();
      };
      originalImage.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Dimension Change Listeners
  if (widthInput) {
    widthInput.addEventListener('input', function() {
      if (isUpdatingInputs) return;
      if (lockAspectRatio.checked && originalImage) {
        isUpdatingInputs = true;
        heightInput.value = Math.round(parseInt(this.value || 0) / originalAspectRatio) || '';
        isUpdatingInputs = false;
      }
      if (percentageSlider) {
        percentageSlider.value = 100;
        percentageValue.textContent = 'Custom';
      }
      presetButtons.forEach(btn => btn.classList.remove('active'));
      resizeImage();
    });
  }

  if (heightInput) {
    heightInput.addEventListener('input', function() {
      if (isUpdatingInputs) return;
      if (lockAspectRatio.checked && originalImage) {
        isUpdatingInputs = true;
        widthInput.value = Math.round(parseInt(this.value || 0) * originalAspectRatio) || '';
        isUpdatingInputs = false;
      }
      if (percentageSlider) {
        percentageSlider.value = 100;
        percentageValue.textContent = 'Custom';
      }
      presetButtons.forEach(btn => btn.classList.remove('active'));
      resizeImage();
    });
  }

  // Percent Slider
  if (percentageSlider) {
    percentageSlider.addEventListener('input', function() {
      if (!originalImage) return;
      
      const pct = parseInt(this.value);
      percentageValue.textContent = `${pct}%`;
      
      isUpdatingInputs = true;
      widthInput.value = Math.round(originalImage.naturalWidth * (pct / 100));
      heightInput.value = Math.round(originalImage.naturalHeight * (pct / 100));
      isUpdatingInputs = false;
      
      presetButtons.forEach(btn => btn.classList.remove('active'));
      resizeImage();
    });
  }

  // Presets
  presetButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      if (!originalImage) return;
      
      presetButtons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      const presetType = this.dataset.preset;
      let targetW = originalImage.naturalWidth;
      let targetH = originalImage.naturalHeight;
      
      if (presetType === 'passport') {
        // Indian/Standard passport size ratio (approx 413x531 px at 300dpi)
        targetW = 413;
        targetH = 531;
        lockAspectRatio.checked = false; // Override lock for passport crop/stretch
      } else if (presetType === 'web-hd') {
        targetW = 1280;
        targetH = 720;
        lockAspectRatio.checked = false;
      } else if (presetType === 'insta-square') {
        targetW = 1080;
        targetH = 1080;
        lockAspectRatio.checked = false;
      } else if (presetType === 'fb-cover') {
        targetW = 820;
        targetH = 312;
        lockAspectRatio.checked = false;
      }
      
      isUpdatingInputs = true;
      widthInput.value = targetW;
      heightInput.value = targetH;
      if (percentageSlider) {
        percentageSlider.value = 100;
        percentageValue.textContent = 'Preset';
      }
      isUpdatingInputs = false;
      
      resizeImage();
    });
  });

  // Settings Listeners
  if (formatSelect) formatSelect.addEventListener('change', resizeImage);
  if (qualitySlider) {
    qualitySlider.addEventListener('input', function() {
      qualityValue.textContent = `${Math.round(this.value * 100)}%`;
      resizeImage();
    });
  }

  // Main Resize Action
  async function resizeImage() {
    if (!originalImage) return;

    if (resizeIndicator) resizeIndicator.style.display = 'block';

    const w = parseInt(widthInput.value) || 1;
    const h = parseInt(heightInput.value) || 1;
    const format = formatSelect ? formatSelect.value : 'image/jpeg';
    const quality = parseFloat(qualitySlider ? qualitySlider.value : 0.8);
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = w;
    canvas.height = h;
    
    // Draw and scale
    ctx.drawImage(originalImage, 0, 0, w, h);
    
    const exportQuality = (format === 'image/png') ? undefined : quality;
    resizedBlob = await new Promise(resolve => canvas.toBlob(resolve, format, exportQuality));
    
    if (resizedBlob) {
      updateUI(w, h, format);
    }
  }

  function updateUI(w, h, format) {
    if (resizeIndicator) resizeIndicator.style.display = 'none';
    
    if (currentObjectURL) {
      URL.revokeObjectURL(currentObjectURL);
    }
    currentObjectURL = URL.createObjectURL(resizedBlob);
    previewImage.src = currentObjectURL;
    
    compSizeVal.textContent = formatBytes(resizedBlob.size);
    dimensionsVal.textContent = `${w} × ${h} px`;
    
    downloadBtn.onclick = function() {
      const link = document.createElement('a');
      link.href = currentObjectURL;
      
      const origNameNoExt = currentFile.name.substring(0, currentFile.name.lastIndexOf('.')) || currentFile.name;
      let ext = 'jpg';
      if (format === 'image/png') ext = 'png';
      else if (format === 'image/webp') ext = 'webp';
      
      link.download = `${origNameNoExt}_resized.${ext}`;
      
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        document.body.removeChild(link);
      }, 100);
    };
  }

  // Reset
  if (resetBtn) {
    resetBtn.addEventListener('click', function() {
      currentFile = null;
      originalImage = null;
      resizedBlob = null;
      fileInput.value = '';
      previewImage.src = '';
      
      if (currentObjectURL) {
        URL.revokeObjectURL(currentObjectURL);
        currentObjectURL = null;
      }
      
      widthInput.value = '';
      heightInput.value = '';
      lockAspectRatio.checked = true;
      if (percentageSlider) {
        percentageSlider.value = 100;
        percentageValue.textContent = '100%';
      }
      
      presetButtons.forEach(btn => btn.classList.remove('active'));
      
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
