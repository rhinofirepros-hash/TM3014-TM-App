import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Mail, LogOut, CheckCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';
import oauthEmailService from '../services/oauthEmailService';

const EmailAuthModal = ({ open, onClose, onAuthSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [authProvider, setAuthProvider] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const { toast } = useToast();
  const { isDarkMode } = useTheme();

  useEffect(() => {
    // Check if user is already authenticated
    if (oauthEmailService.isAuthenticated()) {
      const user = oauthEmailService.getCurrentUser();
      setCurrentUser(user);
      setAuthProvider(user.provider);
    }
  }, [open]);

  const handleGmailAuth = async () => {
    setIsLoading(true);
    setAuthProvider('gmail');

    try {
      const result = await oauthEmailService.authenticateGmail();
      
      if (result.success) {
        setCurrentUser({
          provider: 'gmail',
          email: result.email,
          name: result.name
        });
        
        toast({
          title: "Gmail Connected",
          description: `Successfully connected to ${result.email}`,
        });

        if (onAuthSuccess) {
          onAuthSuccess(result);
        }
      } else {
        throw new Error(result.error || 'Gmail authentication failed');
      }
    } catch (error) {
      console.error('Gmail auth error:', error);
      toast({
        title: "Gmail Authentication Failed",
        description: error.message,
        variant: "destructive"
      });
      setAuthProvider(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOutlookAuth = async () => {
    setIsLoading(true);
    setAuthProvider('outlook');

    try {
      const result = await oauthEmailService.authenticateOutlook();
      
      if (result.success) {
        setCurrentUser({
          provider: 'outlook',
          email: result.email,
          name: result.name
        });
        
        toast({
          title: "Outlook Connected",
          description: `Successfully connected to ${result.email}`,
        });

        if (onAuthSuccess) {
          onAuthSuccess(result);
        }
      } else {
        throw new Error(result.error || 'Outlook authentication failed');
      }
    } catch (error) {
      console.error('Outlook auth error:', error);
      toast({
        title: "Outlook Authentication Failed",
        description: error.message,
        variant: "destructive"
      });
      setAuthProvider(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    oauthEmailService.logout();
    setCurrentUser(null);
    setAuthProvider(null);
    
    toast({
      title: "Logged Out",
      description: "Email account disconnected successfully",
    });
  };

  const handleClose = () => {
    if (currentUser && onAuthSuccess) {
      onAuthSuccess(currentUser);
    }
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-[425px] ${
        isDarkMode 
          ? 'bg-slate-900/95 backdrop-blur-xl border-white/20 shadow-2xl text-white' 
          : 'bg-white/95 backdrop-blur-xl border-gray-200/50 shadow-2xl text-gray-900'
      }`}>
        <DialogHeader>
          <DialogTitle className={`text-xl font-bold flex items-center gap-2 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            <Mail className="w-6 h-6 text-red-600" />
            Email Authentication
          </DialogTitle>
        </DialogHeader>

        <div className="py-6">
          {currentUser ? (
            // Already authenticated
            <div className="space-y-4">
              <div className={`flex items-center justify-center p-4 rounded-lg border ${
                isDarkMode 
                  ? 'bg-green-900/30 border-green-500/30' 
                  : 'bg-green-50 border-green-200'
              }`}>
                <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
                <div className="text-center">
                  <p className={`font-medium ${isDarkMode ? 'text-green-400' : 'text-green-800'}`}>Connected Successfully!</p>
                  <p className={`text-sm ${isDarkMode ? 'text-green-300' : 'text-green-600'}`}>{currentUser.email}</p>
                </div>
              </div>

              <div className="flex items-center justify-center gap-2">
                <Badge variant="secondary" className={`capitalize ${
                  isDarkMode 
                    ? 'bg-white/20 text-white border-white/30' 
                    : 'bg-gray-100 text-gray-800 border-gray-200'
                }`}>
                  {currentUser.provider}
                </Badge>
                <Badge variant="outline" className={
                  isDarkMode 
                    ? 'border-white/30 text-white' 
                    : 'border-gray-300 text-gray-700'
                }>
                  {currentUser.name}
                </Badge>
              </div>

              <p className={`text-sm text-center ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                You can now send T&M tag emails directly from your {currentUser.provider} account.
              </p>

              <div className="flex gap-2">
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  className={`flex-1 ${
                    isDarkMode 
                      ? 'border-white/30 text-white hover:bg-white/10' 
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                  disabled={isLoading}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Disconnect
                </Button>
                <Button
                  onClick={handleClose}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  Continue
                </Button>
              </div>
            </div>
          ) : (
            // Not authenticated
            <div className="space-y-4">
              <div className="text-center mb-6">
                <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Connect your email account to send T&M tags directly to General Contractors
                </p>
                {(!process.env.REACT_APP_GOOGLE_CLIENT_ID && !process.env.REACT_APP_MICROSOFT_CLIENT_ID) && (
                  <p className={`text-xs mt-2 p-2 rounded ${
                    isDarkMode 
                      ? 'text-yellow-300 bg-yellow-900/30' 
                      : 'text-yellow-600 bg-yellow-50'
                  }`}>
                    Demo Mode: Real OAuth credentials not configured
                  </p>
                )}
              </div>

              <div className="space-y-3">
                <Button 
                  onClick={handleGmailAuth}
                  disabled={isLoading}
                  variant="outline"
                  className={`w-full flex items-center justify-center gap-3 h-12 ${
                    isDarkMode 
                      ? 'border-white/30 text-white hover:border-red-400 hover:bg-red-900/20' 
                      : 'border-gray-300 hover:border-red-400 hover:bg-red-50 text-gray-700'
                  }`}
                >
                  {isLoading && authProvider === 'gmail' ? (
                    <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Mail className="w-5 h-5 text-red-600" />
                  )}
                  <span>
                    {isLoading && authProvider === 'gmail' ? 'Connecting...' : 'Connect Gmail'}
                  </span>
                </Button>
                
                <Button 
                  onClick={handleOutlookAuth}
                  disabled={isLoading}
                  variant="outline"
                  className={`w-full flex items-center justify-center gap-3 h-12 ${
                    isDarkMode 
                      ? 'border-white/30 text-white hover:border-blue-400 hover:bg-blue-900/20' 
                      : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50 text-gray-700'
                  }`}
                >
                  {isLoading && authProvider === 'outlook' ? (
                    <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Mail className="w-5 h-5 text-blue-600" />
                  )}
                  <span>
                    {isLoading && authProvider === 'outlook' ? 'Connecting...' : 'Connect Outlook'}
                  </span>
                </Button>
              </div>

              <div className="text-center">
                <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  Emails will be sent from your personal account
                </p>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="border-t pt-4">
          <div className="text-xs text-gray-500 text-center w-full">
            Your email credentials are stored securely and used only for sending T&M tags
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EmailAuthModal;