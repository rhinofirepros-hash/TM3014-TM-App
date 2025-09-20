import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { cn } from '../../lib/utils';

const StatsCard = ({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  iconColor = 'text-blue-500',
  onClick,
  className,
  ...props 
}) => {
  const { getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  return (
    <div
      className={cn(
        `rounded-lg p-6 ${themeClasses.statsCard}`,
        onClick && 'cursor-pointer transform hover:scale-105 transition-all duration-200',
        className
      )}
      onClick={onClick}
      {...props}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className={`text-sm font-medium ${themeClasses.text.secondary} mb-2`}>
            {title}
          </p>
          <p className={`text-3xl font-bold ${themeClasses.text.primary} mb-1`}>
            {value}
          </p>
          {subtitle && (
            <p className={`text-xs ${themeClasses.text.muted}`}>
              {subtitle}
            </p>
          )}
        </div>
        {Icon && (
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${iconColor} bg-current/10`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  );
};

export { StatsCard };