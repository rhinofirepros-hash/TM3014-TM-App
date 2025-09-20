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
    return saved ? saved === 'dark' : true; // Default to dark mode
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
    // EXACT SAME COLORS AS T&M REPORTS PAGE
    background: isDarkMode 
      ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
      : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100',
    
    // Cards matching T&M Reports styling - REMOVED BORDER
    card: isDarkMode 
      ? 'backdrop-blur-xl bg-white/10 text-white shadow-2xl' 
      : 'bg-white text-gray-900 shadow-lg',
    
    // Hover effects matching T&M Reports
    cardHover: isDarkMode 
      ? 'hover:bg-white/20 transition-all duration-200' 
      : 'hover:bg-gray-50 transition-all duration-200',
    
    // Text colors matching T&M Reports
    text: {
      primary: isDarkMode ? 'text-white font-medium' : 'text-gray-900 font-medium',
      secondary: isDarkMode ? 'text-gray-300' : 'text-gray-600',
      muted: isDarkMode ? 'text-gray-400' : 'text-gray-500',
      accent: isDarkMode ? 'text-blue-400' : 'text-blue-600',
      success: isDarkMode ? 'text-green-400' : 'text-green-600', 
      warning: isDarkMode ? 'text-yellow-400' : 'text-yellow-600', 
      error: isDarkMode ? 'text-red-400' : 'text-red-600', 
    },
    
    // Header matching T&M Reports exactly - REMOVED BORDER
    header: isDarkMode 
      ? 'backdrop-blur-xl bg-white/10' 
      : 'bg-white shadow-sm',
    
    // Buttons matching T&M Reports
    button: {
      primary: isDarkMode 
        ? 'bg-blue-600 hover:bg-blue-700 text-white border-0 shadow-lg' 
        : 'bg-blue-600 hover:bg-blue-700 text-white border-0 shadow-lg',
      secondary: isDarkMode 
        ? 'backdrop-blur-xl bg-white/10 hover:bg-white/20 text-white shadow-sm' 
        : 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 shadow-sm',
      ghost: isDarkMode 
        ? 'text-gray-300 hover:bg-white/10 hover:text-white' 
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
      success: isDarkMode
        ? 'bg-green-600 hover:bg-green-700 text-white shadow-lg'
        : 'bg-green-600 hover:bg-green-700 text-white shadow-lg',
      danger: isDarkMode
        ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg'
        : 'bg-red-600 hover:bg-red-700 text-white shadow-lg',
    },
    
    // Inputs matching T&M Reports - REMOVED BORDER
    input: {
      primary: isDarkMode 
        ? 'backdrop-blur-xl bg-white/10 text-white placeholder-gray-400 focus:border-blue-400 focus:ring-1 focus:ring-blue-400/20' 
        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:border-blue-600 focus:ring-1 focus:ring-blue-600/20',
      secondary: isDarkMode 
        ? 'backdrop-blur-xl bg-white/5 text-white placeholder-gray-400' 
        : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500'
    },
    
    // Modals matching T&M Reports - REMOVED BORDER
    modal: isDarkMode 
      ? 'backdrop-blur-xl bg-white/10 shadow-2xl' 
      : 'bg-white shadow-2xl shadow-gray-500/10',
      
    // Tables matching T&M Reports - REMOVED BORDER
    table: isDarkMode
      ? 'backdrop-blur-xl bg-white/10 shadow-lg'
      : 'bg-white shadow-sm',
      
    // Dropdowns matching T&M Reports - REMOVED BORDER
    dropdown: isDarkMode
      ? 'backdrop-blur-xl bg-white/10 text-white shadow-xl'
      : 'bg-white text-gray-900 shadow-lg',

    // Stats cards matching T&M Reports exactly - REMOVED BORDER
    statsCard: isDarkMode
      ? 'backdrop-blur-xl bg-white/10 shadow-2xl'
      : 'bg-white shadow-lg',

    // Badges matching T&M Reports
    badge: {
      primary: isDarkMode ? 'bg-blue-600/80 text-blue-100' : 'bg-blue-100 text-blue-800',
      secondary: isDarkMode ? 'bg-gray-600/80 text-gray-100' : 'bg-gray-100 text-gray-800',
      success: isDarkMode ? 'bg-green-600/80 text-green-100' : 'bg-green-100 text-green-800',
      warning: isDarkMode ? 'bg-yellow-600/80 text-yellow-100' : 'bg-yellow-100 text-yellow-800',
      error: isDarkMode ? 'bg-red-600/80 text-red-100' : 'bg-red-100 text-red-800',
    },

    // Colors matching T&M Reports
    colors: {
      blue: isDarkMode ? '#3B82F6' : '#3B82F6',
      green: isDarkMode ? '#10B981' : '#10B981', 
      red: isDarkMode ? '#EF4444' : '#EF4444',
      amber: isDarkMode ? '#F59E0B' : '#F59E0B',
      purple: isDarkMode ? '#8B5CF6' : '#8B5CF6',
      pink: isDarkMode ? '#EC4899' : '#EC4899',
      indigo: isDarkMode ? '#6366F1' : '#6366F1',
      cyan: isDarkMode ? '#06B6D4' : '#06B6D4',
    }
  });

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, getThemeClasses }}>
      {children}
    </ThemeContext.Provider>
  );
};