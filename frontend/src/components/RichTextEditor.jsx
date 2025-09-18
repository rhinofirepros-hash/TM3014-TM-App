import React, { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { useTheme } from '../contexts/ThemeContext';
import { 
  Bold, 
  Italic, 
  Underline, 
  List, 
  ListOrdered, 
  AlignLeft, 
  AlignCenter, 
  AlignRight, 
  Type 
} from 'lucide-react';

const RichTextEditor = ({ value, onChange }) => {
  const [isEditing, setIsEditing] = useState(false);
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  const toolbarButtons = [
    { icon: Type, label: 'Paragraph', action: () => {} },
    { icon: Bold, label: 'Bold', action: () => {} },
    { icon: Italic, label: 'Italic', action: () => {} },
    { icon: Underline, label: 'Underline', action: () => {} },
    { icon: List, label: 'Bullet List', action: () => {} },
    { icon: ListOrdered, label: 'Numbered List', action: () => {} },
    { icon: AlignLeft, label: 'Align Left', action: () => {} },
    { icon: AlignCenter, label: 'Align Center', action: () => {} },
    { icon: AlignRight, label: 'Align Right', action: () => {} },
  ];

  return (
    <div className={`border rounded-md ${
      isDarkMode 
        ? 'border-white/20 bg-white/5' 
        : 'border-gray-300 bg-white/80'
    }`}>
      {/* Toolbar */}
      <div className={`flex items-center gap-1 p-2 border-b ${
        isDarkMode 
          ? 'border-white/20 bg-white/10' 
          : 'border-gray-200 bg-gray-50/80'
      }`}>
        <select className={`text-sm border-0 bg-transparent mr-2 ${themeClasses.text.secondary}`}>
          <option>Paragraph</option>
        </select>
        <div className={`w-px h-6 mx-1 ${
          isDarkMode ? 'bg-white/30' : 'bg-gray-300'
        }`}></div>
        {toolbarButtons.slice(1).map((button, index) => (
          <Button
            key={index}
            variant="ghost"
            size="sm"
            className={`h-8 w-8 p-0 ${
              isDarkMode 
                ? 'hover:bg-white/20 text-white/70' 
                : 'hover:bg-gray-200 text-gray-600'
            }`}
            onClick={button.action}
          >
            <button.icon className="h-4 w-4" />
          </Button>
        ))}
      </div>

      {/* Content Area */}
      <div className="p-3">
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`min-h-[120px] border-0 resize-none focus:ring-0 p-0 ${
            isDarkMode 
              ? 'bg-transparent text-white placeholder-gray-400' 
              : 'bg-transparent text-gray-900 placeholder-gray-500'
          }`}
          placeholder="Enter description of work..."
        />
      </div>
    </div>
  );
};
};

export default RichTextEditor;