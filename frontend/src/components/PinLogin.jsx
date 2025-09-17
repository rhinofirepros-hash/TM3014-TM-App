import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { Mail, Shield } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const PinLogin = ({ onLoginSuccess }) => {
  const [pin, setPin] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loginMethod, setLoginMethod] = useState('pin'); // 'pin', 'gmail', 'outlook'
  const { toast } = useToast();

  const handlePinLogin = () => {
    setIsLoading(true);
    
    // Simple PIN validation
    setTimeout(() => {
      if (pin === 'J777') {
        localStorage.setItem('tm_app_authenticated', 'true');
        localStorage.setItem('tm_app_login_time', new Date().getTime().toString());
        localStorage.setItem('tm_app_login_method', 'pin');
        onLoginSuccess();
        toast({
          title: "Login Successful",
          description: "Welcome to Rhino Fire Protection T&M App",
        });
      } else {
        toast({
          title: "Invalid PIN",
          description: "Please check your PIN and try again.",
          variant: "destructive"
        });
      }
      setIsLoading(false);
    }, 1000);
  };

  const handleGmailLogin = () => {
    setIsLoading(true);
    
    // Simulate Gmail OAuth (in production, use Google OAuth)
    setTimeout(() => {
      // For demo purposes, simulate successful Gmail login
      localStorage.setItem('tm_app_authenticated', 'true');
      localStorage.setItem('tm_app_login_time', new Date().getTime().toString());
      localStorage.setItem('tm_app_login_method', 'gmail');
      localStorage.setItem('tm_app_user_email', 'user@gmail.com');
      localStorage.setItem('tm_app_user_name', 'Jesus Garcia');
      
      onLoginSuccess();
      toast({
        title: "Gmail Login Successful",
        description: "Connected with Gmail account",
      });
      setIsLoading(false);
    }, 2000);
  };

  const handleOutlookLogin = () => {
    setIsLoading(true);
    
    // Simulate Outlook OAuth (in production, use Microsoft Graph)
    setTimeout(() => {
      // For demo purposes, simulate successful Outlook login
      localStorage.setItem('tm_app_authenticated', 'true');
      localStorage.setItem('tm_app_login_time', new Date().getTime().toString());
      localStorage.setItem('tm_app_login_method', 'outlook');
      localStorage.setItem('tm_app_user_email', 'user@outlook.com');
      localStorage.setItem('tm_app_user_name', 'Jesus Garcia');
      
      onLoginSuccess();
      toast({
        title: "Outlook Login Successful",
        description: "Connected with Outlook account",
      });
      setIsLoading(false);
    }, 2000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handlePinLogin();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-24 h-20 flex items-center justify-center overflow-hidden">
            <img 
              src="https://customer-assets.emergentagent.com/job_b98f6205-b977-4a20-97e0-9a9b9eeea432/artifacts/yzknuiqy_TITLEBLOCKRHINOFIRE1.png" 
              alt="Rhino Fire Protection" 
              className="w-24 h-20 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <span className="text-red-500 font-bold text-xl hidden">RF</span>
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Rhino Fire Protection
          </CardTitle>
          <p className="text-gray-600">T&M Daily Tag Application</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* OAuth Login Options */}
          <div className="space-y-3">
            <div className="text-center text-sm font-medium text-gray-700 mb-4">
              Choose your login method
            </div>
            
            <Button 
              onClick={handleGmailLogin}
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center gap-2"
              variant={loginMethod === 'gmail' ? 'default' : 'outline'}
            >
              <Mail className="w-4 h-4" />
              {isLoading && loginMethod === 'gmail' ? 'Connecting...' : 'Login with Gmail'}
            </Button>
            
            <Button 
              onClick={handleOutlookLogin}
              disabled={isLoading}
              className="w-full bg-blue-800 hover:bg-blue-900 text-white flex items-center justify-center gap-2"
              variant={loginMethod === 'outlook' ? 'default' : 'outline'}
            >
              <Mail className="w-4 h-4" />
              {isLoading && loginMethod === 'outlook' ? 'Connecting...' : 'Login with Outlook'}
            </Button>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <Separator className="w-full" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">Or use PIN</span>
            </div>
          </div>

          {/* PIN Login */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="pin" className="text-sm font-medium text-gray-700 flex items-center gap-2">
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
                className="text-center text-lg tracking-widest"
                maxLength={4}
                disabled={isLoading}
              />
            </div>
            
            <Button 
              onClick={handlePinLogin}
              disabled={!pin || isLoading}
              className="w-full bg-red-600 hover:bg-red-700 text-white"
            >
              {isLoading && loginMethod === 'pin' ? 'Verifying...' : 'Access with PIN'}
            </Button>
          </div>
          
          <div className="text-center text-xs text-gray-500">
            Contact supervisor if you need access
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PinLogin;