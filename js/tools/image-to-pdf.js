document.addEventListener('DOMContentLoaded', function() {
  
  // Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const toolWorkspace = document.getElementById('toolWorkspace');
  const pdfFileList = document.getElementById('pdfFileList');
  
  // Controls
  const pageSizeSelect = document.getElementById('pageSizeSelect');
  const orientationSelect = document.getElementById('orientationSelect');
  const qualitySlider = document.getElementById('qualitySlider');
  const qualityValue = document.getElementById('qualityValue');
  
  // Buttons
  const generateBtn = document.getElementById('generateBtn');
  const downloadBtn = document.getElementById('downloadBtn');
  const resetBtn = document.getElementById('resetBtn');
  const pdfIndicator = document.getElementById('pdfIndicator');
  
  // State
  let filesList = []; // Array of objects: { id, file, src, sizeFormatted }
  let currentFileId = 0;
  let dragSrcEl = null;
  let generatedPdfBlob = null;
  let generatedPdfURL = null;

  // Drag & Drop Dropzone
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
        addFiles(files);
      }
    });

    dropZone.addEventListener('click', () => {
      fileInput.click();
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', function() {
      if (this.files.length > 0) {
        addFiles(this.files);
      }
    });
  }

  // Pre-selected quality display update
  if (qualitySlider) {
    qualitySlider.addEventListener('input', function() {
      qualityValue.textContent = `${Math.round(this.value * 100)}%`;
    });
  }

  // Add files to list
  function addFiles(files) {
    let imagesAdded = 0;
    let nonJpgSkipped = false;
    const isJpgPage = window.location.pathname.includes('jpg-to-pdf');
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      if (isJpgPage) {
        const isJpg = file.type === 'image/jpeg' || file.name.toLowerCase().endsWith('.jpg') || file.name.toLowerCase().endsWith('.jpeg');
        if (!isJpg) {
          nonJpgSkipped = true;
          continue;
        }
      }
      
      if (file.type.match('image.*')) {
        imagesAdded++;
        const id = currentFileId++;
        const src = URL.createObjectURL(file);
        filesList.push({
          id: id,
          file: file,
          src: src,
          sizeFormatted: formatBytes(file.size)
        });
      }
    }
    
    if (nonJpgSkipped) {
      alert('Only JPG/JPEG files are supported on this page. Other files were skipped.');
    }
    
    if (imagesAdded > 0) {
      dropZone.style.display = 'none';
      toolWorkspace.style.display = 'grid';
      resetBtn.style.display = 'inline-flex';
      renderFileList();
    }
  }

  // Render HTML list for files
  function renderFileList() {
    pdfFileList.innerHTML = '';
    
    filesList.forEach((item, index) => {
      const card = document.createElement('div');
      card.className = 'pdf-file-card';
      card.draggable = true;
      card.dataset.id = item.id;
      
      card.innerHTML = `
        <div class="pdf-card-info">
          <img src="${item.src}" class="pdf-card-thumb" alt="thumbnail">
          <div class="pdf-card-details">
            <span class="pdf-card-name">${item.file.name}</span>
            <span class="pdf-card-size">${item.sizeFormatted}</span>
          </div>
        </div>
        <button class="pdf-card-delete" aria-label="Remove image">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      `;
      
      // Delete listener
      card.querySelector('.pdf-card-delete').onclick = (e) => {
        e.stopPropagation();
        filesList = filesList.filter(f => f.id !== item.id);
        if (filesList.length === 0) {
          resetTool();
        } else {
          renderFileList();
        }
      };

      // Drag & Drop reorder listeners
      card.addEventListener('dragstart', handleDragStart, false);
      card.addEventListener('dragover', handleDragOver, false);
      card.addEventListener('drop', handleDrop, false);
      card.addEventListener('dragend', handleDragEnd, false);
      
      pdfFileList.appendChild(card);
    });
    
    // Hide download button since list has changed
    downloadBtn.style.display = 'none';
    if (generatedPdfURL) {
      URL.revokeObjectURL(generatedPdfURL);
      generatedPdfURL = null;
    }
    generatedPdfBlob = null;
  }

  // HTML5 Drag and Drop event handlers
  function handleDragStart(e) {
    this.style.opacity = '0.4';
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
  }

  function handleDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
  }

  function handleDrop(e) {
    e.stopPropagation();
    if (dragSrcEl !== this) {
      const srcId = parseInt(dragSrcEl.dataset.id);
      const targetId = parseInt(this.dataset.id);
      
      const srcIndex = filesList.findIndex(f => f.id === srcId);
      const targetIndex = filesList.findIndex(f => f.id === targetId);
      
      // Swap positions in list
      const temp = filesList[srcIndex];
      filesList.splice(srcIndex, 1);
      filesList.splice(targetIndex, 0, temp);
      
      renderFileList();
    }
    return false;
  }

  function handleDragEnd(e) {
    this.style.opacity = '1';
    renderFileList();
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

  // Generate PDF Core
  if (generateBtn) {
    generateBtn.addEventListener('click', async function() {
      if (filesList.length === 0) return;
      
      pdfIndicator.style.display = 'block';
      generateBtn.disabled = true;
      clearError();
      
      try {
        if (generatedPdfURL) {
          URL.revokeObjectURL(generatedPdfURL);
          generatedPdfURL = null;
        }
        generatedPdfBlob = await assemblePDF();
        generatedPdfURL = URL.createObjectURL(generatedPdfBlob);
        pdfIndicator.style.display = 'none';
        generateBtn.disabled = false;
        
        // Show download option
        downloadBtn.style.display = 'inline-flex';
        downloadBtn.scrollIntoView({ behavior: 'smooth' });
      } catch (err) {
        console.error(err);
        showError('Unable to generate the PDF. Please try another image or format.');
        pdfIndicator.style.display = 'none';
        generateBtn.disabled = false;
      }
    });
  }

  if (downloadBtn) {
    downloadBtn.addEventListener('click', function() {
      if (!generatedPdfURL) {
        showError('The file could not be generated. Please try again.');
        return;
      }
      
      const link = document.createElement('a');
      link.href = generatedPdfURL;
      link.download = `sudogrep_compiled_${Date.now()}.pdf`;
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        document.body.removeChild(link);
      }, 100);
    });
  }

  // PDF binary assembler using raw DCTDecode
  async function assemblePDF() {
    const pageSize = pageSizeSelect.value;
    const orientation = orientationSelect.value;
    const quality = parseFloat(qualitySlider ? qualitySlider.value : 0.85);
    
    const buffer = new BinaryBuffer();
    // Write PDF Header (including binary file comment)
    buffer.writeString("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n");
    
    const offsets = [];
    let objCount = 0;
    
    function beginObject() {
      objCount++;
      offsets[objCount] = buffer.length;
      buffer.writeString(`${objCount} 0 obj\n`);
      return objCount;
    }
    
    function endObject() {
      buffer.writeString("endobj\n");
    }

    // Catalog (Obj 1)
    beginObject();
    buffer.writeString("<< /Type /Catalog /Pages 2 0 R >>\n");
    endObject();
    
    // Write placeholder Pages Obj 2
    offsets[2] = buffer.length;
    buffer.writeString("2 0 obj\n<< /Type /Pages /Kids [");
    for (let i = 0; i < filesList.length; i++) {
      buffer.writeString(`${3 + i * 3} 0 R `);
    }
    buffer.writeString(`] /Count ${filesList.length} >>\n`);
    endObject();
    objCount = 2; // Set count to 2 so next object starts at 3

    // Render each image onto canvas and compile
    for (let i = 0; i < filesList.length; i++) {
      const item = filesList[i];
      const img = await loadImage(item.src);
      
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ctx.drawImage(img, 0, 0);
      
      // Convert Canvas to JPEG (this respects browser EXIF and creates a compliant DCT stream)
      const dataUrl = canvas.toDataURL('image/jpeg', quality);
      const base64 = dataUrl.split(',')[1];
      const binaryString = atob(base64);
      const jpegBytes = new Uint8Array(binaryString.length);
      for (let k = 0; k < binaryString.length; k++) {
        jpegBytes[k] = binaryString.charCodeAt(k);
      }
      
      // Determine page dimensions
      let pageWidth, pageHeight;
      const imgW = img.naturalWidth;
      const imgH = img.naturalHeight;
      
      if (pageSize === 'fit') {
        if (orientation === 'landscape') {
          pageWidth = Math.max(imgW, imgH);
          pageHeight = Math.min(imgW, imgH);
        } else {
          pageWidth = Math.min(imgW, imgH);
          pageHeight = Math.max(imgW, imgH);
        }
      } else {
        let baseW = 595.275; // A4
        let baseH = 841.89;
        if (pageSize === 'letter') {
          baseW = 612;
          baseH = 792;
        }
        
        if (orientation === 'landscape') {
          pageWidth = Math.max(baseW, baseH);
          pageHeight = Math.min(baseW, baseH);
        } else {
          pageWidth = Math.min(baseW, baseH);
          pageHeight = Math.max(baseW, baseH);
        }
      }
      
      // Calculate scaling & translation matrix to center image maintaining aspect ratio
      const scale = Math.min(pageWidth / imgW, pageHeight / imgH);
      const renderW = imgW * scale;
      const renderH = imgH * scale;
      const posX = (pageWidth - renderW) / 2;
      const posY = (pageHeight - renderH) / 2;
      
      // Write Page Object (Obj 3 + i*3)
      const pageId = beginObject();
      buffer.writeString(`<< /Type /Page /Parent 2 0 R /MediaBox [ 0 0 ${pageWidth.toFixed(3)} ${pageHeight.toFixed(3)} ] /Contents ${pageId + 1} 0 R /Resources << /XObject << /Im1 ${pageId + 2} 0 R >> >> >>\n`);
      endObject();
      
      // Write Content Stream (Obj 3 + i*3 + 1)
      const contentId = beginObject();
      const contentStream = 'q\n' + renderW.toFixed(3) + ' 0 0 ' + renderH.toFixed(3) + ' ' + posX.toFixed(3) + ' ' + posY.toFixed(3) + ' cm\n/Im1 Do\nQ\n';
      buffer.writeString(`<< /Length ${contentStream.length} >>\nstream\n${contentStream}endstream\n`);
      endObject();
      
      // Write Image Stream (Obj 3 + i*3 + 2)
      beginObject();
      buffer.writeString(`<< /Type /XObject /Subtype /Image /Width ${imgW} /Height ${imgH} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpegBytes.length} >>\nstream\n`);
      buffer.writeBytes(jpegBytes);
      buffer.writeString("\nendstream\n");
      endObject();
    }
    
    // Write xref Table
    const startXrefOffset = buffer.length;
    buffer.writeString("xref\n");
    buffer.writeString(`0 ${objCount + 1}\n`);
    
    // Object 0 entry (must be exactly 20 bytes)
    buffer.writeString("0000000000 65535 f\r\n");
    for (let i = 1; i <= objCount; i++) {
      const offsetStr = String(offsets[i]).padStart(10, '0');
      buffer.writeString(`${offsetStr} 00000 n\r\n`);
    }
    
    // Write Trailer
    buffer.writeString("trailer\n");
    buffer.writeString(`<< /Size ${objCount + 1} /Root 1 0 R >>\n`);
    buffer.writeString("startxref\n");
    buffer.writeString(`${startXrefOffset}\n`);
    buffer.writeString("%%EOF\n");
    
    return buffer.toBlob("application/pdf");
  }

  // Async loader helper
  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = (e) => reject(e);
      img.src = src;
    });
  }

  // Reset Tool
  if (resetBtn) {
    resetBtn.addEventListener('click', resetTool);
  }

  function resetTool() {
    filesList.forEach(item => {
      URL.revokeObjectURL(item.src);
    });
    filesList = [];
    currentFileId = 0;
    
    if (fileInput) fileInput.value = '';
    pdfFileList.innerHTML = '';
    
    downloadBtn.style.display = 'none';
    toolWorkspace.style.display = 'none';
    resetBtn.style.display = 'none';
    dropZone.style.display = 'flex';
    
    if (generatedPdfURL) {
      URL.revokeObjectURL(generatedPdfURL);
      generatedPdfURL = null;
    }
    generatedPdfBlob = null;
    clearError();
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

  // Custom Binary Buffer classes
  class BinaryBuffer {
    constructor() {
      this.chunks = [];
      this.length = 0;
    }
    writeString(str) {
      const bytes = new Uint8Array(str.length);
      for (let i = 0; i < str.length; i++) {
        bytes[i] = str.charCodeAt(i) & 0xFF;
      }
      this.chunks.push(bytes);
      this.length += bytes.length;
    }
    writeBytes(bytes) {
      this.chunks.push(new Uint8Array(bytes));
      this.length += bytes.length;
    }
    toBlob(mimeType) {
      return new Blob(this.chunks, { type: mimeType });
    }
  }
});
