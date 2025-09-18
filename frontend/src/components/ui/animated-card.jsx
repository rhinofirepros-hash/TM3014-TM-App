import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

const AnimatedCard = React.forwardRef(({ className, children, delay = 0, ...props }, ref) => {
  const [isVisible, setIsVisible] = useState(false);
  const cardRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            setIsVisible(true);
          }, delay);
        }
      },
      {
        threshold: 0.2, // Trigger when 20% visible
        rootMargin: '100px 0px -50px 0px' // Start animation earlier, more graceful
      }
    );

    if (cardRef.current) {
      observer.observe(cardRef.current);
    }

    return () => {
      if (cardRef.current) {
        observer.unobserve(cardRef.current);
      }
    };
  }, [delay]);

  return (
    <div
      ref={cardRef}
      className={cn(
        "rounded-lg border bg-card text-card-foreground shadow-sm transition-all duration-700 transform hover:scale-105 hover:shadow-2xl group cursor-pointer",
        isVisible 
          ? "opacity-100 translate-y-0 scale-100" 
          : "opacity-0 translate-y-8 scale-95",
        "hover:rotate-1 hover:-translate-y-2",
        className
      )}
      {...props}
    >
      <div className="relative overflow-hidden rounded-lg">
        {/* Gradient overlay effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-blue/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Glass reflection effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
        
        {children}
      </div>
    </div>
  );
});

AnimatedCard.displayName = "AnimatedCard";

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6 relative z-10", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight transition-colors duration-300",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground transition-colors duration-300", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div 
    ref={ref} 
    className={cn("p-6 pt-0 relative z-10", className)} 
    {...props} 
  />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0 relative z-10", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { AnimatedCard, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };