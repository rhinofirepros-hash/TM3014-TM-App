import React, { useState, useEffect } from 'react';
import GcLogin from './GcLogin';
import EnhancedGcDashboard from './EnhancedGcDashboard';

const GcPortal = () => {
  const [loginData, setLoginData] = useState(null);

  useEffect(() => {
    // Check if we have a direct project ID in the URL (for admin access)
    const path = window.location.pathname;
    const match = path.match(/^\/gc-portal\/(.+)$/);
    
    if (match) {
      const projectId = match[1];
      // Direct admin access - skip login for admins
      setLoginData({
        projectId: projectId,
        keyId: null,
        adminAccess: true
      });
    }
  }, []);

  const handleLoginSuccess = (data) => {
    setLoginData(data);
  };

  const handleLogout = () => {
    setLoginData(null);
  };

  return (
    <div>
      {!loginData ? (
        <GcLogin onLoginSuccess={handleLoginSuccess} />
      ) : (
        <GcDashboard 
          projectId={loginData.projectId} 
          keyId={loginData.keyId}
          adminAccess={loginData.adminAccess}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
};

export default GcPortal;