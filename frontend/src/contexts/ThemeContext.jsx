import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : false;
  });

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const getThemeClasses = () => ({
    // EXACT COLOR SCHEME from user's preferred screenshot - Blue-tinted dark theme
    background: isDarkMode 
      ? 'bg-[#1a202c]' // Blue-tinted dark background (not almost black)
      : 'bg-gray-50',
    
    // Cards that match the screenshot - lighter blue than background
    card: isDarkMode 
      ? 'bg-[#2d3748] border border-[#4a5568]/30 text-white shadow-lg' 
      : 'bg-white border border-gray-200 text-gray-900 shadow-lg',
    
    // Consistent hover effects
    cardHover: isDarkMode 
      ? 'hover:bg-[#2d3748]/90 hover:border-[#4a5568]/40 transition-all duration-200' 
      : 'hover:bg-gray-50 hover:border-gray-300 transition-all duration-200',
    
    // Text colors that match the screenshot
    text: {
      primary: isDarkMode ? 'text-white font-medium' : 'text-gray-900 font-medium',
      secondary: isDarkMode ? 'text-[#a0aec0]' : 'text-gray-600', // Light gray for good contrast
      muted: isDarkMode ? 'text-[#718096]' : 'text-gray-500', // Slightly darker gray for muted
      accent: isDarkMode ? 'text-[#4299e1]' : 'text-blue-600', // Nice blue accent
      success: isDarkMode ? 'text-[#48bb78]' : 'text-green-600', 
      warning: isDarkMode ? 'text-[#ed8936]' : 'text-yellow-600', 
      error: isDarkMode ? 'text-[#f56565]' : 'text-red-600', 
    },
    
    // Header matching the screenshot style
    header: isDarkMode 
      ? 'bg-[#2d3748] border-b border-[#4a5568]/30 shadow-lg' 
      : 'bg-white border-b border-gray-200 shadow-sm',
    
    // Buttons that match the blue theme
    button: {
      primary: isDarkMode 
        ? 'bg-[#4299e1] hover:bg-[#3182ce] text-white border-0 shadow-lg' 
        : 'bg-[#4299e1] hover:bg-[#3182ce] text-white border-0 shadow-lg',
      secondary: isDarkMode 
        ? 'bg-[#2d3748] hover:bg-[#4a5568] text-white border border-[#4a5568]/50 shadow-sm' 
        : 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 shadow-sm',
      ghost: isDarkMode 
        ? 'text-[#a0aec0] hover:bg-[#2d3748] hover:text-white' 
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
      success: isDarkMode
        ? 'bg-[#48bb78] hover:bg-[#38a169] text-white shadow-lg'
        : 'bg-[#48bb78] hover:bg-[#38a169] text-white shadow-lg',
      danger: isDarkMode
        ? 'bg-[#f56565] hover:bg-[#e53e3e] text-white shadow-lg'
        : 'bg-[#f56565] hover:bg-[#e53e3e] text-white shadow-lg',
    },
    
    // Inputs with blue theme
    input: {
      primary: isDarkMode 
        ? 'bg-[#2d3748] border-[#4a5568]/50 text-white placeholder-[#718096] focus:border-[#4299e1] focus:ring-1 focus:ring-[#4299e1]/20' 
        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:border-[#4299e1] focus:ring-1 focus:ring-[#4299e1]/20',
      secondary: isDarkMode 
        ? 'bg-[#1a202c] border-[#4a5568]/30 text-white placeholder-[#718096]' 
        : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500'
    },
    
    // Modals with blue theme
    modal: isDarkMode 
      ? 'bg-[#2d3748] border border-[#4a5568]/30 shadow-2xl shadow-black/20' 
      : 'bg-white border border-gray-200 shadow-2xl shadow-gray-500/10',
      
    // Tables with blue theme
    table: isDarkMode
      ? 'bg-[#2d3748] border-[#4a5568]/30 shadow-lg'
      : 'bg-white border-gray-200 shadow-sm',
      
    // Dropdowns with blue theme
    dropdown: isDarkMode
      ? 'bg-[#2d3748] border-[#4a5568]/50 text-white shadow-xl'
      : 'bg-white border-gray-300 text-gray-900 shadow-lg',

    // Stats cards matching the screenshot exactly
    statsCard: isDarkMode
      ? 'bg-[#2d3748] border border-[#4a5568]/30 shadow-lg'
      : 'bg-white border border-gray-200 shadow-lg',

    // Badges with blue theme
    badge: {
      primary: isDarkMode ? 'bg-[#4299e1]/10 text-[#4299e1] border border-[#4299e1]/20' : 'bg-blue-100 text-blue-800',
      secondary: isDarkMode ? 'bg-[#718096]/10 text-[#a0aec0] border border-[#718096]/20' : 'bg-gray-100 text-gray-800',
      success: isDarkMode ? 'bg-[#48bb78]/10 text-[#48bb78] border border-[#48bb78]/20' : 'bg-green-100 text-green-800',
      warning: isDarkMode ? 'bg-[#ed8936]/10 text-[#ed8936] border border-[#ed8936]/20' : 'bg-yellow-100 text-yellow-800',
      error: isDarkMode ? 'bg-[#f56565]/10 text-[#f56565] border border-[#f56565]/20' : 'bg-red-100 text-red-800',
    },

    // Color palette matching the screenshot
    colors: {
      blue: isDarkMode ? '#4299e1' : '#4299e1',
      green: isDarkMode ? '#48bb78' : '#48bb78', 
      red: isDarkMode ? '#f56565' : '#f56565',
      amber: isDarkMode ? '#ed8936' : '#ed8936',
      purple: isDarkMode ? '#9f7aea' : '#9f7aea',
      pink: isDarkMode ? '#ed64a6' : '#ed64a6',
      indigo: isDarkMode ? '#667eea' : '#667eea',
      cyan: isDarkMode ? '#38b2ac' : '#38b2ac',
    }
  });

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, getThemeClasses }}>
      {children}
    </ThemeContext.Provider>
  );
};