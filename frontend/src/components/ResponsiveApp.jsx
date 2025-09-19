import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

const ResponsiveWrapper = ({ children }) => {
  const { isDarkMode } = useTheme();
  
  return (
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      <div className="w-full">
        {children}
      </div>
    </div>
  );
};

export default ResponsiveWrapper;