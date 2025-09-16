# T&M Daily Tag App - Backend Integration Contracts

## Overview
This document outlines the API contracts and integration plan for the Time & Material Daily Tag application for Rhino Fire Protection.

## API Endpoints Required

### 1. Projects Management
```
GET /api/projects
- Returns list of available projects
- Response: [{ id, name, status, created_at }]

POST /api/projects
- Create new project (admin only)
- Body: { name, description, cost_codes[] }
```

### 2. T&M Tags CRUD Operations
```
POST /api/tm-tags
- Create new T&M tag
- Body: TMTagCreate schema (see below)
- Response: TMTag with generated ID

GET /api/tm-tags
- List all T&M tags with pagination
- Query params: ?page=1&limit=10&project_id=xxx

GET /api/tm-tags/{id}
- Get specific T&M tag by ID
- Response: Complete TMTag object

PUT /api/tm-tags/{id}
- Update existing T&M tag
- Body: TMTagUpdate schema

DELETE /api/tm-tags/{id}
- Soft delete T&M tag
```

### 3. PDF Generation & Email
```
POST /api/tm-tags/{id}/generate-pdf
- Generate PDF for specific T&M tag
- Response: { pdf_url, filename }

POST /api/tm-tags/{id}/email-gc
- Email PDF to General Contractor
- Body: { recipient_email, message? }
- Uses: iacosta@nueragroup.com as default
```

### 4. Workers Management
```
GET /api/workers
- Get list of workers (preloaded with Jesus Garcia)
- Response: [{ id, name, rate, active }]

POST /api/workers
- Add new worker
- Body: { name, rate, active }
```

## Data Models

### TMTag Schema
```typescript
interface TMTag {
  id: string
  project_name: string
  cost_code: string
  date_of_work: Date
  customer_reference?: string
  tm_tag_title: string
  description_of_work: string
  labor_entries: LaborEntry[]
  material_entries: MaterialEntry[]
  signature?: string  // base64 image
  foreman_name: string
  status: 'draft' | 'completed' | 'submitted'
  created_at: Date
  updated_at: Date
  submitted_at?: Date
}

interface LaborEntry {
  id: string
  worker_name: string
  quantity: number
  st_hours: number    // Standard Time hours
  ot_hours: number    // Overtime hours
  dt_hours: number    // Double Time hours
  pot_hours: number   // Penalty Overtime hours
  total_hours: number
  date: string
  hourly_rate: number // Default: 95
}

interface MaterialEntry {
  id: string
  material_name: string
  unit_of_measure: string
  quantity: number
  unit_cost?: number
  total: number
  date_of_work: string
}
```

## Mock Data Currently Used (Frontend)

### Projects
- "Third Ave. Apartments" (primary)
- "Downtown Office Complex"
- "Residential Phase 2"

### Workers
- Jesus Garcia (rate: $95/hr) - Primary foreman
- Mike Rodriguez, Sarah Johnson, Tom Wilson

### Default Values
- Cost Code: "FP-Install"
- Default hours: 8.00 ST hours
- Rate locked at $95/hr

## Frontend-Backend Integration Points

### Current Mock Data Replacement
1. **Replace** `mockData.projects` with API call to `/api/projects`
2. **Replace** `mockData.workers` with API call to `/api/workers`
3. **Replace** localStorage draft saving with `/api/tm-tags` POST/PUT
4. **Integrate** PDF generation with backend `/api/tm-tags/{id}/generate-pdf`
5. **Implement** email functionality via `/api/tm-tags/{id}/email-gc`

### Form Submission Flow
1. User fills form and adds labor/materials
2. Click "Collect Signatures" → Signature captured locally
3. Click "Submit & Email GC" → 
   - POST to `/api/tm-tags` with complete data
   - Auto-generate PDF on backend
   - Auto-email to iacosta@nueragroup.com
   - Show success message with PDF filename

### Email Integration
- **Service**: EmailJS integration (as specified in requirements)
- **Recipient**: iacosta@nueragroup.com
- **Subject**: "T&M Tag - {date} - 3rd Avenue"
- **Body**: "Attached is today's T&M tag for the 3rd Avenue project."
- **Attachment**: Generated PDF

## Backend Implementation Priority

### Phase 1: Core CRUD (Essential)
1. MongoDB models for TMTag, LaborEntry, MaterialEntry
2. Basic CRUD endpoints for T&M tags
3. Projects and Workers endpoints
4. Form validation

### Phase 2: PDF & Email (High Priority)
1. PDF generation using jsPDF on backend
2. EmailJS integration for GC notification
3. File storage for generated PDFs

### Phase 3: Enhancements (Future)
1. User authentication (Jesus Garcia login)
2. Reporting dashboard
3. Google Drive integration (optional)
4. Mobile app optimization

## Environment Variables Needed
```env
# Email Configuration
EMAILJS_SERVICE_ID=your_service_id
EMAILJS_TEMPLATE_ID=your_template_id
EMAILJS_PUBLIC_KEY=your_public_key

# Default Settings
DEFAULT_GC_EMAIL=iacosta@nueragroup.com
DEFAULT_HOURLY_RATE=95
COMPANY_NAME="Rhino Fire Protection"
```

## Testing Requirements
1. End-to-end form submission with PDF generation
2. Email delivery testing
3. Signature capture and storage
4. Data persistence and retrieval
5. Mobile responsiveness testing