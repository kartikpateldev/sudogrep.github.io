# Contact Form Integration Guide

This document describes the design and integration of the contact form for SudoGrep.

---

## 1. Current Architecture

The contact form is configured to process and route user messages without a backend server using **Web3Forms**, a secure, client-side email routing service.

*   **Frontend HTML**: Implemented identically on:
    *   **Contact Page**: [contact/index.html](file:///Users/kt/workspace/portfolios/sudogrep.github.io/contact/index.html) (line 141)
    *   **Homepage Section**: [index.html](file:///Users/kt/workspace/portfolios/sudogrep.github.io/index.html) (line 654)
*   **Logic Handler**: Implemented sitewide in [js/global.js](file:///Users/kt/workspace/portfolios/sudogrep.github.io/js/global.js) (lines 84-176). It listens for form submissions, intercepts the request, disables the submit button, updates text states to `"Sending..."`, performs a client-side fetch, and displays styled inline success/failure alerts.
*   **Routing Access Key**: Uses a public routing token (`d770a694-461b-4aae-89f8-1a2313c66e11`) mapped to `support@sudogrep.in` on the Web3Forms server.

---

## 2. Forms Fields Configuration

The form includes specific configuration parameters for Web3Forms:

```html
<!-- Web3Forms Routing Configuration -->
<input type="hidden" name="access_key" value="d770a694-461b-4aae-89f8-1a2313c66e11">
<input type="hidden" name="subject" value="New SudoGrep Project Inquiry">
<input type="hidden" name="from_name" value="SudoGrep Contact Form">

<!-- Spam Honeypot Protection (Hidden from Users) -->
<input type="checkbox" name="botcheck" class="hidden" style="display: none;">
```

### Parameter Explanations
*   `access_key`: Mapped routing token identifying the destination email address.
*   `subject`: Customize the subject line of emails sent to your inbox.
*   `from_name`: Customize the sender name visible in your email client.
*   `botcheck` (Honeypot): An invisible checkbox field. If a bot parses the HTML and checks it, the submission is automatically discarded as spam by Web3Forms.

---

## 3. Customizing the Recipient Email

To update where contact submissions are sent:

1.  Go to [Web3Forms](https://web3forms.com/) and register the target email (e.g. `your-email@domain.com`) to generate a new free access key.
2.  Copy your new key.
3.  Replace the `access_key` input value in both HTML files:
    *   [contact/index.html](file:///Users/kt/workspace/portfolios/sudogrep.github.io/contact/index.html#L143)
    *   [index.html](file:///Users/kt/workspace/portfolios/sudogrep.github.io/index.html#L656)
4.  Commit the changes and deploy. No backend reconfiguration is required.

---

## 4. Local Testing & Verification

Because Web3Forms is client-side, the contact form can be tested locally:

1.  Run a local HTTP server:
    ```bash
    python3 -m http.server 9090
    ```
2.  Open `http://localhost:9090/contact/` in your browser.
3.  Fill out the form inputs and click **Send Message**.
4.  Upon clicking send:
    *   The submit button changes to `"Sending..."` and is disabled.
    *   A network request is sent to `https://api.web3forms.com/submit`.
    *   A success banner displays: *"Thanks — your message has been sent. We'll get back to you soon."*
    *   The form inputs are cleared.
    *   An email is delivered to the configured inbox.

---

## 5. Troubleshooting

### Form fails to submit (Red Failure UI):
1.  **Network connection**: Verify your device is connected to the internet (Web3Forms requires active network access).
2.  **Access Key validity**: Make sure the Web3Forms key has not been deleted or deactivated.
3.  **Honeypot trigger**: If testing programmatically, ensure your script is not checking the `botcheck` input field.

### Stylesheet or UI glitches:
*   The contact card structures, buttons, and alert animations reuse layouts in [css/home.css](file:///Users/kt/workspace/portfolios/sudogrep.github.io/css/home.css) and [css/components.css](file:///Users/kt/workspace/portfolios/sudogrep.github.io/css/components.css). Ensure these CSS sheets remain linked in headers.
