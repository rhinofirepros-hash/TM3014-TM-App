import React from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Trash2, MoreVertical, Info } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const MaterialTable = ({ entries, onChange }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const addEmptyRow = () => {
    const newEntry = {
      id: Date.now(),
      materialName: '',
      unitOfMeasure: '',
      quantity: 0,
      unitCost: 0,
      total: 0,
      dateOfWork: new Date().toLocaleDateString()
    };
    onChange([...entries, newEntry]);
  };

  const updateEntry = (id, field, value) => {
    const updatedEntries = entries.map(entry => {
      if (entry.id === id) {
        const updated = { ...entry, [field]: value };
        // Recalculate total
        if (field === 'quantity' || field === 'unitCost') {
          updated.total = (parseFloat(updated.quantity) || 0) * (parseFloat(updated.unitCost) || 0);
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
    <div className="overflow-x-auto border rounded-lg">
      <Table className="min-w-[600px]">
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 min-w-[120px]">
              <div className="flex flex-col">
                <span>Material Name*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              <div className="flex flex-col items-center">
                <span>Unit*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              <div className="flex flex-col items-center">
                <span>Qty*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              Total
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[90px]">
              <div className="flex flex-col items-center">
                <span>Date</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              Actions
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                No materials added yet. Click "Add empty row" to get started.
              </TableCell>
            </TableRow>
          ) : (
            entries.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell>
                  <Input
                    value={entry.materialName}
                    onChange={(e) => updateEntry(entry.id, 'materialName', e.target.value)}
                    placeholder="Material name"
                    className="border-0 p-1"
                  />
                </TableCell>
                <TableCell>
                  <Input
                    value={entry.unitOfMeasure}
                    onChange={(e) => updateEntry(entry.id, 'unitOfMeasure', e.target.value)}
                    placeholder="Unit"
                    className="border-0 p-1 text-center"
                  />
                </TableCell>
                <TableCell>
                  <Input
                    type="number"
                    value={entry.quantity}
                    onChange={(e) => updateEntry(entry.id, 'quantity', e.target.value)}
                    className="border-0 p-1 text-center"
                    step="0.01"
                  />
                </TableCell>
                <TableCell className="text-center font-medium">
                  ${entry.total.toFixed(2)}
                </TableCell>
                <TableCell>
                  <Input
                    value={entry.dateOfWork}
                    onChange={(e) => updateEntry(entry.id, 'dateOfWork', e.target.value)}
                    className="border-0 p-1 text-center"
                  />
                </TableCell>
                <TableCell>
                  <div className="flex gap-1 justify-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeEntry(entry.id)}
                      className="h-8 w-8 p-0 text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-gray-600 hover:bg-gray-50"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default MaterialTable;