import * as React from "react"
import { cn } from "../../lib/utils"
import { useTheme } from "../../contexts/ThemeContext"

const Label = React.forwardRef(({ className, ...props }, ref) => {
  const { getThemeClasses } = useTheme()
  const themeClasses = getThemeClasses()
  
  return (
    <label
      ref={ref}
      className={cn(
        `text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${themeClasses.text.primary}`,
        className
      )}
      {...props}
    />
  )
})
Label.displayName = "Label"

export { Label }