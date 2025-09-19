import React, { useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Key, Shield, Building } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const GcOnlyLogin = ({ onLoginSuccess }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
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
    if (formData.pin.length !== 4) {
      toast({
        title: "Invalid PIN",
        description: "Please enter a 4-digit PIN",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      // Find project by PIN first
      const projectsResponse = await fetch(`${backendUrl}/api/projects`);
      if (!projectsResponse.ok) {
        throw new Error("Unable to connect to server");
      }
      
      const projects = await projectsResponse.json();
      const matchingProject = projects.find(p => p.gc_pin === formData.pin && !p.gc_pin_used);
      
      if (!matchingProject) {
        toast({
          title: "Invalid PIN",
          description: "PIN not found or already used",
          variant: "destructive"
        });
        return;
      }

      // Now login with the found project
      const response = await fetch(`${backendUrl}/api/gc/login-simple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectId: matchingProject.id,
          pin: formData.pin,
          ip: window.location.hostname,
          userAgent: navigator.userAgent
        })
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Login Successful",
          description: `Welcome to ${data.projectName} project dashboard`,
        });
        
        onLoginSuccess({
          projectId: matchingProject.id,
          keyId: null,
          adminAccess: false
        });
      } else {
        const error = await response.json();
        toast({
          title: "Login Failed",
          description: error.detail || "Invalid credentials",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('GC Login error:', error);
      toast({
        title: "Connection Error",
        description: "Unable to connect to server. Please try again.",
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
    <div className={`min-h-screen flex items-center justify-center px-4 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      <div className={`w-full max-w-md space-y-8 backdrop-blur-md border-0 shadow-xl rounded-lg p-8 ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
              alt="Rhino Fire Protection" 
              className="h-16 w-auto"
            />
          </div>
          <div>
            <h2 className={`text-2xl font-bold ${themeClasses.text.primary}`}>
              General Contractor Access
            </h2>
            <p className={`mt-2 text-sm ${themeClasses.text.secondary}`}>
              Enter your project credentials to view the dashboard
            </p>
          </div>
        </div>

        {/* Login Form */}
        <div className="space-y-6">
          <div className="space-y-4">
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
            disabled={isLoading || formData.pin.length !== 4}
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

          <div className={`p-4 rounded-lg border text-center ${
            isDarkMode 
              ? 'bg-blue-900/20 border-blue-500/30 text-blue-200' 
              : 'bg-blue-50 border-blue-200 text-blue-800'
          }`}>
            <div className="flex items-center justify-center gap-2 mb-2">
              <Shield className="w-4 h-4" />
              <span className="font-medium text-sm">Secure Access</span>
            </div>
            <p className="text-xs leading-relaxed">
              This dashboard provides project progress information for authorized contractors only.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GcOnlyLogin;