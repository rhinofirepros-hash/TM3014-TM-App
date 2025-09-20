import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority"
import { cn } from "../../lib/utils"
import { useTheme } from "../../contexts/ThemeContext"

const Button = React.forwardRef(({ className, variant = "primary", size = "default", asChild = false, ...props }, ref) => {
  const { getThemeClasses } = useTheme()
  const themeClasses = getThemeClasses()
  const Comp = asChild ? Slot : "button"
  
  const baseClasses = "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
  
  const variantClasses = {
    primary: themeClasses.button.primary,
    secondary: themeClasses.button.secondary, 
    ghost: themeClasses.button.ghost,
    success: themeClasses.button.success,
    destructive: themeClasses.button.danger,
    outline: themeClasses.button.secondary,
    link: "text-primary underline-offset-4 hover:underline"
  }
  
  const sizeClasses = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10"
  }
  
  return (
    <Comp
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size], 
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button }