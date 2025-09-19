import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Shield, Building, Key, AlertCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';

const GcLogin = ({ onLoginSuccess }) => {
  const { toast } = useToast();
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  const [formData, setFormData] = useState({
    projectId: '',
    pin: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLogin = async () => {
    if (!formData.projectId || !formData.pin) {
      toast({
        title: "Missing Information",
        description: "Please enter both Project ID and PIN",
        variant: "destructive"
      });
      return;
    }

    if (formData.pin.length !== 4) {
      toast({
        title: "Invalid PIN",
        description: "PIN must be 4 digits",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/gc/login-simple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectId: formData.projectId,
          pin: formData.pin,
          ip: 'web-client',
          userAgent: navigator.userAgent
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        toast({
          title: "Access Granted",
          description: `Loading project dashboard... New PIN: ${result.newPin}`,
        });

        // Call parent callback with login success
        if (onLoginSuccess) {
          onLoginSuccess({
            projectId: result.projectId,
            projectName: result.projectName,
            newPin: result.newPin
          });
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }
      
    } catch (error) {
      console.error('GC Login error:', error);
      toast({
        title: "Access Denied",
        description: error.message || "Invalid project ID or PIN",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{
      background: isDarkMode 
        ? 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
        : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)'
    }}>
      <div className="w-full max-w-md">
        <Card className={`${themeClasses.card.primary} shadow-2xl border-0`}>
          <CardHeader className="text-center pb-8">
            <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <CardTitle className={`text-2xl font-bold ${themeClasses.text.primary}`}>
              General Contractor Access
            </CardTitle>
            <p className={`text-sm ${themeClasses.text.secondary} mt-2`}>
              Enter your project ID and 4-digit PIN to view project progress
            </p>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className={`text-sm font-medium ${themeClasses.text.primary}`}>
                  <Building className="w-4 h-4 inline mr-2" />
                  Project ID
                </Label>
                <Input
                  type="text"
                  placeholder="Enter project ID"
                  value={formData.projectId}
                  onChange={(e) => handleInputChange('projectId', e.target.value)}
                  onKeyPress={handleKeyPress}
                  className={`${themeClasses.input.primary} h-12`}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={`text-sm font-medium ${themeClasses.text.primary}`}>
                  <Key className="w-4 h-4 inline mr-2" />
                  4-Digit PIN
                </Label>
                <Input
                  type="text"
                  placeholder="0000"
                  maxLength={4}
                  value={formData.pin}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, ''); // Only digits
                    handleInputChange('pin', value);
                  }}
                  onKeyPress={handleKeyPress}
                  className={`${themeClasses.input.primary} h-12 text-center text-lg tracking-widest`}
                />
              </div>
            </div>

            <Button
              onClick={handleLogin}
              disabled={isLoading || !formData.projectId || formData.key.length !== 4}
              className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-medium"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Verifying Access...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4 mr-2" />
                  View Dashboard
                </>
              )}
            </Button>

            <div className={`p-4 rounded-lg border ${
              isDarkMode 
                ? 'bg-blue-900/20 border-blue-500/30 text-blue-200' 
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}>
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-medium mb-1">Secure Access</p>
                  <p>
                    Access keys are single-use and expire after use. 
                    Contact your project manager if you need a new key.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center mt-8">
          <p className={`text-sm ${themeClasses.text.secondary}`}>
            Powered by <span className="font-semibold text-blue-600">Rhino Fire Protection</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default GcLogin;