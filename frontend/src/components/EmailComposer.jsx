import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Mail, Send, FileText, User, Calendar, Clock, DollarSign } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import emailService from '../services/emailService';
import oauthEmailService from '../services/oauthEmailService';
import EmailAuthModal from './EmailAuthModal';

const EmailComposer = ({ isOpen, onClose, formData, pdfData }) => {
  const [emailData, setEmailData] = useState({
    to: '',
    cc: '',
    subject: '',
    message: '',
    template: 'professional'
  });
  const [isSending, setIsSending] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authenticatedUser, setAuthenticatedUser] = useState(null);
  const [userEmail, setUserEmail] = useState('');
  const [userName, setUserName] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    // Get user email from login method
    const loginMethod = localStorage.getItem('tm_app_login_method');
    const storedEmail = localStorage.getItem('tm_app_user_email');
    const storedName = localStorage.getItem('tm_app_user_name');
    
    if (loginMethod === 'gmail' || loginMethod === 'outlook') {
      setUserEmail(storedEmail || '');
      setUserName(storedName || 'Jesus Garcia');
    } else {
      setUserEmail('jesus.garcia@rhinofire.com');
      setUserName('Jesus Garcia');
    }

    // Pre-fill email data
    if (formData) {
      setEmailData(prev => ({
        ...prev,
        to: formData.gcEmail || '',
        subject: generateSubject(),
        message: generateMessage()
      }));
    }
  }, [formData]);

  const generateSubject = () => {
    const date = formData?.dateOfWork ? 
      new Date(formData.dateOfWork).toLocaleDateString() : 
      new Date().toLocaleDateString();
    
    return `T&M Tag - ${formData?.projectName || 'Project'} - ${date}`;
  };

  const generateMessage = () => {
    const templates = {
      professional: `Dear General Contractor,

Please find attached the Time & Material tag for today's work on the ${formData?.projectName || 'project'}.

Project Details:
• Project: ${formData?.projectName || 'N/A'}
• Cost Code: ${formData?.costCode || 'N/A'}
• Date of Work: ${formData?.dateOfWork ? new Date(formData.dateOfWork).toLocaleDateString() : 'N/A'}
• Work Description: ${formData?.tmTagTitle || 'N/A'}

Labor Summary:
• Total Hours: ${formData?.laborEntries?.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0) || 0} hours
• Workers: ${formData?.laborEntries?.length || 0}

${formData?.descriptionOfWork ? `Work Performed:\n${formData.descriptionOfWork}\n\n` : ''}Please review and approve at your earliest convenience. If you have any questions or concerns, please don't hesitate to contact me.

Best regards,
${userName}
Rhino Fire Protection
${userEmail}
Phone: (555) 123-4567`,

      brief: `Hi,

Attached is the T&M tag for ${formData?.projectName || 'project'} - ${formData?.dateOfWork ? new Date(formData.dateOfWork).toLocaleDateString() : new Date().toLocaleDateString()}.

Total Hours: ${formData?.laborEntries?.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0) || 0}
Workers: ${formData?.laborEntries?.length || 0}

${formData?.tmTagTitle || 'Work completed as scheduled.'}

Please review and let me know if you need anything else.

Thanks,
${userName}
Rhino Fire Protection`,

      detailed: `Dear Project Manager,

I hope this email finds you well. Attached please find the completed Time & Material documentation for today's work on ${formData?.projectName || 'the project'}.

PROJECT INFORMATION:
━━━━━━━━━━━━━━━━━━━━
• Project Name: ${formData?.projectName || 'N/A'}
• Cost Code: ${formData?.costCode || 'N/A'}
• Date of Work: ${formData?.dateOfWork ? new Date(formData.dateOfWork).toLocaleDateString() : 'N/A'}
• Foreman: ${userName}

WORK SUMMARY:
━━━━━━━━━━━━━━━
• Description: ${formData?.tmTagTitle || 'N/A'}
• Total Labor Hours: ${formData?.laborEntries?.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0) || 0}
• Number of Workers: ${formData?.laborEntries?.length || 0}
• Materials Used: ${formData?.materialEntries?.length || 0} items

${formData?.descriptionOfWork ? `DETAILED WORK DESCRIPTION:\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n${formData.descriptionOfWork}\n\n` : ''}All work has been completed according to specifications and safety standards. The attached PDF contains complete details including worker hours, materials used, and required signatures.

Please review the attached documentation and let me know if you need any clarification or have questions about the work performed.

Thank you for your continued partnership.

Best regards,

${userName}
Foreman
Rhino Fire Protection
Email: ${userEmail}
Phone: (555) 123-4567
www.rhinofireprotection.com`
    };

    return templates[emailData.template] || templates.professional;
  };

  const emailTemplates = [
    { value: 'professional', label: 'Professional', icon: '💼' },
    { value: 'brief', label: 'Brief & Direct', icon: '⚡' },
    { value: 'detailed', label: 'Detailed Report', icon: '📋' }
  ];

  const handleTemplateChange = (template) => {
    setEmailData(prev => ({
      ...prev,
      template,
      message: generateMessage()
    }));
  };

  const handleSendEmail = async () => {
    if (!emailData.to) {
      toast({
        title: "Email Required",
        description: "Please enter the recipient's email address.",
        variant: "destructive"
      });
      return;
    }

    setIsSending(true);

    try {
      // Initialize EmailJS service
      await emailService.initialize();

      // Prepare email data for the service
      const emailPayload = {
        gcEmail: emailData.to,
        ccEmail: emailData.cc,
        projectName: formData?.projectName,
        tmTagTitle: formData?.tmTagTitle,
        dateOfWork: formData?.dateOfWork ? new Date(formData.dateOfWork).toLocaleDateString() : new Date().toLocaleDateString(),
        message: emailData.message,
        pdfData: pdfData, // Base64 PDF data
        filename: `TM_Tag_${formData?.dateOfWork ? new Date(formData.dateOfWork).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]}.pdf`
      };

      // Send email using the EmailJS service
      const result = await emailService.sendTMTagEmail(emailPayload);

      if (result.success) {
        toast({
          title: "Email Sent Successfully",
          description: `T&M tag sent to ${emailData.to}`,
        });

        // Log email for reports
        const emailLog = {
          id: Date.now(),
          to: emailData.to,
          cc: emailData.cc,
          subject: emailData.subject,
          sentAt: new Date().toISOString(),
          project: formData?.projectName,
          template: emailData.template,
          messageId: result.messageId
        };
        
        const existingLogs = JSON.parse(localStorage.getItem('email_logs') || '[]');
        existingLogs.unshift(emailLog);
        localStorage.setItem('email_logs', JSON.stringify(existingLogs));
        
        onClose();
      } else {
        throw new Error(result.error || 'Failed to send email');
      }
    } catch (error) {
      console.error('Email sending error:', error);
      toast({
        title: "Email Failed",
        description: error.message || "Failed to send email. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5 text-blue-600" />
            Send T&M Tag to General Contractor
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Email Form */}
          <div className="lg:col-span-2 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="to">To (GC Email)*</Label>
                <Input
                  id="to"
                  type="email"
                  value={emailData.to}
                  onChange={(e) => setEmailData(prev => ({ ...prev, to: e.target.value }))}
                  placeholder="gc@contractor.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cc">CC (Optional)</Label>
                <Input
                  id="cc"
                  type="email"
                  value={emailData.cc}
                  onChange={(e) => setEmailData(prev => ({ ...prev, cc: e.target.value }))}
                  placeholder="manager@company.com"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <Input
                id="subject"
                value={emailData.subject}
                onChange={(e) => setEmailData(prev => ({ ...prev, subject: e.target.value }))}
                placeholder="T&M Tag - Project Name - Date"
              />
            </div>

            <div className="space-y-2">
              <Label>Email Template</Label>
              <Select value={emailData.template} onValueChange={handleTemplateChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {emailTemplates.map((template) => (
                    <SelectItem key={template.value} value={template.value}>
                      <span className="flex items-center gap-2">
                        <span>{template.icon}</span>
                        {template.label}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">Message</Label>
              <Textarea
                id="message"
                value={emailData.message}
                onChange={(e) => setEmailData(prev => ({ ...prev, message: e.target.value }))}
                rows={12}
                className="font-mono text-sm"
              />
            </div>
          </div>

          {/* Summary Panel */}
          <div className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  T&M Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">Project:</span>
                  <span className="font-medium">{formData?.projectName}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">Date:</span>
                  <span className="font-medium">
                    {formData?.dateOfWork ? new Date(formData.dateOfWork).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">Hours:</span>
                  <span className="font-medium">
                    {formData?.laborEntries?.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0) || 0}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">Labor Cost:</span>
                  <span className="font-medium">
                    ${((formData?.laborEntries?.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0) || 0) * 95).toLocaleString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Email Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">From:</span>
                  <span className="font-medium">{userEmail}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Method:</span>
                  <span className="font-medium capitalize">
                    {localStorage.getItem('tm_app_login_method') || 'PIN'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">PDF:</span>
                  <span className="font-medium text-green-600">✓ Attached</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSendEmail}
            disabled={isSending || !emailData.to}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Send className="w-4 h-4 mr-2" />
            {isSending ? 'Sending...' : 'Send Email'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EmailComposer;