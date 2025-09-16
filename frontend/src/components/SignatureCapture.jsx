import React, { useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Trash2, PenTool } from 'lucide-react';

const SignatureCapture = ({ isOpen, onClose, onSave }) => {
  const sigCanvas = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);

  const clear = () => {
    sigCanvas.current.clear();
    setIsEmpty(true);
  };

  const save = () => {
    if (sigCanvas.current.isEmpty()) {
      alert('Please provide a signature before saving.');
      return;
    }
    
    const signatureData = sigCanvas.current.getTrimmedCanvas().toDataURL('image/png');
    onSave(signatureData);
    onClose();
  };

  const handleCanvasChange = () => {
    setIsEmpty(sigCanvas.current.isEmpty());
  };

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
            <SignatureCanvas
              ref={sigCanvas}
              penColor="black"
              canvasProps={{
                width: window.innerWidth < 640 ? Math.min(window.innerWidth - 80, 500) : 600,
                height: window.innerWidth < 640 ? 150 : 200,
                className: 'signature-canvas bg-white rounded border w-full'
              }}
              onEnd={handleCanvasChange}
            />
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