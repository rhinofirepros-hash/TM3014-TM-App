import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Shield, Building2, Key, Sun, Moon } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const PinLogin = ({ onLogin, onGcLogin }) => {
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { isDarkMode, toggleTheme, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Admin PINs
      const adminPins = ['J777', 'A123', 'ADMIN', '1234'];
      
      console.log('Checking PIN:', pin.toUpperCase(), 'against admin PINs:', adminPins);
      if (adminPins.includes(pin.toUpperCase())) {
        console.log('PIN matched! Setting localStorage and calling onLogin');
        localStorage.setItem('isAuthenticated', 'true');
        alert('PIN authenticated! Calling onLogin...');
        // Force immediate navigation
        setTimeout(() => {
          console.log('Timeout reached, calling onLogin()');
          onLogin();
        }, 100);
      } else {
        setError('Invalid PIN. Please try again.');
      }
    } catch (err) {
      setError('Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGcAccess = () => {
    // Navigate to GC login page
    window.location.hash = 'gc-login';
    if (onGcLogin) {
      onGcLogin();
    }
  };

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 ${themeClasses.background}`}>
      {/* Theme Toggle - Fixed Position */}
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleTheme}
        className="fixed top-4 right-4 z-10"
      >
        {isDarkMode ? <Sun className="w-5 h-5" style={{ color: '#FEF08A' }} /> : <Moon className="w-5 h-5" style={{ color: '#1E293B' }} />}
      </Button>

      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
              alt="Rhino Fire Protection" 
              className="h-12 w-auto"
            />
          </div>
          <h1 className={`text-3xl font-bold ${themeClasses.text.primary} mb-2`}>
            Welcome to Rhino
          </h1>
          <p className={`${themeClasses.text.secondary}`}>
            Time & Material Daily Tag System
          </p>
        </div>

        {/* Admin Login Card */}
        <Card className={`${themeClasses.card} rounded-lg`}>
          <CardHeader className="text-center">
            <div className={`w-12 h-12 mx-auto mb-4 rounded-lg flex items-center justify-center`}
                 style={{ backgroundColor: `${themeClasses.colors.blue}40`, color: themeClasses.colors.blue }}>
              <Shield className="w-6 h-6" />
            </div>
            <CardTitle className={themeClasses.text.primary}>Admin Access</CardTitle>
            <p className={`text-sm ${themeClasses.text.secondary}`}>
              Enter your admin PIN to access the system
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Input
                  type="password"
                  placeholder="Enter Admin PIN"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  className={`text-center text-lg font-mono ${themeClasses.input.primary}`}
                  required
                />
              </div>
              
              {error && (
                <div className={`text-sm text-center p-3 rounded-lg`}
                     style={{ backgroundColor: `${themeClasses.colors.red}20`, color: themeClasses.colors.red }}>
                  {error}
                </div>
              )}
              
              <Button 
                type="submit" 
                className="w-full text-lg py-3"
                disabled={isLoading || !pin}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Authenticating...
                  </div>
                ) : (
                  <>
                    <Key className="w-5 h-5 mr-2" />
                    Access with PIN
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* GC Access Card */}
        <Card className={`${themeClasses.card} rounded-lg`}>
          <CardHeader className="text-center">
            <div className={`w-12 h-12 mx-auto mb-4 rounded-lg flex items-center justify-center`}
                 style={{ backgroundColor: `${themeClasses.colors.green}40`, color: themeClasses.colors.green }}>
              <Building2 className="w-6 h-6" />
            </div>
            <CardTitle className={themeClasses.text.primary}>General Contractor</CardTitle>
            <p className={`text-sm ${themeClasses.text.secondary}`}>
              Access project updates and T&M submissions
            </p>
          </CardHeader>
          <CardContent>
            <Button 
              variant="secondary"
              className="w-full text-lg py-3"
              onClick={handleGcAccess}
            >
              <Building2 className="w-5 h-5 mr-2" />
              GC Portal Access
            </Button>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center pt-6">
          <p className={`text-xs ${themeClasses.text.muted}`}>
            Rhino Fire Protection © 2024 • TM3014 System
          </p>
        </div>
      </div>
    </div>
  );
};

export default PinLogin;