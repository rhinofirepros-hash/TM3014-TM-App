import emailjs from '@emailjs/browser';

class EmailService {
  constructor() {
    this.publicKey = process.env.REACT_APP_EMAILJS_PUBLIC_KEY;
    this.serviceId = process.env.REACT_APP_EMAILJS_SERVICE_ID;
    this.templateId = process.env.REACT_APP_EMAILJS_TEMPLATE_ID;
    this.isInitialized = false;
  }

  async initialize() {
    if (!this.publicKey || !this.serviceId || !this.templateId) {
      console.warn('EmailJS not configured - using mock email service');
      return false;
    }

    try {
      emailjs.init(this.publicKey);
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize EmailJS:', error);
      return false;
    }
  }

  async sendTMTagEmail(emailData) {
    try {
      // If EmailJS is not configured, use mock implementation
      if (!this.isInitialized) {
        return this.mockSendEmail(emailData);
      }

      const templateParams = {
        to_email: emailData.gcEmail,
        project_name: emailData.projectName,
        tm_tag_title: emailData.tmTagTitle,
        date_of_work: emailData.dateOfWork,
        foreman_name: "Jesus Garcia",
        message: emailData.message || this.generateDefaultMessage(emailData),
        company_name: "Rhino Fire Protection",
        attachment: emailData.pdfData, // Base64 PDF data
        filename: emailData.filename || `TM_Tag_${emailData.dateOfWork}.pdf`
      };

      const response = await emailjs.send(
        this.serviceId,
        this.templateId,
        templateParams
      );

      return {
        success: true,
        message: 'Email sent successfully',
        messageId: response.text
      };

    } catch (error) {
      console.error('Email sending failed:', error);
      return {
        success: false,
        error: error.message || 'Failed to send email'
      };
    }
  }

  mockSendEmail(emailData) {
    // Mock implementation for when EmailJS is not configured
    console.log('Mock Email Service - Email would be sent with:', {
      to: emailData.gcEmail,
      subject: `T&M Tag for ${emailData.projectName} - ${emailData.dateOfWork}`,
      project: emailData.projectName,
      title: emailData.tmTagTitle,
      attachment: emailData.filename
    });

    // Simulate email sending delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          message: 'Email sent successfully (mock)',
          messageId: 'mock_' + Date.now()
        });
      }, 1500);
    });
  }

  generateDefaultMessage(emailData) {
    return `Dear General Contractor,

Please find attached the Time & Material tag for the following project:

Project: ${emailData.projectName}
T&M Tag: ${emailData.tmTagTitle}
Date of Work: ${emailData.dateOfWork}
Foreman: Jesus Garcia

This T&M tag has been completed and is ready for your review and approval.

Please review the attached PDF and let us know if you have any questions or need additional information.

Best regards,
Rhino Fire Protection
Email: info@rhinofireprotection.com
Phone: (555) 123-4567`;
  }
}

export default new EmailService();