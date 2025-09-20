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
    // VISION UI EXACT COLOR SCHEME - Dark theme matching the reference
    background: isDarkMode 
      ? 'bg-[#0F172A]' // Exact Vision UI dark background
      : 'bg-gray-50',
    
    // VISION UI CARD STYLING - Consistent across ALL components
    card: isDarkMode 
      ? 'bg-[#1E293B] border border-[#334155]/20 text-white shadow-xl shadow-black/10' 
      : 'bg-white border border-gray-200 text-gray-900 shadow-lg',
    
    // Vision UI hover effects - consistent everywhere
    cardHover: isDarkMode 
      ? 'hover:bg-[#1E293B]/90 hover:border-[#334155]/30 transition-all duration-200' 
      : 'hover:bg-gray-50 hover:border-gray-300 transition-all duration-200',
    
    // VISION UI TEXT COLORS - Exact matching
    text: {
      primary: isDarkMode ? 'text-white font-medium' : 'text-gray-900 font-medium',
      secondary: isDarkMode ? 'text-[#94A3B8]' : 'text-gray-600', // Exact Vision UI secondary text
      muted: isDarkMode ? 'text-[#64748B]' : 'text-gray-500', // Exact Vision UI muted text
      accent: isDarkMode ? 'text-[#3B82F6]' : 'text-blue-600', // Vision UI blue accent
      success: isDarkMode ? 'text-[#10B981]' : 'text-green-600', // Vision UI green
      warning: isDarkMode ? 'text-[#F59E0B]' : 'text-yellow-600', // Vision UI amber
      error: isDarkMode ? 'text-[#EF4444]' : 'text-red-600', // Vision UI red
    },
    
    // VISION UI HEADER - Exact styling
    header: isDarkMode 
      ? 'bg-[#1E293B] border-b border-[#334155]/20 shadow-lg' 
      : 'bg-white border-b border-gray-200 shadow-sm',
    
    // VISION UI BUTTONS - Consistent styling
    button: {
      primary: isDarkMode 
        ? 'bg-[#3B82F6] hover:bg-[#2563EB] text-white border-0 shadow-lg' 
        : 'bg-[#3B82F6] hover:bg-[#2563EB] text-white border-0 shadow-lg',
      secondary: isDarkMode 
        ? 'bg-[#1E293B] hover:bg-[#334155] text-white border border-[#334155]/50 shadow-sm' 
        : 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 shadow-sm',
      ghost: isDarkMode 
        ? 'text-[#94A3B8] hover:bg-[#1E293B] hover:text-white' 
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
      success: isDarkMode
        ? 'bg-[#10B981] hover:bg-[#059669] text-white shadow-lg'
        : 'bg-[#10B981] hover:bg-[#059669] text-white shadow-lg',
      danger: isDarkMode
        ? 'bg-[#EF4444] hover:bg-[#DC2626] text-white shadow-lg'
        : 'bg-[#EF4444] hover:bg-[#DC2626] text-white shadow-lg',
    },
    
    // VISION UI INPUTS - Consistent styling
    input: {
      primary: isDarkMode 
        ? 'bg-[#1E293B] border-[#334155]/50 text-white placeholder-[#64748B] focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]/20' 
        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]/20',
      secondary: isDarkMode 
        ? 'bg-[#0F172A] border-[#334155]/30 text-white placeholder-[#64748B]' 
        : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500'
    },
    
    // VISION UI MODALS - Consistent styling
    modal: isDarkMode 
      ? 'bg-[#1E293B] border border-[#334155]/20 shadow-2xl shadow-black/30' 
      : 'bg-white border border-gray-200 shadow-2xl shadow-gray-500/10',
      
    // VISION UI TABLES - Consistent styling
    table: isDarkMode
      ? 'bg-[#1E293B] border-[#334155]/20 shadow-lg'
      : 'bg-white border-gray-200 shadow-sm',
      
    // VISION UI DROPDOWNS - Consistent styling
    dropdown: isDarkMode
      ? 'bg-[#1E293B] border-[#334155]/50 text-white shadow-xl'
      : 'bg-white border-gray-300 text-gray-900 shadow-lg',

    // VISION UI STATS CARDS - Exact styling for consistency
    statsCard: isDarkMode
      ? 'bg-[#1E293B] border border-[#334155]/20 shadow-xl shadow-black/10'
      : 'bg-white border border-gray-200 shadow-lg',

    // VISION UI BADGES - Consistent styling
    badge: {
      primary: isDarkMode ? 'bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20' : 'bg-blue-100 text-blue-800',
      secondary: isDarkMode ? 'bg-[#64748B]/10 text-[#94A3B8] border border-[#64748B]/20' : 'bg-gray-100 text-gray-800',
      success: isDarkMode ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20' : 'bg-green-100 text-green-800',
      warning: isDarkMode ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20' : 'bg-yellow-100 text-yellow-800',
      error: isDarkMode ? 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20' : 'bg-red-100 text-red-800',
    },

    // VISION UI COLORS - Exact color values for consistency
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