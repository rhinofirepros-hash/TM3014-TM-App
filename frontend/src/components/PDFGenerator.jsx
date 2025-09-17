import React from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const PDFGenerator = ({ formData, onGenerate }) => {
  const generatePDF = async () => {
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // Add border and professional layout
      pdf.setDrawColor(0, 0, 0);
      pdf.setLineWidth(0.5);
      pdf.rect(10, 10, 190, 277); // Outer border
      
      // Header section with logo space
      pdf.setFillColor(240, 240, 240);
      pdf.rect(15, 15, 180, 25, 'F');
      
      // Company Header
      pdf.setFontSize(18);
      pdf.setFont(undefined, 'bold');
      pdf.text('RHINO FIRE PROTECTION', 105, 25, { align: 'center' });
      pdf.setFontSize(14);
      pdf.text('TIME & MATERIAL TAG', 105, 32, { align: 'center' });
      
      // Add logo placeholder (you can replace this with actual logo loading)
      pdf.setDrawColor(100, 100, 100);
      pdf.setLineWidth(0.2);
      pdf.rect(170, 17, 20, 20); // Logo placeholder
      pdf.setFontSize(8);
      pdf.text('LOGO', 180, 28, { align: 'center' });
      
      // Project Information Section
      let yPos = 50;
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text('PROJECT INFORMATION', 15, yPos);
      
      yPos += 8;
      pdf.setFont(undefined, 'normal');
      pdf.setFontSize(10);
      
      // Create form-like layout
      pdf.text('Project Name:', 15, yPos);
      pdf.text(formData.projectName || '', 50, yPos);
      pdf.text('Cost Code:', 120, yPos);
      pdf.text(formData.costCode || '', 145, yPos);
      
      yPos += 7;
      pdf.text('Date of Work:', 15, yPos);
      pdf.text(formData.dateOfWork ? formData.dateOfWork.toLocaleDateString() : '', 50, yPos);
      pdf.text('Foreman:', 120, yPos);
      pdf.text('Jesus Garcia', 145, yPos);
      
      yPos += 7;
      pdf.text('T&M Tag Title:', 15, yPos);
      const titleText = pdf.splitTextToSize(formData.tmTagTitle || '', 110);
      pdf.text(titleText, 50, yPos);
      
      if (formData.customerReference) {
        yPos += 7;
        pdf.text('Customer Reference:', 15, yPos);
        pdf.text(formData.customerReference, 65, yPos);
      }
      
      // Description of Work
      yPos += 12;
      pdf.setFont(undefined, 'bold');
      pdf.text('DESCRIPTION OF WORK:', 15, yPos);
      yPos += 6;
      pdf.setFont(undefined, 'normal');
      
      const description = formData.descriptionOfWork || '';
      const splitDescription = pdf.splitTextToSize(description, 170);
      pdf.text(splitDescription, 15, yPos);
      
      yPos += (splitDescription.length * 4) + 10;
      
      // Labor Section
      if (formData.laborEntries && formData.laborEntries.length > 0) {
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(11);
        pdf.text('LABOR', 15, yPos);
        yPos += 6;
        
        // Labor table with borders
        pdf.setDrawColor(150, 150, 150);
        pdf.setLineWidth(0.1);
        
        // Labor table headers
        pdf.setFontSize(8);
        pdf.rect(15, yPos, 50, 8); // Worker name
        pdf.rect(65, yPos, 20, 8); // Qty
        pdf.rect(85, yPos, 20, 8); // ST
        pdf.rect(105, yPos, 20, 8); // OT
        pdf.rect(125, yPos, 20, 8); // DT
        pdf.rect(145, yPos, 20, 8); // POT
        pdf.rect(165, yPos, 20, 8); // Total
        pdf.rect(185, yPos, 10, 8); // Date (shorter)
        
        pdf.text('Worker Name', 17, yPos + 5);
        pdf.text('Qty', 72, yPos + 5);
        pdf.text('ST', 92, yPos + 5);
        pdf.text('OT', 112, yPos + 5);
        pdf.text('DT', 132, yPos + 5);
        pdf.text('POT', 152, yPos + 5);
        pdf.text('Total', 170, yPos + 5);
        pdf.text('Date', 187, yPos + 5);
        
        yPos += 8;
        
        // Labor entries
        pdf.setFont(undefined, 'normal');
        formData.laborEntries.forEach((entry) => {
          pdf.rect(15, yPos, 50, 6);
          pdf.rect(65, yPos, 20, 6);
          pdf.rect(85, yPos, 20, 6);
          pdf.rect(105, yPos, 20, 6);
          pdf.rect(125, yPos, 20, 6);
          pdf.rect(145, yPos, 20, 6);
          pdf.rect(165, yPos, 20, 6);
          pdf.rect(185, yPos, 10, 6);
          
          pdf.text(entry.workerName || '', 17, yPos + 4);
          pdf.text(entry.quantity?.toString() || '1', 72, yPos + 4);
          pdf.text(entry.stHours?.toString() || '0', 92, yPos + 4);
          pdf.text(entry.otHours?.toString() || '0', 112, yPos + 4);
          pdf.text(entry.dtHours?.toString() || '0', 132, yPos + 4);
          pdf.text(entry.potHours?.toString() || '0', 152, yPos + 4);
          pdf.text(entry.totalHours?.toString() || '0', 170, yPos + 4);
          pdf.text(entry.date?.substring(0, 8) || '', 187, yPos + 4);
          yPos += 6;
        });
        
        // Labor totals
        const totalHours = formData.laborEntries.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0);
        pdf.setFont(undefined, 'bold');
        pdf.rect(145, yPos, 40, 6);
        pdf.text('TOTAL HOURS:', 147, yPos + 4);
        pdf.text(totalHours.toFixed(2), 170, yPos + 4);
        yPos += 12;
      }
      
      // Materials Section
      if (formData.materialEntries && formData.materialEntries.length > 0) {
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(12);
        pdf.text('MATERIALS:', 20, yPos);
        yPos += 10;
        
        // Materials table headers
        pdf.setFontSize(10);
        pdf.text('Material', 20, yPos);
        pdf.text('Unit', 80, yPos);
        pdf.text('Qty', 110, yPos);
        pdf.text('Unit Cost', 130, yPos);
        pdf.text('Total', 160, yPos);
        pdf.text('Date', 180, yPos);
        
        yPos += 5;
        pdf.line(20, yPos, 200, yPos);
        yPos += 5;
        
        // Material entries
        pdf.setFont(undefined, 'normal');
        let materialTotal = 0;
        formData.materialEntries.forEach((entry) => {
          pdf.text(entry.materialName || '', 20, yPos);
          pdf.text(entry.unitOfMeasure || '', 80, yPos);
          pdf.text(entry.quantity?.toString() || '0', 110, yPos);
          pdf.text(`$${entry.unitCost?.toFixed(2) || '0.00'}`, 130, yPos);
          pdf.text(`$${entry.total?.toFixed(2) || '0.00'}`, 160, yPos);
          pdf.text(entry.dateOfWork || '', 180, yPos);
          materialTotal += parseFloat(entry.total) || 0;
          yPos += 5;
        });
        
        // Material totals
        pdf.line(20, yPos, 200, yPos);
        yPos += 5;
        pdf.setFont(undefined, 'bold');
        pdf.text('TOTAL MATERIALS:', 120, yPos);
        pdf.text(`$${materialTotal.toFixed(2)}`, 160, yPos);
        yPos += 15;
      }
      
      // Signature section
      yPos += 10;
      pdf.setFont(undefined, 'bold');
      pdf.text('FOREMAN SIGNATURE:', 20, yPos);
      pdf.line(80, yPos, 150, yPos); // Signature line
      yPos += 15;
      
      pdf.text('DATE:', 20, yPos);
      pdf.line(40, yPos, 80, yPos); // Date line
      
      // Footer
      pdf.setFontSize(8);
      pdf.setFont(undefined, 'normal');
      pdf.text('Generated by TM3014 T&M Daily Tag App - Rhino Fire Protection', 105, 280, { align: 'center' });
      
      // Generate filename with date
      const dateStr = formData.dateOfWork ? 
        formData.dateOfWork.toISOString().split('T')[0].replace(/-/g, '') : 
        new Date().toISOString().split('T')[0].replace(/-/g, '');
      const filename = `TM_Tag_${dateStr}.pdf`;
      
      // Save the PDF
      pdf.save(filename);
      
      if (onGenerate) {
        onGenerate({ success: true, filename });
      }
      
      return { success: true, filename, pdfData: pdf.output('datauristring') };
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      if (onGenerate) {
        onGenerate({ success: false, error: error.message });
      }
      return { success: false, error: error.message };
    }
  };

  return { generatePDF };
};

export default PDFGenerator;