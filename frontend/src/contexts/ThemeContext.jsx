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
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark' || (savedTheme === null && true); // Default to dark
  });

  useEffect(() => {
    // Save theme preference to localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update document class for global styling if needed
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  const getThemeClasses = () => ({
    background: isDarkMode 
      ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
      : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100',
    
    card: isDarkMode 
      ? 'backdrop-blur-md border-0 shadow-xl bg-white/10 text-white' 
      : 'backdrop-blur-md border-0 shadow-xl bg-white/70 text-gray-900',
    
    cardHover: isDarkMode 
      ? 'hover:bg-white/20' 
      : 'hover:bg-white/90',
    
    text: {
      primary: isDarkMode ? 'text-white' : 'text-gray-900',
      secondary: isDarkMode ? 'text-gray-300' : 'text-gray-600',
      muted: isDarkMode ? 'text-gray-400' : 'text-gray-500',
    },
    
    header: 'backdrop-blur-sm bg-white/10 border-b border-white/20',
    
    button: {
      ghost: isDarkMode 
        ? 'text-white hover:bg-white/20' 
        : 'text-gray-700 hover:bg-black/10',
      primary: isDarkMode 
        ? 'bg-blue-600 hover:bg-blue-700 text-white' 
        : 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: isDarkMode 
        ? 'bg-white/20 hover:bg-white/30 text-white' 
        : 'bg-gray-200 hover:bg-gray-300 text-gray-900',
    },
    
    input: isDarkMode 
      ? 'bg-white/10 border-white/20 text-white placeholder-gray-400' 
      : 'bg-white/70 border-gray-300 text-gray-900 placeholder-gray-500',
    
    modal: isDarkMode 
      ? 'bg-slate-900/95 backdrop-blur-md border-white/20' 
      : 'bg-white/95 backdrop-blur-md border-gray-200',
  });

  const value = {
    isDarkMode,
    toggleTheme,
    getThemeClasses,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};