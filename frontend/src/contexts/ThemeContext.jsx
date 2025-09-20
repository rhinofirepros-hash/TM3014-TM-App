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
    // Modern, clean backgrounds
    background: isDarkMode 
      ? 'bg-slate-900' 
      : 'bg-gray-50',
    
    // Consistent card styling - modern, flat design
    card: isDarkMode 
      ? 'bg-slate-800 border border-slate-700 text-white' 
      : 'bg-white border border-gray-200 text-gray-900',
    
    // Hover states - subtle and modern
    cardHover: isDarkMode 
      ? 'hover:bg-slate-750 transition-colors duration-200' 
      : 'hover:bg-gray-50 transition-colors duration-200',
    
    // Text colors
    text: {
      primary: isDarkMode ? 'text-white' : 'text-gray-900',
      secondary: isDarkMode ? 'text-slate-300' : 'text-gray-600',
      muted: isDarkMode ? 'text-slate-400' : 'text-gray-500',
    },
    
    // Header styling
    header: isDarkMode 
      ? 'bg-slate-800 border-b border-slate-700' 
      : 'bg-white border-b border-gray-200',
    
    // Button variants
    button: {
      primary: isDarkMode 
        ? 'bg-blue-600 hover:bg-blue-700 text-white border-0' 
        : 'bg-blue-600 hover:bg-blue-700 text-white border-0',
      secondary: isDarkMode 
        ? 'bg-slate-700 hover:bg-slate-600 text-white border border-slate-600' 
        : 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300',
      ghost: isDarkMode 
        ? 'text-slate-300 hover:bg-slate-700 hover:text-white' 
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
    },
    
    // Input styling
    input: {
      primary: isDarkMode 
        ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500' 
        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:border-blue-500',
      secondary: isDarkMode 
        ? 'bg-slate-800 border-slate-600 text-white placeholder-slate-400' 
        : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500'
    },
    
    // Modal styling
    modal: isDarkMode 
      ? 'bg-slate-800 border border-slate-700' 
      : 'bg-white border border-gray-200',
      
    // Table styling
    table: isDarkMode
      ? 'bg-slate-800 border-slate-700'
      : 'bg-white border-gray-200',
      
    // Dropdown/Select styling
    dropdown: isDarkMode
      ? 'bg-slate-700 border-slate-600 text-white'
      : 'bg-white border-gray-300 text-gray-900',
  });

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, getThemeClasses }}>
      {children}
    </ThemeContext.Provider>
  );
};