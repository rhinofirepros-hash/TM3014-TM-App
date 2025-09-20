import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "../../lib/utils"
import { useTheme } from "../../contexts/ThemeContext"

const Badge = React.forwardRef(({ className, variant = "primary", ...props }, ref) => {
  const { getThemeClasses } = useTheme()
  const themeClasses = getThemeClasses()
  
  const baseClasses = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
  
  const variantClasses = {
    primary: themeClasses.badge.primary,
    secondary: themeClasses.badge.secondary,
    success: themeClasses.badge.success,
    warning: themeClasses.badge.warning,
    destructive: themeClasses.badge.error,
    outline: themeClasses.badge.secondary
  }
  
  return (
    <div
      ref={ref}
      className={cn(baseClasses, variantClasses[variant], className)}
      {...props}
    />
  )
})
Badge.displayName = "Badge"

export { Badge }