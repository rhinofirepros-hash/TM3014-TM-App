import React from 'react';
import { cn } from '../../lib/utils';

const AnimatedButton = React.forwardRef(({ className, variant = "default", size = "default", children, ...props }, ref) => {
  const baseClasses = "relative inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 transform active:scale-95 hover:scale-105 hover:shadow-xl";
  
  const variants = {
    default: "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg hover:from-blue-700 hover:to-indigo-700 hover:shadow-2xl active:shadow-lg",
    destructive: "bg-gradient-to-r from-red-600 to-pink-600 text-white shadow-lg hover:from-red-700 hover:to-pink-700 hover:shadow-2xl active:shadow-lg",
    outline: "border border-white/30 bg-white/10 backdrop-blur-sm text-white shadow-lg hover:bg-white/20 hover:shadow-2xl active:shadow-lg hover:border-white/50",
    secondary: "bg-white/20 text-white shadow-lg hover:bg-white/30 hover:shadow-2xl active:shadow-lg backdrop-blur-sm",
    ghost: "text-white hover:bg-white/20 hover:shadow-lg active:shadow-sm",
    link: "text-blue-400 underline-offset-4 hover:underline hover:text-blue-300 transition-colors duration-200"
  };

  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10"
  };

  return (
    <button
      className={cn(
        baseClasses,
        variants[variant],
        sizes[size],
        "group overflow-hidden",
        className
      )}
      ref={ref}
      {...props}
    >
      <span className="relative z-10 flex items-center gap-2">
        {children}
      </span>
      
      {/* Ripple effect overlay */}
      <div className="absolute inset-0 opacity-0 group-active:opacity-20 bg-white rounded-md transition-opacity duration-150"></div>
      
      {/* Shine effect */}
      <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
    </button>
  );
});

AnimatedButton.displayName = "AnimatedButton";

export { AnimatedButton };