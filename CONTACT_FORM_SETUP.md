# Contact Form Setup Guide

## Overview
The contact form is configured to send emails using PHP's `mail()` function. Here are the options to make it work:

## Option 1: Using PHP on Your Server (Recommended for Production)

### Requirements:
- Web server with PHP support (Apache, Nginx, etc.)
- PHP mail configuration

### Steps:
1. Upload all files including `send-email.php` to your web server
2. Ensure your server has PHP mail configured
3. Update the email address in `send-email.php` (line 21):
   ```php
   $to = 'support@sudogrep.in'; // Change to your email
   ```
4. Test the form by submitting a message

### Server Configuration:
Most shared hosting providers have PHP mail pre-configured. For VPS/dedicated servers, you may need to:
- Install and configure a mail server (Postfix, Sendmail, etc.)
- Or use SMTP with PHPMailer library

## Option 2: Using Third-Party Email Services

### FormSubmit.co (No Backend Required)
1. Replace the form action in `index.html`:
   ```html
   <form action="https://formsubmit.co/support@sudogrep.in" method="POST">
   ```
2. Add hidden fields for customization:
   ```html
   <input type="hidden" name="_subject" value="New Contact Form Submission">
   <input type="hidden" name="_captcha" value="false">
   <input type="hidden" name="_next" value="https://sudogrep.in/thank-you.html">
   ```

### Formspree.io
1. Sign up at https://formspree.io
2. Create a new form and get your endpoint
3. Update the form action:
   ```html
   <form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
   ```

### EmailJS (Client-side JavaScript)
1. Sign up at https://www.emailjs.com/
2. Create an email service and template
3. Replace the JavaScript fetch call with EmailJS SDK
4. No PHP file needed

## Option 3: Using Netlify Forms (If hosting on Netlify)

1. Add `netlify` attribute to the form:
   ```html
   <form name="contact" method="POST" data-netlify="true">
   ```
2. Add a hidden input:
   ```html
   <input type="hidden" name="form-name" value="contact">
   ```
3. Deploy to Netlify - forms will work automatically

## Option 4: Using Google Apps Script

1. Create a Google Apps Script to receive form data
2. Deploy as web app
3. Update the fetch URL in `script.js` to your Apps Script URL
4. No PHP needed

## Testing Locally

For local testing without a mail server:
1. The form will show an error (expected)
2. Check browser console for form data
3. Use a service like MailHog or Mailtrap for local email testing

## Current Setup

The website currently uses:
- **Frontend**: HTML form with JavaScript validation
- **Backend**: PHP script (`send-email.php`) that sends emails
- **Email**: Sends to `support@sudogrep.in`

## Troubleshooting

### Form doesn't send emails:
1. Check if PHP mail is configured on your server
2. Check spam folder
3. Verify email address in `send-email.php`
4. Check server error logs

### 404 Error on submit:
1. Ensure `send-email.php` is uploaded to the server
2. Check file permissions (should be 644)
3. Verify the file path in `script.js`

### CORS Errors:
1. Ensure both HTML and PHP are on the same domain
2. Or configure CORS headers properly in PHP

## Recommended Solution for GitHub Pages

Since GitHub Pages doesn't support PHP, use one of these:
1. **FormSubmit.co** - Easiest, no signup required
2. **Formspree.io** - Free tier available, good features
3. **EmailJS** - Client-side only, no backend needed

## Need Help?

Contact: support@sudogrep.in
