import React from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Trash2, MoreVertical, Info } from 'lucide-react';

const EquipmentTable = ({ entries, onChange }) => {
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
    <div className="overflow-x-auto border rounded-lg">
      <Table className="min-w-[700px]">
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 min-w-[140px]">
              <div className="flex flex-col">
                <span>Equipment Name*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[100px]">
              <div className="flex flex-col items-center">
                <span>Pieces of Equipment*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              <div className="flex flex-col items-center">
                <span>Unit of Measure*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              <div className="flex flex-col items-center">
                <span>Quantity*</span>
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
              <TableCell colSpan={7} className="text-center py-8 text-gray-500">
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
                    className="border-0 p-2 h-8 text-xs sm:text-sm"
                  />
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    type="number"
                    value={entry.piecesOfEquipment}
                    onChange={(e) => updateEntry(entry.id, 'piecesOfEquipment', e.target.value)}
                    className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-20"
                    step="1"
                  />
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    value={entry.unitOfMeasure}
                    onChange={(e) => updateEntry(entry.id, 'unitOfMeasure', e.target.value)}
                    placeholder="Unit"
                    className="border-0 p-2 text-center h-8 text-xs sm:text-sm"
                  />
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    type="number"
                    value={entry.quantity}
                    onChange={(e) => updateEntry(entry.id, 'quantity', e.target.value)}
                    className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-16"
                    step="0.01"
                  />
                </TableCell>
                <TableCell className="text-center font-medium text-xs sm:text-sm p-1">
                  <div className="bg-gray-50 rounded px-2 py-1">
                    {entry.total.toFixed(2)}
                  </div>
                </TableCell>
                <TableCell className="p-1">
                  <Input
                    value={entry.dateOfWork}
                    onChange={(e) => updateEntry(entry.id, 'dateOfWork', e.target.value)}
                    className="border-0 p-2 text-center h-8 text-xs sm:text-sm min-w-[85px]"
                    placeholder="MM/DD/YYYY"
                  />
                </TableCell>
                <TableCell className="p-1">
                  <div className="flex gap-1 justify-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeEntry(entry.id)}
                      className="h-7 w-7 p-0 text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 text-gray-600 hover:bg-gray-50"
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
    </div>
  );
};

export default EquipmentTable;