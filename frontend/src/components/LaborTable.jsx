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
            <TableHead className="text-sm font-medium text-gray-700 w-48">
              Worker Name / Description*
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              Quantity Of Workers*
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              ST (Hrs)
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              OT (Hrs)
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              DT (Hrs)
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              POT (Hrs)
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              POT (Hrs)
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              Total (Hrs)
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              Date Of Work
              <Info className="w-4 h-4 text-gray-400 inline ml-1" />
            </TableHead>
            <TableHead className="text-sm font-medium text-gray-700 text-center">
              Actions
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.map((entry) => (
            <TableRow key={entry.id}>
              <TableCell>
                <Select
                  value={entry.workerName}
                  onValueChange={(value) => updateEntry(entry.id, 'workerName', value)}
                >
                  <SelectTrigger className="border-0 p-1 h-auto">
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
              <TableCell>
                <Input
                  type="number"
                  value={entry.quantity}
                  onChange={(e) => updateEntry(entry.id, 'quantity', e.target.value)}
                  className="border-0 p-1 text-center"
                  step="0.01"
                />
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  value={entry.stHours}
                  onChange={(e) => updateEntry(entry.id, 'stHours', e.target.value)}
                  className="border-0 p-1 text-center"
                  step="0.01"
                />
                <div className="text-xs text-gray-500 text-center mt-1">hrs</div>
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  value={entry.otHours}
                  onChange={(e) => updateEntry(entry.id, 'otHours', e.target.value)}
                  className="border-0 p-1 text-center"
                  step="0.01"
                />
                <div className="text-xs text-gray-500 text-center mt-1">hrs</div>
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  value={entry.dtHours}
                  onChange={(e) => updateEntry(entry.id, 'dtHours', e.target.value)}
                  className="border-0 p-1 text-center"
                  step="0.01"
                />
                <div className="text-xs text-gray-500 text-center mt-1">hrs</div>
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  value={entry.potHours}
                  onChange={(e) => updateEntry(entry.id, 'potHours', e.target.value)}
                  className="border-0 p-1 text-center"
                  step="0.01"
                />
                <div className="text-xs text-gray-500 text-center mt-1">hrs</div>
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  value={entry.potHours}
                  onChange={(e) => updateEntry(entry.id, 'potHours', e.target.value)}
                  className="border-0 p-1 text-center"
                  step="0.01"
                />
                <div className="text-xs text-gray-500 text-center mt-1">hrs</div>
              </TableCell>
              <TableCell className="text-center font-medium">
                {entry.totalHours.toFixed(2)}
              </TableCell>
              <TableCell>
                <Input
                  value={entry.date}
                  onChange={(e) => updateEntry(entry.id, 'date', e.target.value)}
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