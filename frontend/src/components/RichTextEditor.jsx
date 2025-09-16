import React, { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
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
    <div className="border border-gray-300 rounded-md">
      {/* Toolbar */}
      <div className="flex items-center gap-1 p-2 border-b border-gray-200 bg-gray-50">
        <select className="text-sm border-0 bg-transparent text-gray-600 mr-2">
          <option>Paragraph</option>
        </select>
        <div className="w-px h-6 bg-gray-300 mx-1"></div>
        {toolbarButtons.slice(1).map((button, index) => (
          <Button
            key={index}
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 hover:bg-gray-200"
            onClick={button.action}
          >
            <button.icon className="h-4 w-4 text-gray-600" />
          </Button>
        ))}
      </div>

      {/* Content Area */}
      <div className="p-3">
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="min-h-[120px] border-0 resize-none focus:ring-0 p-0"
          placeholder="Enter description of work..."
        />
      </div>
    </div>
  );
};

export default RichTextEditor;