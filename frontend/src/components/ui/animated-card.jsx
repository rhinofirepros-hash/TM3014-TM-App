import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

const AnimatedCard = React.forwardRef(({ className, children, delay = 0, ...props }, ref) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const cardRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated) {
          setTimeout(() => {
            setIsVisible(true);
            setHasAnimated(true);
          }, delay);
        }
      },
      {
        threshold: 0.1, // Trigger when 10% visible
        rootMargin: '150px 0px -100px 0px' // Start animation earlier, more graceful
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
  }, [delay, hasAnimated]);

  return (
    <div
      ref={cardRef}
      className={cn(
        "rounded-lg border bg-card text-card-foreground shadow-sm transform group cursor-pointer",
        "will-change-transform transition-all duration-700 ease-[cubic-bezier(0.34,1.56,0.64,1)]",
        isVisible 
          ? "opacity-100 translate-y-0 scale-100" 
          : "opacity-0 translate-y-8 scale-95",
        "hover:scale-[1.02] hover:shadow-2xl hover:-translate-y-1 hover:rotate-[0.5deg]",
        "active:scale-[0.98] active:shadow-lg",
        className
      )}
      {...props}
    >
      <div className="relative overflow-hidden rounded-lg">
        {/* Gradient overlay effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Glass reflection effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out"></div>
        
        {children}
      </div>
    </div>
  );
});
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