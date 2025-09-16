import React from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Trash2, MoreVertical, Info, Plus } from 'lucide-react';
import { mockData } from '../data/mock';

const LaborTable = ({ entries, onChange }) => {
  const addEmptyRow = () => {
    const newEntry = {
      id: Date.now(),
      workerName: 'Jesus Garcia',
      quantity: 1,
      stHours: 8.00,
      otHours: 0,
      dtHours: 0,
      potHours: 0,
      totalHours: 8.00,
      date: new Date().toLocaleDateString()
    };
    onChange([...entries, newEntry]);
  };

  const addJesusRow = () => {
    const jesusEntry = {
      id: Date.now(),
      workerName: 'Jesus Garcia',
      quantity: 1,
      stHours: 8.00,
      otHours: 0,
      dtHours: 0,
      potHours: 0,
      totalHours: 8.00,
      date: new Date().toLocaleDateString()
    };
    onChange([...entries, jesusEntry]);
  };

  const updateEntry = (id, field, value) => {
    const updatedEntries = entries.map(entry => {
      if (entry.id === id) {
        const updated = { ...entry, [field]: value };
        // Recalculate total hours
        updated.totalHours = 
          (parseFloat(updated.stHours) || 0) + 
          (parseFloat(updated.otHours) || 0) + 
          (parseFloat(updated.dtHours) || 0) + 
          (parseFloat(updated.potHours) || 0);
        return updated;
      }
      return entry;
    });
    onChange(updatedEntries);
  };

  const removeEntry = (id) => {
    onChange(entries.filter(entry => entry.id !== id));
  };

  const getTotalHours = () => {
    return entries.reduce((total, entry) => total + (parseFloat(entry.totalHours) || 0), 0).toFixed(2);
  };

  const getColumnTotal = (column) => {
    return entries.reduce((total, entry) => total + (parseFloat(entry[column]) || 0), 0).toFixed(2);
  };

  return (
    <div className="overflow-x-auto border rounded-lg">
      <Table className="min-w-[800px]">
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 min-w-[140px]">
              <div className="flex flex-col">
                <span>Worker Name*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              <div className="flex flex-col items-center">
                <span>Qty*</span>
                <Info className="w-3 h-3 text-gray-400 mt-1" />
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[70px]">
              <div className="flex flex-col items-center">
                <span>ST</span>
                <span className="text-xs text-gray-500">(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[70px]">
              <div className="flex flex-col items-center">
                <span>OT</span>
                <span className="text-xs text-gray-500">(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[70px]">
              <div className="flex flex-col items-center">
                <span>DT</span>
                <span className="text-xs text-gray-500">(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[70px]">
              <div className="flex flex-col items-center">
                <span>POT</span>
                <span className="text-xs text-gray-500">(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[70px]">
              <div className="flex flex-col items-center">
                <span>POT</span>
                <span className="text-xs text-gray-500">(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className="text-xs sm:text-sm font-medium text-gray-700 text-center min-w-[80px]">
              <div className="flex flex-col items-center">
                <span>Total</span>
                <span className="text-xs text-gray-500">(Hrs)</span>
              </div>
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
          {entries.map((entry) => (
            <TableRow key={entry.id}>
              <TableCell className="p-1">
                <Select
                  value={entry.workerName}
                  onValueChange={(value) => updateEntry(entry.id, 'workerName', value)}
                >
                  <SelectTrigger className="border-0 p-2 h-8 text-xs sm:text-sm min-w-[120px]">
                    <SelectValue placeholder="Select worker" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockData.workers.map((worker) => (
                      <SelectItem key={worker.id} value={worker.name}>
                        {worker.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.stHours}
                  onChange={(e) => updateEntry(entry.id, 'stHours', e.target.value)}
                  className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-14"
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.otHours}
                  onChange={(e) => updateEntry(entry.id, 'otHours', e.target.value)}
                  className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-14"
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.dtHours}
                  onChange={(e) => updateEntry(entry.id, 'dtHours', e.target.value)}
                  className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-14"
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.potHours}
                  onChange={(e) => updateEntry(entry.id, 'potHours', e.target.value)}
                  className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-14"
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.potHours}
                  onChange={(e) => updateEntry(entry.id, 'potHours', e.target.value)}
                  className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-14"
                  step="0.01"
                />
              </TableCell>
              <TableCell className="text-center font-medium text-xs sm:text-sm p-1">
                <div className="bg-gray-50 rounded px-2 py-1">
                  {entry.totalHours.toFixed(2)}
                </div>
              </TableCell>
              <TableCell className="p-1">
                <Input
                  value={entry.date}
                  onChange={(e) => updateEntry(entry.id, 'date', e.target.value)}
                  className="border-0 p-2 text-center h-8 text-xs sm:text-sm w-20"
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
          ))}
          
          {/* Totals Row */}
          <TableRow className="bg-gray-50 font-medium">
            <TableCell colSpan={2} className="text-right">
              Total Labor Hours:
            </TableCell>
            <TableCell className="text-center">
              {getColumnTotal('stHours')}
            </TableCell>
            <TableCell className="text-center">
              {getColumnTotal('otHours')}
            </TableCell>
            <TableCell className="text-center">
              {getColumnTotal('dtHours')}
            </TableCell>
            <TableCell className="text-center">
              {getColumnTotal('potHours')}
            </TableCell>
            <TableCell className="text-center">
              {getColumnTotal('potHours')}
            </TableCell>
            <TableCell className="text-center">
              {getTotalHours()}
            </TableCell>
            <TableCell colSpan={2}></TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
};

export default LaborTable;