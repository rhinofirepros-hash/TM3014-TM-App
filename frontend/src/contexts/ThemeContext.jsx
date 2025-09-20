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
    // Vision UI inspired backgrounds - sophisticated dark theme
    background: isDarkMode 
      ? 'bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 min-h-screen' 
      : 'bg-gradient-to-br from-gray-50 to-white min-h-screen',
    
    // Vision UI card styling - modern with subtle gradients and glass morphism
    card: isDarkMode 
      ? 'bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-xl border border-slate-700/50 text-white shadow-2xl shadow-black/20' 
      : 'bg-white/80 backdrop-blur-xl border border-gray-200/50 text-gray-900 shadow-xl shadow-gray-500/10',
    
    // Modern hover states with subtle transitions
    cardHover: isDarkMode 
      ? 'hover:from-slate-700/95 hover:to-slate-800/95 hover:border-slate-600/60 hover:shadow-3xl hover:shadow-purple-500/10 transition-all duration-300' 
      : 'hover:bg-white/90 hover:shadow-2xl hover:shadow-gray-500/20 hover:border-gray-300/60 transition-all duration-300',
    
    // Enhanced text hierarchy
    text: {
      primary: isDarkMode ? 'text-white font-medium' : 'text-gray-900 font-medium',
      secondary: isDarkMode ? 'text-slate-300' : 'text-gray-600',
      muted: isDarkMode ? 'text-slate-400' : 'text-gray-500',
      accent: isDarkMode ? 'text-purple-400' : 'text-purple-600',
      success: isDarkMode ? 'text-green-400' : 'text-green-600',
      warning: isDarkMode ? 'text-yellow-400' : 'text-yellow-600',
      error: isDarkMode ? 'text-red-400' : 'text-red-600',
    },
    
    // Modern header with gradient
    header: isDarkMode 
      ? 'bg-gradient-to-r from-slate-800/95 to-slate-900/95 backdrop-blur-xl border-b border-slate-700/50 shadow-lg' 
      : 'bg-white/95 backdrop-blur-xl border-b border-gray-200/50 shadow-sm',
    
    // Vision UI button styles
    button: {
      primary: isDarkMode 
        ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30' 
        : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 shadow-lg shadow-purple-500/25',
      secondary: isDarkMode 
        ? 'bg-slate-700/80 hover:bg-slate-600/90 text-white border border-slate-600/50 backdrop-blur-sm shadow-lg' 
        : 'bg-white/80 hover:bg-gray-50 text-gray-900 border border-gray-300 backdrop-blur-sm shadow-sm',
      ghost: isDarkMode 
        ? 'text-slate-300 hover:bg-slate-700/50 hover:text-white hover:backdrop-blur-sm' 
        : 'text-gray-600 hover:bg-gray-100/80 hover:text-gray-900',
      success: isDarkMode
        ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg shadow-green-500/25'
        : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg shadow-green-500/25',
      danger: isDarkMode
        ? 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white shadow-lg shadow-red-500/25'
        : 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white shadow-lg shadow-red-500/25',
    },
    
    // Modern input styling with glass morphism
    input: {
      primary: isDarkMode 
        ? 'bg-slate-800/60 backdrop-blur-sm border-slate-600/50 text-white placeholder-slate-400 focus:border-purple-500/70 focus:ring-2 focus:ring-purple-500/20 shadow-inner' 
        : 'bg-white/60 backdrop-blur-sm border-gray-300/50 text-gray-900 placeholder-gray-500 focus:border-purple-500/70 focus:ring-2 focus:ring-purple-500/20 shadow-sm',
      secondary: isDarkMode 
        ? 'bg-slate-700/40 backdrop-blur-sm border-slate-600/40 text-white placeholder-slate-400' 
        : 'bg-gray-50/60 backdrop-blur-sm border-gray-300/40 text-gray-900 placeholder-gray-500'
    },
    
    // Enhanced modal styling
    modal: isDarkMode 
      ? 'bg-gradient-to-br from-slate-800/95 to-slate-900/95 backdrop-blur-xl border border-slate-700/50 shadow-2xl shadow-black/30' 
      : 'bg-white/95 backdrop-blur-xl border border-gray-200/50 shadow-2xl shadow-gray-500/20',
      
    // Modern table styling
    table: isDarkMode
      ? 'bg-slate-800/60 backdrop-blur-sm border-slate-700/50 shadow-lg'
      : 'bg-white/80 backdrop-blur-sm border-gray-200/50 shadow-sm',
      
    // Enhanced dropdown styling
    dropdown: isDarkMode
      ? 'bg-slate-800/95 backdrop-blur-xl border-slate-600/50 text-white shadow-xl'
      : 'bg-white/95 backdrop-blur-xl border-gray-300/50 text-gray-900 shadow-lg',

    // Stats card styling for dashboards
    statsCard: isDarkMode
      ? 'bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/40 shadow-xl shadow-black/10'
      : 'bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl border border-gray-200/40 shadow-lg shadow-gray-500/10',

    // Badge styling
    badge: {
      primary: isDarkMode ? 'bg-purple-600/80 text-purple-100 backdrop-blur-sm' : 'bg-purple-600 text-white',
      secondary: isDarkMode ? 'bg-slate-600/80 text-slate-100 backdrop-blur-sm' : 'bg-gray-600 text-white',
      success: isDarkMode ? 'bg-green-600/80 text-green-100 backdrop-blur-sm' : 'bg-green-600 text-white',
      warning: isDarkMode ? 'bg-yellow-600/80 text-yellow-100 backdrop-blur-sm' : 'bg-yellow-600 text-white',
      error: isDarkMode ? 'bg-red-600/80 text-red-100 backdrop-blur-sm' : 'bg-red-600 text-white',
    }
  });

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, getThemeClasses }}>
      {children}
    </ThemeContext.Provider>
  );
};