import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { Mail, Shield } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';

const PinLogin = ({ onLoginSuccess }) => {
  const [pin, setPin] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loginMethod, setLoginMethod] = useState('pin'); // 'pin', 'gmail', 'outlook'
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  const handlePinLogin = async () => {
    setIsLoading(true);
    
    try {
      // Accept both admin PINs and any valid GC PINs for testing
      const validAdminPins = ['J777', '2602', '2568', '6614', '4313', '7503'];
      
      if (validAdminPins.includes(pin)) {
        // Admin PIN - regular admin login
        setTimeout(() => {
          localStorage.setItem('tm_app_authenticated', 'true');
          localStorage.setItem('tm_app_login_time', new Date().getTime().toString());
          localStorage.setItem('tm_app_login_method', 'pin');
          onLoginSuccess();
          toast({
            title: "Admin Login Successful",
            description: "Welcome to Rhino Fire Protection T&M App",
          });
          setIsLoading(false);
        }, 1000);
      } else if (pin.length === 4 && /^\d{4}$/.test(pin)) {
        // 4-digit PIN - try GC login
        console.log('Attempting GC login with 4-digit PIN:', pin);
        
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        
        // Find project by PIN - much simpler approach
        const projectsResponse = await fetch(`${backendUrl}/api/projects`);
        
        if (projectsResponse.ok) {
          const projects = await projectsResponse.json();
          const matchingProject = projects.find(p => p.gc_pin === pin && !p.gc_pin_used);
          
          if (matchingProject) {
            // Found matching project, attempt GC login
            const gcLoginResponse = await fetch(`${backendUrl}/api/gc/login-simple`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                projectId: matchingProject.id,
                pin: pin,
                ip: 'admin-unified-login'
              })
            });
            
            if (gcLoginResponse.ok) {
              const gcResult = await gcLoginResponse.json();
              
              toast({
                title: "GC Login Successful", 
                description: `Welcome to ${matchingProject.name} project dashboard`,
              });
              
              // Redirect to GC dashboard
              window.location.href = `/gc-portal/${matchingProject.id}`;
              return;
              
            } else {
              const error = await gcLoginResponse.json();
              throw new Error(error.detail || 'GC login failed');
            }
          } else {
            throw new Error('PIN not found or already used');
          }
        } else {
          throw new Error('Unable to verify PIN - server error');
        }
      } else {
        throw new Error('Invalid PIN format');
      }
      
    } catch (error) {
      console.error('Login error:', error);
      toast({
        title: "Login Failed",
        description: error.message || "Please check your PIN and try again.",
        variant: "destructive"
      });
      setIsLoading(false);
    }
  };

  // Simplified direct login - no OAuth needed

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handlePinLogin();
    }
  };

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      <Card className={`w-full max-w-md shadow-xl ${
        isDarkMode 
          ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
          : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
      }`}>
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-24 h-20 flex items-center justify-center overflow-hidden">
            <img 
              src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
              alt="Rhino Fire Protection" 
              className="w-24 h-20 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <span className="text-red-500 font-bold text-xl hidden">RF</span>
          </div>
          <CardTitle className={`text-2xl font-bold ${themeClasses.text.primary}`}>
            Rhino Fire Protection
          </CardTitle>
          <p className={themeClasses.text.secondary}>T&M Daily Tag Application</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Direct Login Instructions */}
          <div className="text-center mb-6">
            <p className={`text-sm ${themeClasses.text.secondary}`}>Enter your PIN to access the T&M Tag system</p>
          </div>

          {/* PIN Login */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="pin" className={`text-sm font-medium ${themeClasses.text.primary} flex items-center gap-2`}>
                <Shield className="w-4 h-4" />
                Enter PIN Code
              </Label>
              <Input
                id="pin"
                type="password"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your PIN"
                className={`text-center text-lg tracking-widest ${themeClasses.input}`}
                maxLength={4}
                disabled={isLoading}
              />
            </div>
            
            <div className={`text-xs text-center ${themeClasses.text.secondary}`}>
              <p>Enter your access PIN to continue</p>
            </div>
            
            <Button 
              onClick={handlePinLogin}
              disabled={!pin || isLoading}
              className={`w-full ${themeClasses.button.primary}`}
            >
              {isLoading && loginMethod === 'pin' ? 'Verifying...' : 'Access with PIN'}
            </Button>
          </div>
          
          <div className={`text-center text-xs ${themeClasses.text.secondary}`}>
            Contact supervisor if you need access
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PinLogin;