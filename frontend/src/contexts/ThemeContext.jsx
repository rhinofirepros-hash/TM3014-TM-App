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
      : 'bg-gradient-to-br from-blue-50/80 via-indigo-50/60 to-slate-100/90',
    
    card: isDarkMode 
      ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
      : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30',
    
    cardHover: isDarkMode 
      ? 'hover:bg-white/20 hover:shadow-3xl transition-all duration-300' 
      : 'hover:bg-white/60 hover:shadow-3xl transition-all duration-300',
    
    text: {
      primary: isDarkMode ? 'text-white' : 'text-gray-900',
      secondary: isDarkMode ? 'text-gray-300' : 'text-gray-600',
      muted: isDarkMode ? 'text-gray-400' : 'text-gray-500',
    },
    
    header: isDarkMode 
      ? 'backdrop-blur-xl bg-white/10 border-b border-white/20' 
      : 'backdrop-blur-xl bg-white/30 border-b border-white/40',
    
    button: {
      ghost: isDarkMode 
        ? 'text-white hover:bg-white/20 backdrop-blur border-white/20' 
        : 'text-gray-700 hover:bg-white/40 backdrop-blur border-gray-300/50',
      primary: isDarkMode 
        ? 'bg-blue-600/80 hover:bg-blue-700/90 text-white backdrop-blur border-blue-500/30' 
        : 'bg-blue-600/80 hover:bg-blue-700/90 text-white backdrop-blur border-blue-500/30',
      secondary: isDarkMode 
        ? 'bg-white/20 hover:bg-white/30 text-white backdrop-blur border-white/30' 
        : 'bg-white/50 hover:bg-white/70 text-gray-900 backdrop-blur border-gray-300/50',
    },
    
    input: isDarkMode 
      ? 'bg-white/10 border-white/20 text-white placeholder-gray-400 backdrop-blur' 
      : 'bg-white/60 border-gray-300/50 text-gray-900 placeholder-gray-500 backdrop-blur',
    
    modal: isDarkMode 
      ? 'bg-slate-900/95 backdrop-blur-xl border-white/20 shadow-2xl' 
      : 'bg-white/95 backdrop-blur-xl border-gray-200/50 shadow-2xl',
      
    table: isDarkMode
      ? 'bg-white/5 backdrop-blur border-white/10'
      : 'bg-white/50 backdrop-blur border-gray-200/30',
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