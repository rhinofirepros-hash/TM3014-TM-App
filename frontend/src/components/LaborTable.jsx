import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Trash2, MoreVertical, Info, Plus } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const LaborTable = ({ entries, onChange, onSaveWorker }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  // State for installers/workers from API
  const [availableWorkers, setAvailableWorkers] = useState([]);
  const [isLoadingWorkers, setIsLoadingWorkers] = useState(false);
  
  // Load workers from the new Rhino Platform installers endpoint
  useEffect(() => {
    const loadWorkers = async () => {
      try {
        setIsLoadingWorkers(true);
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        if (backendUrl) {
          const response = await fetch(`${backendUrl}/api/installers`);
          if (response.ok) {
            const workersData = await response.json();
            setAvailableWorkers(workersData);
          } else {
            console.warn('Failed to load workers from API, falling back to localStorage');
            // Fallback to localStorage for backward compatibility
            const savedWorkers = JSON.parse(localStorage.getItem('saved_workers') || '[]');
            setAvailableWorkers(savedWorkers);
          }
        }
      } catch (error) {
        console.error('Error loading workers:', error);
        // Fallback to localStorage
        const savedWorkers = JSON.parse(localStorage.getItem('saved_workers') || '[]');
        setAvailableWorkers(savedWorkers);
      } finally {
        setIsLoadingWorkers(false);
      }
    };
    
    loadWorkers();
  }, []);
  const addEmptyRow = () => {
    const newEntry = {
      id: Date.now(),
      workerName: '',
      quantity: 1,
      stHours: 0,
      otHours: 0,
      dtHours: 0,
      potHours: 0,
      totalHours: 0,
      date: new Date().toLocaleDateString()
    };
    onChange([...entries, newEntry]);
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
    <div className={`overflow-x-auto border rounded-lg ${
      isDarkMode 
        ? 'border-white/20 bg-white/5' 
        : 'border-gray-300 bg-white/80'
    }`}>
      <Table className="min-w-[800px]">
        <TableHeader>
          <TableRow className={`${
            isDarkMode 
              ? 'bg-white/10 border-white/20' 
              : 'bg-gray-50/80 border-gray-200'
          }`}>
            <TableHead className={`text-xs sm:text-sm font-medium min-w-[140px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col">
                <span>Worker Name*</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[80px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>Qty*</span>
                <Info className={`w-3 h-3 mt-1 ${themeClasses.text.muted}`} />
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[70px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>ST</span>
                <span className={`text-xs ${themeClasses.text.secondary}`}>(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[70px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>OT</span>
                <span className={`text-xs ${themeClasses.text.secondary}`}>(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[70px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>DT</span>
                <span className={`text-xs ${themeClasses.text.secondary}`}>(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[70px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>POT</span>
                <span className={`text-xs ${themeClasses.text.secondary}`}>(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[70px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>POT</span>
                <span className={`text-xs ${themeClasses.text.secondary}`}>(Hrs)</span>
              </div>
            </TableHead>
            <TableHead className={`text-xs sm:text-sm font-medium text-center min-w-[80px] ${themeClasses.text.primary}`}>
              <div className="flex flex-col items-center">
                <span>Total</span>
                <span className={`text-xs ${themeClasses.text.secondary}`}>(Hrs)</span>
              </div>
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
          {entries.map((entry) => (
            <TableRow key={entry.id}>
              <TableCell className="p-1">
                <Input
                  value={entry.workerName}
                  onChange={(e) => updateEntry(entry.id, 'workerName', e.target.value)}
                  onBlur={() => {
                    // Auto-save new worker names to the database
                    if (entry.workerName && entry.workerName.trim() && onSaveWorker) {
                      onSaveWorker(entry.workerName.trim());
                    }
                  }}
                  placeholder="Enter worker name"
                  className={`border-0 p-2 h-8 text-xs sm:text-sm min-w-[120px] ${themeClasses.input}`}
                  list={`workers-${entry.id}`}
                />
                <datalist id={`workers-${entry.id}`}>
                  {availableWorkers.map((worker) => (
                    <option key={worker.id} value={worker.name} />
                  ))}
                </datalist>
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
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.stHours}
                  onChange={(e) => updateEntry(entry.id, 'stHours', e.target.value)}
                  className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-14 ${themeClasses.input}`}
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.otHours}
                  onChange={(e) => updateEntry(entry.id, 'otHours', e.target.value)}
                  className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-14 ${themeClasses.input}`}
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.dtHours}
                  onChange={(e) => updateEntry(entry.id, 'dtHours', e.target.value)}
                  className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-14 ${themeClasses.input}`}
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.potHours}
                  onChange={(e) => updateEntry(entry.id, 'potHours', e.target.value)}
                  className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-14 ${themeClasses.input}`}
                  step="0.01"
                />
              </TableCell>
              <TableCell className="p-1">
                <Input
                  type="number"
                  value={entry.potHours}
                  onChange={(e) => updateEntry(entry.id, 'potHours', e.target.value)}
                  className={`border-0 p-2 text-center h-8 text-xs sm:text-sm w-14 ${themeClasses.input}`}
                  step="0.01"
                />
              </TableCell>
              <TableCell className="text-center font-medium text-xs sm:text-sm p-1">
                <div className={`rounded px-2 py-1 ${
                  isDarkMode 
                    ? 'bg-white/10 border border-white/20' 
                    : 'bg-gray-50 border border-gray-200'
                }`}>
                  {entry.totalHours.toFixed(2)}
                </div>
              </TableCell>
              <TableCell className="p-1">
                <Input
                  value={entry.date}
                  onChange={(e) => updateEntry(entry.id, 'date', e.target.value)}
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
          ))}
          
          {/* Totals Row */}
          <TableRow className={`font-medium ${
            isDarkMode 
              ? 'bg-white/10 border-white/20' 
              : 'bg-gray-50/80 border-gray-200'
          }`}>
            <TableCell colSpan={2} className={`text-right ${themeClasses.text.primary}`}>
              Total Labor Hours:
            </TableCell>
            <TableCell className={`text-center ${themeClasses.text.primary}`}>
              {getColumnTotal('stHours')}
            </TableCell>
            <TableCell className={`text-center ${themeClasses.text.primary}`}>
              {getColumnTotal('otHours')}
            </TableCell>
            <TableCell className={`text-center ${themeClasses.text.primary}`}>
              {getColumnTotal('dtHours')}
            </TableCell>
            <TableCell className={`text-center ${themeClasses.text.primary}`}>
              {getColumnTotal('potHours')}
            </TableCell>
            <TableCell className={`text-center ${themeClasses.text.primary}`}>
              {getColumnTotal('potHours')}
            </TableCell>
            <TableCell className={`text-center ${themeClasses.text.primary}`}>
              {getTotalHours()}
            </TableCell>
            <TableCell colSpan={2}></TableCell>
          </TableRow>
        </TableBody>
      </Table>
      
      {/* Add Worker Button */}
      <div className={`p-4 border-t ${
        isDarkMode 
          ? 'border-white/20 bg-white/5' 
          : 'border-gray-200 bg-gray-50/50'
      }`}>
        <Button
          onClick={addEmptyRow}
          className={`w-full ${
            isDarkMode
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Worker
        </Button>
      </div>
    </div>
  );
};

export default LaborTable;