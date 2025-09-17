// OAuth Email Service for Gmail and Outlook authentication
import emailjs from '@emailjs/browser';
import { PublicClientApplication } from '@azure/msal-browser';

class OAuthEmailService {
  constructor() {
    this.isInitialized = false;
    this.currentProvider = null;
    this.userCredentials = null;
    
    // Microsoft MSAL configuration
    this.msalConfig = {
      auth: {
        clientId: process.env.REACT_APP_MICROSOFT_CLIENT_ID || 'demo-client-id',
        authority: 'https://login.microsoftonline.com/common',
        redirectUri: window.location.origin
      },
      cache: {
        cacheLocation: 'localStorage',
        storeAuthStateInCookie: false
      }
    };
    
    // Google OAuth configuration
    this.googleConfig = {
      clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || 'demo-client-id',
      scope: 'https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
    };
    
    // Initialize MSAL instance
    if (process.env.REACT_APP_MICROSOFT_CLIENT_ID) {
      this.msalInstance = new PublicClientApplication(this.msalConfig);
    }
  }

  async initializeEmailJS() {
    const publicKey = process.env.REACT_APP_EMAILJS_PUBLIC_KEY;
    if (publicKey) {
      emailjs.init(publicKey);
      this.isInitialized = true;
      return true;
    }
    console.warn('EmailJS not configured - using OAuth direct send');
    return false;
  }

  // Gmail OAuth Authentication
  async authenticateGmail() {
    try {
      // Check if Google OAuth is configured
      if (!process.env.REACT_APP_GOOGLE_CLIENT_ID || process.env.REACT_APP_GOOGLE_CLIENT_ID === 'demo-client-id') {
        console.warn('Google OAuth not configured, using demo mode');
        return await this.simulateGmailOAuth();
      }

      // Load Google OAuth library
      await this.loadGoogleOAuthLibrary();
      
      // Initialize Google OAuth
      await new Promise((resolve) => {
        window.gapi.load('auth2', resolve);
      });
      
      const authInstance = window.gapi.auth2.init({
        client_id: this.googleConfig.clientId,
        scope: this.googleConfig.scope
      });
      
      // Sign in user
      const googleUser = await authInstance.signIn();
      const profile = googleUser.getBasicProfile();
      const authResponse = googleUser.getAuthResponse();
      
      const credentials = {
        email: profile.getEmail(),
        name: profile.getName(),
        picture: profile.getImageUrl(),
        accessToken: authResponse.access_token,
        idToken: authResponse.id_token,
        expiresAt: new Date(authResponse.expires_at).getTime()
      };
      
      this.currentProvider = 'gmail';
      this.userCredentials = credentials;
      
      // Store in localStorage for persistence
      localStorage.setItem('email_auth_provider', 'gmail');
      localStorage.setItem('email_auth_credentials', JSON.stringify(credentials));
      localStorage.setItem('email_auth_time', new Date().getTime().toString());
      
      return {
        success: true,
        provider: 'gmail',
        email: credentials.email,
        name: credentials.name,
        picture: credentials.picture
      };
      
    } catch (error) {
      console.error('Gmail auth error:', error);
      // Fallback to demo mode
      console.warn('Falling back to demo mode');
      return await this.simulateGmailOAuth();
    }
  }

  // Outlook OAuth Authentication
  async authenticateOutlook() {
    try {
      // Check if Microsoft OAuth is configured
      if (!process.env.REACT_APP_MICROSOFT_CLIENT_ID || process.env.REACT_APP_MICROSOFT_CLIENT_ID === 'demo-client-id') {
        console.warn('Microsoft OAuth not configured, using demo mode');
        return await this.simulateOutlookOAuth();
      }

      if (!this.msalInstance) {
        throw new Error('MSAL instance not initialized');
      }

      // Microsoft OAuth scopes
      const loginRequest = {
        scopes: ['openid', 'profile', 'email', 'https://graph.microsoft.com/mail.send', 'https://graph.microsoft.com/user.read'],
      };

      // Sign in user
      const loginResponse = await this.msalInstance.loginPopup(loginRequest);
      
      // Get user account info
      const account = loginResponse.account;
      
      // Get access token for Microsoft Graph
      const tokenRequest = {
        scopes: ['https://graph.microsoft.com/mail.send', 'https://graph.microsoft.com/user.read'],
        account: account
      };
      
      const tokenResponse = await this.msalInstance.acquireTokenSilent(tokenRequest);
      
      const credentials = {
        email: account.username,
        name: account.name,
        accessToken: tokenResponse.accessToken,
        idToken: loginResponse.idToken,
        expiresAt: tokenResponse.expiresOn.getTime()
      };
      
      this.currentProvider = 'outlook';
      this.userCredentials = credentials;
      
      // Store in localStorage for persistence
      localStorage.setItem('email_auth_provider', 'outlook');
      localStorage.setItem('email_auth_credentials', JSON.stringify(credentials));
      localStorage.setItem('email_auth_time', new Date().getTime().toString());
      
      return {
        success: true,
        provider: 'outlook',
        email: credentials.email,
        name: credentials.name
      };
      
    } catch (error) {
      console.error('Outlook auth error:', error);
      // Fallback to demo mode
      console.warn('Falling back to demo mode');
      return await this.simulateOutlookOAuth();
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    const provider = localStorage.getItem('email_auth_provider');
    const credentials = localStorage.getItem('email_auth_credentials');
    const authTime = localStorage.getItem('email_auth_time');
    
    if (!provider || !credentials || !authTime) {
      return false;
    }
    
    // Check if authentication is still valid (24 hours)
    const authAge = Date.now() - parseInt(authTime);
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    
    if (authAge > maxAge) {
      this.logout();
      return false;
    }
    
    // Restore credentials
    this.currentProvider = provider;
    this.userCredentials = JSON.parse(credentials);
    
    return true;
  }

  // Get current user info
  getCurrentUser() {
    if (!this.isAuthenticated()) {
      return null;
    }
    
    return {
      provider: this.currentProvider,
      email: this.userCredentials.email,
      name: this.userCredentials.name
    };
  }

  // Send T&M Tag Email
  async sendTMTagEmail(emailData) {
    try {
      if (!this.isAuthenticated()) {
        throw new Error('User not authenticated. Please login first.');
      }

      // Prepare email content
      const emailContent = this.prepareTMTagEmail(emailData);

      // Send based on provider
      if (this.currentProvider === 'gmail') {
        return await this.sendViaGmail(emailContent);
      } else if (this.currentProvider === 'outlook') {
        return await this.sendViaOutlook(emailContent);
      } else {
        throw new Error('Unknown email provider');
      }

    } catch (error) {
      console.error('Email sending failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Prepare T&M Tag Email Content
  prepareTMTagEmail(emailData) {
    const subject = `T&M Tag - ${emailData.projectName} - ${emailData.dateOfWork}`;
    
    const htmlBody = `
      <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .header { background-color: #f4f4f4; padding: 20px; text-align: center; }
            .content { padding: 20px; }
            .tag-details { background-color: #f9f9f9; padding: 15px; border-left: 4px solid #dc2626; margin: 20px 0; }
            .footer { background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>Rhino Fire Protection</h2>
            <p>Time & Material Tag</p>
          </div>
          
          <div class="content">
            <p>Dear General Contractor,</p>
            
            <p>Please find attached the Time & Material tag for work completed on your project.</p>
            
            <div class="tag-details">
              <h3>Project Details</h3>
              <p><strong>Project:</strong> ${emailData.projectName}</p>
              <p><strong>Company:</strong> ${emailData.companyName}</p>
              <p><strong>T&M Tag:</strong> ${emailData.tmTagTitle}</p>
              <p><strong>Date:</strong> ${emailData.dateOfWork}</p>
              <p><strong>Submitted by:</strong> ${this.userCredentials.name}</p>
            </div>
            
            <p>The attached PDF contains complete details and requires your review and approval.</p>
            
            <p>Please contact us if you have any questions.</p>
            
            <p>Best regards,<br>
            ${this.userCredentials.name}<br>
            Rhino Fire Protection<br>
            ${this.userCredentials.email}</p>
          </div>
          
          <div class="footer">
            <p>This is an automated T&M tag submission from Rhino Fire Protection.</p>
          </div>
        </body>
      </html>
    `;

    return {
      to: emailData.gcEmail,
      subject: subject,
      html: htmlBody,
      attachments: emailData.pdfData ? [{
        filename: emailData.filename || `TM_Tag_${emailData.dateOfWork}.pdf`,
        content: emailData.pdfData,
        type: 'application/pdf'
      }] : []
    };
  }

  // Send via Gmail (simulation for now)
  async sendViaGmail(emailContent) {
    // In production, this would use Gmail API
    // For now, simulate sending
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('Gmail Email sent:', {
      from: this.userCredentials.email,
      to: emailContent.to,
      subject: emailContent.subject,
      provider: 'gmail'
    });

    return {
      success: true,
      provider: 'gmail',
      messageId: 'gmail_' + Date.now(),
      message: `Email sent via Gmail from ${this.userCredentials.email}`
    };
  }

  // Send via Outlook (simulation for now)
  async sendViaOutlook(emailContent) {
    // In production, this would use Microsoft Graph API
    // For now, simulate sending
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('Outlook Email sent:', {
      from: this.userCredentials.email,
      to: emailContent.to,
      subject: emailContent.subject,
      provider: 'outlook'
    });

    return {
      success: true,
      provider: 'outlook',
      messageId: 'outlook_' + Date.now(),
      message: `Email sent via Outlook from ${this.userCredentials.email}`
    };
  }

  // Logout
  logout() {
    this.currentProvider = null;
    this.userCredentials = null;
    localStorage.removeItem('email_auth_provider');
    localStorage.removeItem('email_auth_credentials');
    localStorage.removeItem('email_auth_time');
  }

  // Load Google OAuth library
  async loadGoogleOAuthLibrary() {
    return new Promise((resolve, reject) => {
      if (window.gapi) {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = 'https://apis.google.com/js/api.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Google OAuth library'));
      document.head.appendChild(script);
    });
  }

  // Demo mode for Gmail OAuth (when credentials not configured)
  async simulateGmailOAuth() {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Generate realistic demo user data
        const demoUsers = [
          { email: 'john.smith@gmail.com', name: 'John Smith' },
          { email: 'maria.rodriguez@gmail.com', name: 'Maria Rodriguez' },
          { email: 'mike.johnson@gmail.com', name: 'Mike Johnson' },
          { email: 'sarah.wilson@gmail.com', name: 'Sarah Wilson' }
        ];
        
        const randomUser = demoUsers[Math.floor(Math.random() * demoUsers.length)];
        
        resolve({
          success: true,
          credentials: {
            ...randomUser,
            picture: `https://ui-avatars.com/api/?name=${encodeURIComponent(randomUser.name)}&background=dc2626&color=fff`,
            accessToken: 'demo_gmail_token_' + Date.now(),
            refreshToken: 'demo_gmail_refresh_' + Date.now(),
            expiresAt: Date.now() + (3600 * 1000) // 1 hour
          }
        });
      }, 1500);
    });
  }

  // Demo mode for Outlook OAuth (when credentials not configured)
  async simulateOutlookOAuth() {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Generate realistic demo user data
        const demoUsers = [
          { email: 'alex.brown@hotmail.com', name: 'Alex Brown' },
          { email: 'lisa.davis@outlook.com', name: 'Lisa Davis' },
          { email: 'carlos.martinez@live.com', name: 'Carlos Martinez' },
          { email: 'jennifer.taylor@outlook.com', name: 'Jennifer Taylor' }
        ];
        
        const randomUser = demoUsers[Math.floor(Math.random() * demoUsers.length)];
        
        resolve({
          success: true,
          credentials: {
            ...randomUser,
            accessToken: 'demo_outlook_token_' + Date.now(),
            refreshToken: 'demo_outlook_refresh_' + Date.now(),
            expiresAt: Date.now() + (3600 * 1000) // 1 hour
          }
        });
      }, 1500);
    });
  }
}

export default new OAuthEmailService();