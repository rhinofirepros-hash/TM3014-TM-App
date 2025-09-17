import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Trash2, PenTool } from 'lucide-react';

const SignatureCapture = ({ isOpen, onClose, onSave }) => {
  const sigCanvas = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);
  const [canvasSize, setCanvasSize] = useState({ width: 600, height: 200 });
  const [signerName, setSignerName] = useState('');
  const [signerTitle, setSignerTitle] = useState('Foreman');

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
      <DialogContent className="max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <PenTool className="w-5 h-5" />
            Foreman Signature
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="text-sm text-gray-600">
            Please sign below to confirm the accuracy of this Time & Material tag:
          </div>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-2 sm:p-4 bg-gray-50">
            <div className="flex justify-center">
              <SignatureCanvas
                ref={sigCanvas}
                penColor="black"
                backgroundColor="white"
                dotSize={1}
                minWidth={1}
                maxWidth={3}
                throttle={16}
                minDistance={1}
                canvasProps={{
                  width: canvasSize.width,
                  height: canvasSize.height,
                  className: 'signature-canvas bg-white rounded border touch-none',
                  style: { 
                    touchAction: 'none',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px'
                  }
                }}
                onEnd={handleCanvasChange}
                onBegin={() => setIsEmpty(false)}
              />
            </div>
          </div>
          
          <div className="text-xs text-gray-500">
            Sign above using your mouse, trackpad, or touch screen
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
          <Button
            variant="outline"
            onClick={clear}
            disabled={isEmpty}
            className="flex items-center justify-center gap-2 h-10"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </Button>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <Button variant="outline" onClick={onClose} className="h-10">
              Cancel
            </Button>
            <Button 
              onClick={save}
              disabled={isEmpty}
              className="bg-green-600 hover:bg-green-700 h-10"
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