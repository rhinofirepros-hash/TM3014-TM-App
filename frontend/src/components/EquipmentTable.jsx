import React from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Trash2, MoreVertical, Info } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const EquipmentTable = ({ entries, onChange }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  const addEmptyRow = () => {
    const newEntry = {
      id: Date.now(),
      equipmentName: '',
      typeOfEquipment: '',
      quantity: 0,
      piecesOfEquipment: 0,
      total: 0,
      dateOfWork: new Date().toLocaleDateString()
    };
    onChange([...entries, newEntry]);
  };

  const updateEntry = (id, field, value) => {
    const updatedEntries = entries.map(entry => {
      if (entry.id === id) {
        const updated = { ...entry, [field]: value };
        // Recalculate total if needed
        if (field === 'quantity' || field === 'piecesOfEquipment') {
          updated.total = (parseFloat(updated.quantity) || 0) * (parseFloat(updated.piecesOfEquipment) || 0);
        }
        return updated;
      }
      return entry;
    });
    onChange(updatedEntries);
  };

  const removeEntry = (id) => {
    onChange(entries.filter(entry => entry.id !== id));
  };

  return (
    <div className={`overflow-x-auto border rounded-lg ${
      isDarkMode 
        ? 'border-white/20 bg-white/5' 
        : 'border-gray-300 bg-white/80'
    }`}>
      <Table className="min-w-[700px]">
        <TableHeader>
          <TableRow className={`${
            isDarkMode 
              ? 'bg-white/10 border-white/20' 
              : 'bg-gray-50/80 border-gray-200'
          }`}>
            <TableHead className={`text-xs sm:text-sm font-medium min-w-[140px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col">
                <span>Equipment Name*</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[100px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>Pieces of Equipment*</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[80px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>Unit of Measure*</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[80px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>Quantity*</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[80px] ${themeClasses.text.primary}`}>
              Total
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[90px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>Date</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[80px] ${themeClasses.text.primary}`}>
              Actions
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className={`text-center py-8 ${themeClasses.text.secondary}`}>
                No equipment added yet. Click "Add empty row" to get started.
              </TableCell>
            </TableRow>
          ) : (
            entries.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell className="p-1">
                  <Input
                    value={entry.equipmentName}
                    onChange={(e) => updateEntry(entry.id, 'equipmentName', e.target.value)}
                    placeholder="Equipment name"
                    className={`border-0 p-2 h-8 text-xs sm:text-sm ${themeClasses.input}`}
                  />
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    type="number"
                    value={entry.piecesOfEquipment}
                    onChange={(e) => updateEntry(entry.id, 'piecesOfEquipment', e.target.value)}
                    className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-20 ${themeClasses.input}`}
                    step="1"
                  />
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    value={entry.unitOfMeasure}
                    onChange={(e) => updateEntry(entry.id, 'unitOfMeasure', e.target.value)}
                    placeholder="Unit"
                    className={`border-0 p-2 text-center h-8 text-xs sm:text-sm ${themeClasses.input}`}
                  />
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    type="number"
                    value={entry.quantity}
                    onChange={(e) => updateEntry(entry.id, 'quantity', e.target.value)}
                    className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-16 ${themeClasses.input}`}
                    step="0.01"
                  />
                </TableCell>
                <TableCell className={`text-center font-medium text-xs sm:text-sm p-1 ${themeClasses.text.primary}`}>
                  <div className={`rounded px-2 py-1 ${
                    isDarkMode 
                      ? 'bg-white/10 border border-white/20' 
                      : 'bg-gray-50 border border-gray-200'
                  }`}>
                    {entry.total.toFixed(2)}
                  </div>
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    value={entry.dateOfWork}
                    onChange={(e) => updateEntry(entry.id, 'dateOfWork', e.target.value)}
                    className={`border-0 p-2 text-center h-8 text-xs sm:text-sm min-w-[85px] ${themeClasses.input}`}
                    placeholder="MM/DD/YYYY"
                  />
                </TableCell>
                <TableCell className="p-1">
                  <div className="flex gap-1 justify-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeEntry(entry.id)}
                      className={`h-7 w-7 p-0 text-red-600 ${
                        isDarkMode ? 'hover:bg-red-900/20' : 'hover:bg-red-50'
                      }`}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className={`h-7 w-7 p-0 ${
                        isDarkMode 
                          ? 'text-white/70 hover:bg-white/20' 
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <MoreVertical className="h-3 w-3" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      
      {/* Add Equipment Button */}
      <div className={`p-4 border-t ${
        isDarkMode 
          ? 'border-white/20 bg-white/5' 
          : 'border-gray-200 bg-gray-50/50'
      }`}>
        <Button
          onClick={addEmptyRow}
          className={`w-full ${
            isDarkMode
              ? 'bg-orange-600 hover:bg-orange-700 text-white'
              : 'bg-orange-600 hover:bg-orange-700 text-white'
          }`}
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Equipment
        </Button>
      </div>
    </div>
  );
};

export default EquipmentTable;