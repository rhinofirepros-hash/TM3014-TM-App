export const mockData = {
  projects: [
    { id: 1, name: "Third Ave. Apartments" },
    { id: 2, name: "Downtown Office Complex" },
    { id: 3, name: "Residential Phase 2" },
    { id: 4, name: "Commercial Plaza" },
    { id: 5, name: "Medical Center East" }
  ],
  
  workers: [
    { id: 1, name: "Jesus Garcia", rate: 95 },
    { id: 2, name: "Mike Rodriguez", rate: 95 },
    { id: 3, name: "Sarah Johnson", rate: 85 },
    { id: 4, name: "Tom Wilson", rate: 90 }
  ],

  laborEntries: [
    {
      id: 1,
      workerName: "Jesus Garcia",
      quantity: 1.00,
      stHours: 8.00,
      otHours: 0,
      dtHours: 0,
      potHours: 0,
      totalHours: 8.00,
      date: "09/17/2025"
    }
  ],

  materialEntries: [],

  costCodes: [
    "FP-Install",
    "FP-Rough",
    "FP-Test",
    "FP-Finish",
    "General"
  ],

  unitsOfMeasure: [
    "Each",
    "Foot",
    "Linear Foot",
    "Square Foot",
    "Gallon",
    "Pound",
    "Box",
    "Roll"
  ]
};