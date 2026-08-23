/* ==========================================================================
   Ask SudoGrep AI — Lightweight Branded Chatbot
   Architecture: ChatService → AIProvider → KnowledgeProvider
   Zero-cost, zero-backend. Local knowledge base with pattern matching.
   API abstraction layer allows backend wiring without UI changes.
   ========================================================================== */

(function () {
  'use strict';

  /* =========================================================================
     KNOWLEDGE PROVIDER — All verified facts about SudoGrep
     Never invent data. Only facts confirmed from the website source.
  ========================================================================= */
  const KnowledgeProvider = {

    // ── Tools ──────────────────────────────────────────────────────────────
    tools: [
      { name: 'Image Compressor', desc: 'Compress images online — reduce file size while preserving quality.', url: '/image-compressor/' },
      { name: 'Image Resizer', desc: 'Resize images to exact pixel dimensions instantly in your browser.', url: '/image-resizer/' },
      { name: 'Image to PDF', desc: 'Convert JPG, PNG, and other images into a single PDF document.', url: '/image-to-pdf/' },
      { name: 'Image Converter', desc: 'Convert between JPG, PNG, and WebP formats.', url: '/image-converter/' },
      { name: 'JPG to PDF', desc: 'Turn JPG images into PDF files instantly.', url: '/jpg-to-pdf/' },
      { name: 'JPG to PNG', desc: 'Convert JPG images to PNG format.', url: '/jpg-to-png/' },
      { name: 'JPG to WebP', desc: 'Convert JPG images to WebP for faster web performance.', url: '/jpg-to-webp/' },
      { name: 'PNG to JPG', desc: 'Convert PNG images to JPG format.', url: '/png-to-jpg/' },
      { name: 'WebP to JPG', desc: 'Convert WebP images to JPG format.', url: '/webp-to-jpg/' },
      { name: 'Compress to 100KB', desc: 'Compress an image down to approximately 100KB.', url: '/compress-image-to-100kb/' },
      { name: 'Compress to 50KB', desc: 'Compress an image down to approximately 50KB.', url: '/compress-image-to-50kb/' },
      { name: 'Compress to 200KB', desc: 'Compress an image down to approximately 200KB.', url: '/compress-image-to-200kb/' },
      { name: 'Compress JPG to 50KB', desc: 'Compress a JPG image to 50KB.', url: '/compress-jpg-to-50kb/' },
      { name: 'Compress PNG to 50KB', desc: 'Compress a PNG image to 50KB.', url: '/compress-png-to-50kb/' },
      { name: 'Resize for Online Forms', desc: 'Resize and compress photos to meet online form or document requirements.', url: '/resize-image-for-online-forms/' },
      { name: 'Resize for Passport', desc: 'Resize a photo to standard passport dimensions.', url: '/resize-image-for-passport/' },
    ],

    // ── Apps ───────────────────────────────────────────────────────────────
    apps: [
      {
        name: 'File Forge: Convert & Extract',
        desc: 'Utility app to convert and extract files directly on your Android device.',
        url: 'https://play.google.com/store/apps/details?id=dev.kartikpatel.fileforge',
        page: '/apps/file-forge/',
      },
      {
        name: 'BillBuddy – Bill Tracker',
        desc: 'Smart bill reminder and payment tracker to stay organised and avoid late fees.',
        url: 'https://play.google.com/store/apps/details?id=com.billreminder.bill_reminder',
        page: '/apps/billbuddy/',
      },
      {
        name: 'Zip Connect – Node Puzzle',
        desc: 'A beautifully crafted puzzle game — connect nodes, clear paths, and challenge your logic.',
        url: 'https://play.google.com/store/apps/details?id=in.sudogrep.zip_connect',
        page: '/apps/zip-connect/',
      },
      {
        name: 'Aarti Sangrah',
        desc: 'A local, spiritual prayer list and Aarti collection app.',
        url: 'https://play.google.com/store/apps/details?id=com.kp.kartik.aarti',
        page: '/apps/aarti-sangrah/',
      },
      {
        name: 'KB Snap',
        desc: 'Compress photos to any target KB size for online forms and document submissions.',
        url: 'https://play.google.com/store/apps/details?id=in.sudogrep.kb_snap&hl=en_IN',
        page: '/apps/kb-snap/',
      },
      {
        name: 'Ghost Trap: Reveal the World',
        desc: 'Tactical arcade puzzle game — claim territory, avoid ghosts, and reveal famous landmarks from around the world.',
        url: 'https://play.google.com/store/apps/details?id=in.sudogrep.ghosttrap',
        page: '/apps/ghost-trap/',
      },
    ],

    // ── Insights ────────────────────────────────────────────────────────────
    insights: [
      {
        title: 'How AI Agents Are Changing Software Development',
        category: 'AI',
        url: '/blog/how-ai-agents-are-changing-software-development/',
      },
      {
        title: 'Flutter App Development Trends in 2026',
        category: 'Mobile Development',
        url: '/blog/flutter-app-development-trends-2026/',
      },
      {
        title: 'Best Free Image Compression Tools',
        category: 'Web Development',
        url: '/blog/best-free-image-compression-tools/',
      },
    ],

    // ── Contact ─────────────────────────────────────────────────────────────
    contact: {
      whatsapp: 'https://wa.me/917977440556?text=Hi%20SudoGrep%2C%20I%27d%20like%20to%20discuss%20a%20software%20project.',
      calendly: 'https://calendly.com/sudogrep-support/30min',
      email: 'support@sudogrep.in',
      reddit: 'https://www.reddit.com/user/SudoGrep_27/',
      form: '/contact/',
    },

    // ── Pattern matching ─────────────────────────────────────────────────────
    match(message) {
      const q = message.toLowerCase().trim();

      // ── Welcome / identity ─────────────────────────────────────────────
      if (/^(hi|hello|hey|howdy|hiya|sup|yo)\b/.test(q) || q === '') {
        return this._welcome();
      }

      if (/what is sudogrep|who is sudogrep|about sudogrep|tell me about/.test(q)) {
        return this._aboutSudogrep();
      }

      if (/what does sudogrep (do|make|build|offer|create)|what (do|can) (you|sudogrep)/.test(q)) {
        return this._whatWeDo();
      }

      // ── Tools ─────────────────────────────────────────────────────────
      if (/compress.*image|image.*compress|reduce.*image|shrink.*image|make.*image.*smaller|compress.*photo|photo.*compress/.test(q)) {
        return this._toolResponse(this.tools[0]); // Image Compressor
      }

      if (/compress.*100\s*kb|100\s*kb/.test(q)) {
        return this._toolResponse(this.tools.find(t => t.name.includes('100KB')));
      }

      if (/compress.*50\s*kb|50\s*kb/.test(q)) {
        const t = this.tools.find(t => t.name === 'Compress to 50KB');
        return this._toolResponse(t);
      }

      if (/compress.*200\s*kb|200\s*kb/.test(q)) {
        return this._toolResponse(this.tools.find(t => t.name.includes('200KB')));
      }

      if (/resize.*image|image.*resize|change.*size|dimensions/.test(q)) {
        if (/passport/.test(q)) return this._toolResponse(this.tools.find(t => t.name.includes('Passport')));
        if (/form|document|online form/.test(q)) return this._toolResponse(this.tools.find(t => t.name.includes('Online Forms')));
        return this._toolResponse(this.tools[1]); // Image Resizer
      }

      if (/image.*pdf|jpg.*pdf|png.*pdf|convert.*pdf|pdf/.test(q)) {
        if (/jpg|jpeg/.test(q)) return this._toolResponse(this.tools.find(t => t.name === 'JPG to PDF'));
        return this._toolResponse(this.tools[2]); // Image to PDF
      }

      if (/convert.*image|image.*convert|jpg.*png|png.*jpg|webp|convert.*format/.test(q)) {
        if (/jpg.*webp|jpeg.*webp/.test(q)) return this._toolResponse(this.tools.find(t => t.name === 'JPG to WebP'));
        if (/webp.*jpg/.test(q)) return this._toolResponse(this.tools.find(t => t.name === 'WebP to JPG'));
        if (/png.*jpg/.test(q)) return this._toolResponse(this.tools.find(t => t.name === 'PNG to JPG'));
        if (/jpg.*png|jpeg.*png/.test(q)) return this._toolResponse(this.tools.find(t => t.name === 'JPG to PNG'));
        return this._toolResponse(this.tools[3]); // Image Converter
      }

      if (/what.*tool|free.*tool|tool.*free|show.*tool|list.*tool|available.*tool|all.*tool/.test(q)) {
        return this._allTools();
      }

      if (/tool|utility|utilities|online tool/.test(q)) {
        return this._allTools();
      }

      if (/account|sign.?up|login|register/.test(q)) {
        return {
          html: `<p>You don't need an account to use any SudoGrep tools. All tools are free and open to everyone — no sign-up required.</p>
<p><a href="/free-tools/" class="chat-link">Explore Free Tools →</a></p>
<p style="font-size:0.85rem; color: var(--text-muted);">You can also read the <a href="/#faq" class="chat-link">FAQ</a> for more details.</p>`,
        };
      }

      if (/file.*upload|upload.*file|store.*file|file.*store|data.*safe|data.*privacy|privacy/.test(q)) {
        return {
          html: `<p>SudoGrep tools run entirely in your browser — your files are never uploaded to any server. All processing happens locally on your device.</p>
<p><a href="/#faq" class="chat-link">Read the FAQ →</a></p>`,
        };
      }

      // ── Applications ──────────────────────────────────────────────────
      if (/ghost.?trap/.test(q)) {
        const app = this.apps.find(a => a.name.includes('Ghost Trap'));
        return {
          html: `<p><strong>Ghost Trap: Reveal the World</strong> is a tactical arcade puzzle game by SudoGrep. You claim territory, avoid ghosts, and reveal famous landmarks from around the world.</p>
<p>
  <a href="${app.page}" class="chat-link">Learn more about Ghost Trap →</a><br>
  <a href="${app.url}" target="_blank" rel="noopener" class="chat-link">Download on Google Play →</a>
</p>`,
        };
      }

      if (/kb.?snap|kb snap/.test(q)) {
        const app = this.apps.find(a => a.name.includes('KB Snap'));
        return {
          html: `<p><strong>KB Snap</strong> is an Android app that lets you compress photos to any target KB size — ideal for passport photos, online form uploads, and document requirements.</p>
<p><a href="${app.url}" target="_blank" rel="noopener" class="chat-link">Download KB Snap on Google Play →</a></p>`,
        };
      }

      if (/file.?forge|fileforge/.test(q)) {
        const app = this.apps.find(a => a.name.includes('File Forge'));
        return {
          html: `<p><strong>File Forge: Convert & Extract</strong> is a utility app that converts and extracts files directly on your Android device.</p>
<p><a href="${app.url}" target="_blank" rel="noopener" class="chat-link">Download File Forge on Google Play →</a></p>`,
        };
      }

      if (/bill.?buddy|billbuddy/.test(q)) {
        const app = this.apps.find(a => a.name.includes('BillBuddy'));
        return {
          html: `<p><strong>BillBuddy – Bill Tracker</strong> is a smart bill reminder and payment tracker app to help you stay organised and avoid late fees.</p>
<p><a href="${app.url}" target="_blank" rel="noopener" class="chat-link">Download BillBuddy on Google Play →</a></p>`,
        };
      }

      if (/zip.?connect|zipconnect/.test(q)) {
        const app = this.apps.find(a => a.name.includes('Zip Connect'));
        return {
          html: `<p><strong>Zip Connect – Node Puzzle</strong> is a beautifully crafted puzzle game where you connect nodes, clear paths, and challenge your logic.</p>
<p><a href="${app.url}" target="_blank" rel="noopener" class="chat-link">Download Zip Connect on Google Play →</a></p>`,
        };
      }

      if (/aarti|sangrah/.test(q)) {
        const app = this.apps.find(a => a.name.includes('Aarti'));
        return {
          html: `<p><strong>Aarti Sangrah</strong> is a local, spiritual prayer list and Aarti collection app for Android.</p>
<p><a href="${app.url}" target="_blank" rel="noopener" class="chat-link">Download Aarti Sangrah on Google Play →</a></p>`,
        };
      }

      if (/what.*app|app.*sudogrep|mobile.*app|android.*app|show.*app|list.*app|all.*app/.test(q)) {
        return this._allApps();
      }

      if (/app|application|android|google play|play store|download/.test(q)) {
        return this._allApps();
      }

      // ── Services ──────────────────────────────────────────────────────
      if (/flutter|cross.?platform/.test(q)) {
        return this._serviceResponse('Flutter & Cross-Platform Apps', 'SudoGrep builds cross-platform Flutter applications for Android and iOS.');
      }

      if (/ai.*app|ai.*solution|ai.*software|build.*ai|custom.*ai|ai.*integrat|gemini|openai|rag|chatbot.*build/.test(q)) {
        return {
          html: `<p>Yes — SudoGrep builds AI-powered applications, including:</p>
<ul>
  <li>AI agent frameworks</li>
  <li>Retrieval-Augmented Generation (RAG) systems</li>
  <li>Gemini &amp; OpenAI integrations</li>
  <li>On-device AI features</li>
</ul>
<p><a href="/ai-solutions/" class="chat-link">Explore AI Solutions →</a></p>
${this._contactCTA()}`,
        };
      }

      if (/build.*website|website.*build|web.*app|website.*develop|web.*develop/.test(q)) {
        return {
          html: `<p>SudoGrep builds web platforms including static HTML5 sites, Next.js applications, Vite apps, and interactive admin dashboards.</p>
<p><a href="/services/" class="chat-link">View Services →</a></p>
${this._contactCTA()}`,
        };
      }

      if (/service|hire|work.*with|build.*for|custom|project|develop/.test(q)) {
        return this._services();
      }

      // ── Insights / Blog ───────────────────────────────────────────────
      if (/flutter.*article|article.*flutter|flutter.*blog|blog.*flutter/.test(q)) {
        const i = this.insights.find(x => x.category === 'Mobile Development');
        return {
          html: `<p>Here's a Flutter article from SudoGrep Insights:</p>
<p><a href="${i.url}" class="chat-link">${i.title} →</a></p>
<p><a href="/blog/" class="chat-link">View all Insights →</a></p>`,
        };
      }

      if (/ai.*article|article.*ai|ai.*blog|blog.*ai/.test(q)) {
        const i = this.insights.find(x => x.category === 'AI');
        return {
          html: `<p>Here's an AI article from SudoGrep Insights:</p>
<p><a href="${i.url}" class="chat-link">${i.title} →</a></p>
<p><a href="/blog/" class="chat-link">View all Insights →</a></p>`,
        };
      }

      if (/compress.*article|image.*article|article.*compress/.test(q)) {
        const i = this.insights.find(x => x.title.includes('Compression'));
        return {
          html: `<p>Here's an article on image compression:</p>
<p><a href="${i.url}" class="chat-link">${i.title} →</a></p>
<p><a href="/blog/" class="chat-link">View all Insights →</a></p>`,
        };
      }

      if (/article|blog|insight|read|guide|tutorial/.test(q)) {
        return this._allInsights();
      }

      // ── Contact ───────────────────────────────────────────────────────
      if (/whatsapp/.test(q)) {
        return {
          html: `<p>You can reach SudoGrep via WhatsApp for project discussions.</p>
<p><a href="${this.contact.whatsapp}" target="_blank" rel="noopener" class="chat-link">Chat on WhatsApp →</a></p>`,
        };
      }

      if (/calendly|book.*call|call.*book|schedule|meeting|appointment/.test(q)) {
        return {
          html: `<p>You can book a 30-minute call with SudoGrep via Calendly.</p>
<p><a href="${this.contact.calendly}" target="_blank" rel="noopener" class="chat-link">Book a Call →</a></p>`,
        };
      }

      if (/email|mail|support/.test(q)) {
        return {
          html: `<p>You can email SudoGrep at: <a href="mailto:${this.contact.email}" class="chat-link">${this.contact.email}</a></p>`,
        };
      }

      if (/contact|reach|touch|get in touch|talk to/.test(q)) {
        return {
          html: `<p>You can contact SudoGrep through any of these channels:</p>
<ul>
  <li><a href="${this.contact.whatsapp}" target="_blank" rel="noopener" class="chat-link">WhatsApp →</a></li>
  <li><a href="${this.contact.calendly}" target="_blank" rel="noopener" class="chat-link">Book a Call (Calendly) →</a></li>
  <li><a href="mailto:${this.contact.email}" class="chat-link">Email: ${this.contact.email}</a></li>
  <li><a href="${this.contact.form}" class="chat-link">Contact Form →</a></li>
</ul>`,
        };
      }

      if (/reddit/.test(q)) {
        return {
          html: `<p>SudoGrep is on Reddit: <a href="${this.contact.reddit}" target="_blank" rel="noopener" class="chat-link">Visit SudoGrep on Reddit →</a></p>`,
        };
      }

      if (/faq|frequent|common.*question/.test(q)) {
        return {
          html: `<p>You can find answers to common questions in the FAQ section below.</p>
<p><a href="/#faq" class="chat-link">Read the FAQ →</a></p>`,
        };
      }

      // ── Fallback ───────────────────────────────────────────────────────
      return this._fallback();
    },

    // ── Response builders ────────────────────────────────────────────────────
    _welcome() {
      return {
        html: `<p>Hi! I'm <strong>Ask SudoGrep AI</strong> 👋</p>
<p>I can help you find SudoGrep tools, apps, services, insights, and contact options.</p>
<p>What would you like to know?</p>`,
        showQuickActions: true,
      };
    },

    _aboutSudogrep() {
      return {
        html: `<p><strong>SudoGrep</strong> is a software studio that builds free online tools, Android applications, and custom software &amp; AI solutions.</p>
<ul>
  <li>🔧 <a href="/free-tools/" class="chat-link">Free browser tools</a> — image compression, resizing, PDF conversion, and more</li>
  <li>📱 <a href="/apps/" class="chat-link">Android apps</a> — published on Google Play</li>
  <li>🤖 <a href="/ai-solutions/" class="chat-link">AI &amp; software development</a> — custom builds for clients</li>
</ul>`,
      };
    },

    _whatWeDo() {
      return {
        html: `<p>SudoGrep builds three types of products:</p>
<ul>
  <li><strong>Free Tools</strong> — client-side browser utilities (image tools, PDF, conversion)</li>
  <li><strong>Mobile Apps</strong> — Android applications on Google Play</li>
  <li><strong>Custom Software &amp; AI</strong> — Flutter, web platforms, AI agent systems, RAG, and integrations</li>
</ul>
<p>
  <a href="/free-tools/" class="chat-link">Explore Tools →</a>&nbsp;&nbsp;
  <a href="/apps/" class="chat-link">View Apps →</a>&nbsp;&nbsp;
  <a href="/services/" class="chat-link">View Services →</a>
</p>`,
      };
    },

    _toolResponse(tool) {
      if (!tool) return this._fallback();
      return {
        html: `<p>You can use <strong>${tool.name}</strong> — ${tool.desc}</p>
<p><a href="${tool.url}" class="chat-link">Open ${tool.name} →</a></p>
<p style="font-size:0.85rem; color:var(--text-muted);">All SudoGrep tools run 100% in your browser. No file uploads, no account needed.</p>`,
      };
    },

    _allTools() {
      const listed = this.tools.slice(0, 6);
      const items = listed.map(t => `<li><a href="${t.url}" class="chat-link">${t.name}</a></li>`).join('');
      return {
        html: `<p>SudoGrep offers free browser-based tools including:</p>
<ul>${items}</ul>
<p><a href="/free-tools/" class="chat-link">View all Free Tools →</a></p>
<p style="font-size:0.85rem; color:var(--text-muted);">All tools run in your browser — no upload, no account required.</p>`,
      };
    },

    _allApps() {
      const items = this.apps.map(a => `<li><a href="${a.page}" class="chat-link">${a.name}</a></li>`).join('');
      return {
        html: `<p>SudoGrep has published the following Android applications:</p>
<ul>${items}</ul>
<p><a href="/apps/" class="chat-link">View all Applications →</a>&nbsp;&nbsp;<a href="https://play.google.com/store/apps/dev?id=7135905913091619860" target="_blank" rel="noopener" class="chat-link">Google Play →</a></p>`,
      };
    },

    _allInsights() {
      const items = this.insights.map(i => `<li><a href="${i.url}" class="chat-link">${i.title}</a> <span style="color:var(--text-muted);font-size:0.8rem;">(${i.category})</span></li>`).join('');
      return {
        html: `<p>Recent articles from SudoGrep Insights:</p>
<ul>${items}</ul>
<p><a href="/blog/" class="chat-link">View all Insights →</a></p>`,
      };
    },

    _services() {
      return {
        html: `<p>SudoGrep offers custom software and AI development, including:</p>
<ul>
  <li>Flutter, Android &amp; iOS mobile apps</li>
  <li>Web platforms (static, Next.js, Vite)</li>
  <li>AI integrations (Gemini, OpenAI, RAG, agents)</li>
  <li>Backend &amp; cloud systems</li>
</ul>
<p><a href="/services/" class="chat-link">View Services →</a>&nbsp;&nbsp;<a href="/ai-solutions/" class="chat-link">AI Solutions →</a></p>
${this._contactCTA()}`,
      };
    },

    _contactCTA() {
      return `<p style="margin-top:0.75rem;">Ready to discuss your project?</p>
<p>
  <a href="${this.contact.whatsapp}" target="_blank" rel="noopener" class="chat-link">WhatsApp →</a>&nbsp;&nbsp;
  <a href="${this.contact.calendly}" target="_blank" rel="noopener" class="chat-link">Book a Call →</a>&nbsp;&nbsp;
  <a href="${this.contact.form}" class="chat-link">Contact Form →</a>
</p>`;
    },

    _serviceResponse(name, desc) {
      return {
        html: `<p>${desc}</p>
<p><a href="/services/" class="chat-link">View Services →</a></p>
${this._contactCTA()}`,
      };
    },

    _fallback() {
      return {
        html: `<p>I don't have that information about SudoGrep yet. You can contact the team directly for more details.</p>
${this.contact ? `<p>
  <a href="${this.contact.whatsapp}" target="_blank" rel="noopener" class="chat-link">WhatsApp →</a>&nbsp;&nbsp;
  <a href="${this.contact.form}" class="chat-link">Contact Form →</a>
</p>` : ''}
<p style="font-size:0.85rem; color:var(--text-muted);">Or explore the site: <a href="/free-tools/" class="chat-link">Tools</a> · <a href="/apps/" class="chat-link">Apps</a> · <a href="/blog/" class="chat-link">Insights</a></p>`,
      };
    },
  };

  /* =========================================================================
     AI PROVIDER — Abstraction layer for future AI backend
     Currently delegates to KnowledgeProvider.
     To add a real AI API: replace getResponse() body only.
  ========================================================================= */
  const AIProvider = {
    async getResponse(message) {
      // Future: replace this block with a fetch() to your secure backend
      // e.g. fetch('/api/chat', { method: 'POST', body: JSON.stringify({ message }) })
      return KnowledgeProvider.match(message);
    },
  };

  /* =========================================================================
     CHAT SERVICE — Session management, message dispatch
  ========================================================================= */
  const ChatService = {
    history: [],

    async send(message) {
      this.history.push({ role: 'user', content: message });
      const response = await AIProvider.getResponse(message);
      this.history.push({ role: 'bot', content: response });
      return response;
    },

    clear() {
      this.history = [];
    },
  };

  /* =========================================================================
     QUICK ACTIONS — Labelled intents mapped to messages
  ========================================================================= */
  const QUICK_ACTIONS = [
    { label: '🔧 Find a Tool',        message: 'What free tools are available?' },
    { label: '📱 Explore Apps',       message: 'What apps has SudoGrep built?' },
    { label: '🤖 AI Solutions',       message: 'Can SudoGrep build AI-powered software?' },
    { label: '📝 Read Insights',      message: 'Show me the latest articles.' },
    { label: '💼 Work With SudoGrep', message: 'What services does SudoGrep offer?' },
    { label: '📅 Book a Call',        message: 'How can I book a call?' },
  ];

  /* =========================================================================
     CHAT UI — DOM management
  ========================================================================= */
  const ChatUI = {
    window: null,
    messagesEl: null,
    inputEl: null,
    sendBtn: null,
    toggleBtn: null,
    isOpen: false,
    initialized: false,

    init() {
      this.window = document.getElementById('askAiChatWindow');
      this.messagesEl = document.getElementById('chatMessages');
      this.inputEl = document.getElementById('chatInput');
      this.sendBtn = document.getElementById('chatSendBtn');
      this.toggleBtn = document.getElementById('askAiToggleBtn');

      if (!this.window || !this.messagesEl || !this.inputEl) return;

      // Close button
      const closeBtn = document.getElementById('chatCloseBtn');
      if (closeBtn) closeBtn.addEventListener('click', () => this.close());

      // Clear button
      const clearBtn = document.getElementById('chatClearBtn');
      if (clearBtn) clearBtn.addEventListener('click', () => this.clear());

      // Send button
      if (this.sendBtn) {
        this.sendBtn.addEventListener('click', () => this._handleSend());
      }

      // Enter key to send
      if (this.inputEl) {
        this.inputEl.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this._handleSend();
          }
        });
      }

      // ESC key closes chat
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) this.close();
      });

      // Show welcome message
      this._showWelcome();
      this.initialized = true;
    },

    open() {
      if (!this.initialized) this.init();
      this.window.classList.add('chat-open');
      this.window.setAttribute('aria-hidden', 'false');
      this.toggleBtn.setAttribute('aria-expanded', 'true');
      this.isOpen = true;
      // Focus input after transition
      setTimeout(() => this.inputEl && this.inputEl.focus(), 300);
      // Announce to screen readers
      this._announce('Ask SudoGrep AI chat opened');
    },

    close() {
      this.window.classList.remove('chat-open');
      this.window.setAttribute('aria-hidden', 'true');
      this.toggleBtn.setAttribute('aria-expanded', 'false');
      this.isOpen = false;
      this.toggleBtn.focus();
    },

    toggle() {
      if (this.isOpen) this.close();
      else this.open();
    },

    clear() {
      ChatService.clear();
      if (this.messagesEl) this.messagesEl.innerHTML = '';
      this._showWelcome();
    },

    _showWelcome() {
      const welcome = KnowledgeProvider._welcome();
      this._appendBotMessage(welcome.html);
      if (welcome.showQuickActions) this._appendQuickActions();
    },

    _appendQuickActions() {
      const wrap = document.createElement('div');
      wrap.className = 'chat-quick-actions';
      wrap.setAttribute('aria-label', 'Quick topic shortcuts');
      QUICK_ACTIONS.forEach(action => {
        const btn = document.createElement('button');
        btn.className = 'chat-qa-btn';
        btn.textContent = action.label;
        btn.setAttribute('aria-label', action.message);
        btn.addEventListener('click', () => {
          this._handleUserMessage(action.message);
        });
        wrap.appendChild(btn);
      });
      this.messagesEl.appendChild(wrap);
      this._scrollToBottom();
    },

    async _handleSend() {
      const text = this.inputEl.value.trim();
      if (!text) return;
      this.inputEl.value = '';
      await this._handleUserMessage(text);
    },

    async _handleUserMessage(text) {
      // Remove quick actions once user sends a message
      const qa = this.messagesEl.querySelector('.chat-quick-actions');
      if (qa) qa.remove();

      this._appendUserMessage(text);
      this._setLoading(true);

      try {
        const response = await ChatService.send(text);
        this._setLoading(false);
        this._appendBotMessage(response.html);
        this._announce('New response from Ask SudoGrep AI');
      } catch {
        this._setLoading(false);
        this._appendBotMessage('<p>Something went wrong. Please try again.</p>');
      }
    },

    _appendUserMessage(text) {
      const wrap = document.createElement('div');
      wrap.className = 'chat-message-row chat-message-user';
      const bubble = document.createElement('div');
      bubble.className = 'chat-bubble chat-bubble-user';
      bubble.textContent = text;
      wrap.appendChild(bubble);
      this.messagesEl.appendChild(wrap);
      this._scrollToBottom();
    },

    _appendBotMessage(html) {
      const wrap = document.createElement('div');
      wrap.className = 'chat-message-row chat-message-bot';

      const avatar = document.createElement('div');
      avatar.className = 'chat-avatar';
      avatar.setAttribute('aria-hidden', 'true');
      avatar.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>`;

      const bubble = document.createElement('div');
      bubble.className = 'chat-bubble chat-bubble-bot';
      bubble.innerHTML = html;
      // Ensure all links in bot messages open safely
      bubble.querySelectorAll('a[href^="http"]').forEach(a => {
        a.setAttribute('rel', 'noopener noreferrer');
      });

      wrap.appendChild(avatar);
      wrap.appendChild(bubble);
      this.messagesEl.appendChild(wrap);
      this._scrollToBottom();
    },

    _setLoading(state) {
      let loader = document.getElementById('chatLoader');
      if (state) {
        if (loader) return;
        loader = document.createElement('div');
        loader.id = 'chatLoader';
        loader.className = 'chat-message-row chat-message-bot';
        loader.setAttribute('aria-live', 'polite');
        loader.setAttribute('aria-label', 'Loading response');
        loader.innerHTML = `
          <div class="chat-avatar" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
          </div>
          <div class="chat-bubble chat-bubble-bot chat-typing">
            <span></span><span></span><span></span>
          </div>`;
        this.messagesEl.appendChild(loader);
        this._scrollToBottom();
      } else {
        if (loader) loader.remove();
      }
    },

    _scrollToBottom() {
      if (this.messagesEl) {
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
      }
    },

    _announce(text) {
      let live = document.getElementById('chatAriaLive');
      if (!live) {
        live = document.createElement('div');
        live.id = 'chatAriaLive';
        live.setAttribute('aria-live', 'polite');
        live.setAttribute('aria-atomic', 'true');
        live.className = 'sr-only';
        document.body.appendChild(live);
      }
      live.textContent = '';
      setTimeout(() => { live.textContent = text; }, 50);
    },
  };

  /* =========================================================================
     INIT — Wire toggle button and expose ChatUI
  ========================================================================= */
  function init() {
    const toggleBtn = document.getElementById('askAiToggleBtn');
    if (!toggleBtn) return;
    toggleBtn.addEventListener('click', () => ChatUI.toggle());
    // Pre-init the UI so the first open is instant
    ChatUI.init();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
