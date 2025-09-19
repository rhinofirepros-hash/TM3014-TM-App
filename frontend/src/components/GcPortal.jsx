import React, { useState } from 'react';
import GcLogin from './GcLogin';
import GcDashboard from './GcDashboard';

const GcPortal = () => {
  const [loginData, setLoginData] = useState(null);

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
          onLogout={handleLogout}
        />
      )}
    </div>
  );
};

export default GcPortal;