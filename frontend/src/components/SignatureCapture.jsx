import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Trash2, PenTool } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const SignatureCapture = ({ isOpen, onClose, onSave }) => {
  const sigCanvas = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);
  const [canvasSize, setCanvasSize] = useState({ width: 600, height: 200 });
  const [signerName, setSignerName] = useState('');
  const [signerTitle, setSignerTitle] = useState('Foreman');
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  const clear = () => {
    sigCanvas.current.clear();
    setIsEmpty(true);
  };

  const save = () => {
    try {
      if (!sigCanvas.current) {
        alert('Signature canvas not available. Please try again.');
        return;
      }
      
      if (sigCanvas.current.isEmpty()) {
        alert('Please provide a signature before saving.');
        return;
      }
      
      if (!signerName.trim()) {
        alert('Please enter the signer\'s name before saving.');
        return;
      }
      
      const signatureData = sigCanvas.current.getTrimmedCanvas().toDataURL('image/png');
      onSave(signatureData, signerName, signerTitle);
      onClose();
      
      // Reset form
      setSignerName('');
      setSignerTitle('Foreman');
    } catch (error) {
      console.error('Error saving signature:', error);
      alert('Error saving signature. Please try again.');
    }
  };

  const handleCanvasChange = () => {
    if (sigCanvas.current) {
      setIsEmpty(sigCanvas.current.isEmpty());
    }
  };

  // Calculate canvas size based on container
  useEffect(() => {
    const updateCanvasSize = () => {
      const isMobile = window.innerWidth < 640;
      const maxWidth = isMobile ? Math.min(window.innerWidth - 60, 500) : 600;
      const height = isMobile ? 120 : 200;
      
      setCanvasSize({ width: maxWidth, height });
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, [isOpen]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`max-w-2xl mx-4 max-h-[90vh] overflow-y-auto ${themeClasses.modal}`}>
        <DialogHeader>
          <DialogTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
            <PenTool className="w-5 h-5" />
            Foreman Signature
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className={`text-sm ${themeClasses.text.secondary}`}>
            Please enter your information and sign below to confirm the accuracy of this Time & Material tag:
          </div>
          
          {/* Signer Information */}
          <div className={`grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-lg ${
            isDarkMode ? 'bg-white/5 border border-white/10' : 'bg-gray-50 border border-gray-200'
          }`}>
            <div className="space-y-2">
              <Label htmlFor="signerName" className={`text-sm font-medium ${themeClasses.text.primary}`}>
                Full Name *
              </Label>
              <Input
                id="signerName"
                type="text"
                placeholder="Enter your full name"
                value={signerName}
                onChange={(e) => setSignerName(e.target.value)}
                className={`w-full ${themeClasses.input}`}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="signerTitle" className={`text-sm font-medium ${themeClasses.text.primary}`}>
                Title/Position
              </Label>
              <Select value={signerTitle} onValueChange={setSignerTitle}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="Foreman">Foreman</SelectItem>
                  <SelectItem value="Supervisor">Supervisor</SelectItem>
                  <SelectItem value="Project Manager">Project Manager</SelectItem>
                  <SelectItem value="Technician">Technician</SelectItem>
                  <SelectItem value="Apprentice">Apprentice</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className={`border-2 border-dashed rounded-lg p-2 sm:p-4 ${
            isDarkMode 
              ? 'border-white/20 bg-white/5' 
              : 'border-gray-300 bg-gray-50'
          }`}>
            <div className="flex justify-center">
              <SignatureCanvas
                ref={sigCanvas}
                penColor={isDarkMode ? "white" : "black"}
                backgroundColor={isDarkMode ? "#1f2937" : "white"}
                dotSize={1}
                minWidth={1}
                maxWidth={3}
                throttle={16}
                minDistance={1}
                canvasProps={{
                  width: canvasSize.width,
                  height: canvasSize.height,
                  className: `signature-canvas rounded border touch-none ${
                    isDarkMode ? 'bg-gray-800 border-white/20' : 'bg-white border-gray-300'
                  }`,
                  style: { 
                    touchAction: 'none',
                    borderRadius: '4px'
                  }
                }}
                onEnd={handleCanvasChange}
                onBegin={() => setIsEmpty(false)}
              />
            </div>
          </div>
          
          <div className={`text-xs ${themeClasses.text.secondary}`}>
            Sign above using your mouse, trackpad, or touch screen
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
          <Button
            variant="outline"
            onClick={clear}
            disabled={isEmpty}
            className={`flex items-center justify-center gap-2 h-10 ${themeClasses.button.secondary}`}
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </Button>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <Button 
              variant="outline" 
              onClick={onClose} 
              className={`h-10 ${themeClasses.button.secondary}`}
            >
              Cancel
            </Button>
            <Button 
              onClick={save}
              disabled={isEmpty}
              className={`h-10 ${themeClasses.button.primary}`}
            >
              Save Signature
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default SignatureCapture;