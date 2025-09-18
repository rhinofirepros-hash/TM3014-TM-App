/* eslint-disable no-undef */
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
      
      // Clean Header Section - Logo in top right corner with improved loading
      let headerComplete = false;
      
      // Try to add logo with better error handling
      try {
        const logoUrl = 'https://customer-assets.emergentagent.com/job_b98f6205-b977-4a20-97e0-9a9b9eeea432/artifacts/yzknuiqy_TITLEBLOCKRHINOFIRE1.png';
        
        // Create a canvas to handle CORS issues
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            console.log('❌ Logo loading timeout after 10 seconds');
            reject(new Error('Logo loading timeout'));
          }, 10000); // 10 second timeout
          
          img.onload = function() {
            clearTimeout(timeout);
            try {
              // Draw image to canvas to convert to base64
              canvas.width = img.width;
              canvas.height = img.height;
              ctx.drawImage(img, 0, 0);
              
              // Convert to base64
              const base64 = canvas.toDataURL('image/png');
              
              // Add logo in TOP RIGHT CORNER
              pdf.addImage(base64, 'PNG', 125, 15, 70, 35);
              
              // Add "TIME & MATERIAL TAG" text on left side
              pdf.setTextColor(0, 0, 0);
              pdf.setFontSize(16);
              pdf.setFont(undefined, 'bold');
              pdf.text('TIME & MATERIAL TAG', 15, 32);
              
              console.log('✅ Rhino logo successfully added to PDF header (top right corner)');
              headerComplete = true;
            } catch (imgError) {
              console.error('❌ Logo rendering error:', imgError);
            }
            resolve();
          };
          
          img.onerror = function(error) {
            clearTimeout(timeout);
            console.error('❌ Logo loading failed from URL:', logoUrl, error);
            reject(error);
          };
          
          console.log('🔄 Loading Rhino logo from:', logoUrl);
          img.src = logoUrl;
        });
        
      } catch (error) {
        console.error('❌ Logo loading error:', error);
      }
      
      // Fallback if logo failed - still show professional header
      if (!headerComplete) {
        console.log('⚠️ Logo failed to load, using fallback header');
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(18);
        pdf.setFont(undefined, 'bold');
        pdf.text('RHINO FIRE PROTECTION', 15, 25);
        pdf.setFontSize(16);
        pdf.text('TIME & MATERIAL TAG', 15, 35);
        
        // Add a rectangle where logo would be to maintain layout
        pdf.setDrawColor(200, 200, 200);
        pdf.setLineWidth(1);
        pdf.rect(125, 15, 70, 35);
        pdf.setFontSize(10);
        pdf.setTextColor(150, 150, 150);
        pdf.text('LOGO', 160, 35, { align: 'center' });
        pdf.setTextColor(0, 0, 0);
      }
      
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
      
      if (formData.companyName) {
        yPos += 7;
        pdf.text('Company Name:', 15, yPos);
        pdf.text(formData.companyName, 65, yPos);
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
        
        // Labor table with borders - improved sizing
        pdf.setDrawColor(150, 150, 150);
        pdf.setLineWidth(0.1);
        
        // Labor table headers with better column widths
        pdf.setFontSize(8);
        pdf.rect(15, yPos, 60, 8); // Worker name (wider)
        pdf.rect(75, yPos, 15, 8); // Qty
        pdf.rect(90, yPos, 15, 8); // ST
        pdf.rect(105, yPos, 15, 8); // OT
        pdf.rect(120, yPos, 15, 8); // DT
        pdf.rect(135, yPos, 15, 8); // POT
        pdf.rect(150, yPos, 20, 8); // Total (wider)
        pdf.rect(170, yPos, 25, 8); // Date (wider)
        
        pdf.text('Worker Name', 17, yPos + 5);
        pdf.text('Qty', 78, yPos + 5);
        pdf.text('ST', 95, yPos + 5);
        pdf.text('OT', 110, yPos + 5);
        pdf.text('DT', 125, yPos + 5);
        pdf.text('POT', 140, yPos + 5);
        pdf.text('Total', 155, yPos + 5);
        pdf.text('Date', 175, yPos + 5);
        
        yPos += 8;
        
        // Labor entries with improved sizing
        pdf.setFont(undefined, 'normal');
        formData.laborEntries.forEach((entry) => {
          pdf.rect(15, yPos, 60, 6);
          pdf.rect(75, yPos, 15, 6);
          pdf.rect(90, yPos, 15, 6);
          pdf.rect(105, yPos, 15, 6);
          pdf.rect(120, yPos, 15, 6);
          pdf.rect(135, yPos, 15, 6);
          pdf.rect(150, yPos, 20, 6);
          pdf.rect(170, yPos, 25, 6);
          
          // Truncate long names to fit
          const workerName = (entry.workerName || '').length > 20 ? 
            (entry.workerName || '').substring(0, 20) + '...' : 
            (entry.workerName || '');
          
          pdf.text(workerName, 17, yPos + 4);
          pdf.text(entry.quantity?.toString() || '1', 78, yPos + 4);
          pdf.text(entry.stHours?.toString() || '0', 95, yPos + 4);
          pdf.text(entry.otHours?.toString() || '0', 110, yPos + 4);
          pdf.text(entry.dtHours?.toString() || '0', 125, yPos + 4);
          pdf.text(entry.potHours?.toString() || '0', 140, yPos + 4);
          pdf.text(entry.totalHours?.toString() || '0', 155, yPos + 4);
          pdf.text(entry.date?.substring(0, 10) || '', 175, yPos + 4);
          yPos += 6;
        });
        
        // Labor totals with improved sizing
        const totalHours = formData.laborEntries.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0);
        pdf.setFont(undefined, 'bold');
        pdf.rect(120, yPos, 50, 6);
        pdf.rect(170, yPos, 25, 6);
        pdf.text('TOTAL HOURS:', 125, yPos + 4);
        pdf.text(totalHours.toFixed(2), 175, yPos + 4);
        yPos += 12;
      }
      
      // Materials Section
      if (formData.materialEntries && formData.materialEntries.length > 0) {
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(11);
        pdf.text('MATERIALS', 15, yPos);
        yPos += 6;
        
        // Materials table with improved borders and sizing
        pdf.setFontSize(8);
        pdf.rect(15, yPos, 55, 8); // Material name
        pdf.rect(70, yPos, 25, 8); // Unit
        pdf.rect(95, yPos, 20, 8); // Qty
        pdf.rect(115, yPos, 25, 8); // Unit Cost
        pdf.rect(140, yPos, 25, 8); // Total
        pdf.rect(165, yPos, 30, 8); // Date (wider)
        
        pdf.text('Material Name', 17, yPos + 5);
        pdf.text('Unit', 77, yPos + 5);
        pdf.text('Qty', 100, yPos + 5);
        pdf.text('Unit Cost', 120, yPos + 5);
        pdf.text('Total', 147, yPos + 5);
        pdf.text('Date', 170, yPos + 5);
        
        yPos += 8;
        
        // Material entries with improved sizing
        pdf.setFont(undefined, 'normal');
        let materialTotal = 0;
        formData.materialEntries.forEach((entry) => {
          pdf.rect(15, yPos, 55, 6);
          pdf.rect(70, yPos, 25, 6);
          pdf.rect(95, yPos, 20, 6);
          pdf.rect(115, yPos, 25, 6);
          pdf.rect(140, yPos, 25, 6);
          pdf.rect(165, yPos, 30, 6);
          
          // Truncate long material names
          const materialName = (entry.materialName || '').length > 18 ? 
            (entry.materialName || '').substring(0, 18) + '...' : 
            (entry.materialName || '');
          
          pdf.text(materialName, 17, yPos + 4);
          pdf.text((entry.unitOfMeasure || '').substring(0, 8), 72, yPos + 4);
          pdf.text(entry.quantity?.toString() || '0', 100, yPos + 4);
          pdf.text(`$${entry.unitCost?.toFixed(2) || '0.00'}`, 120, yPos + 4);
          pdf.text(`$${entry.total?.toFixed(2) || '0.00'}`, 147, yPos + 4);
          pdf.text(entry.dateOfWork?.substring(0, 10) || '', 170, yPos + 4);
          materialTotal += parseFloat(entry.total) || 0;
          yPos += 6;
        });
        
        // Material totals with improved sizing
        pdf.setFont(undefined, 'bold');
        pdf.rect(115, yPos, 50, 6);
        pdf.rect(165, yPos, 30, 6);
        pdf.text('TOTAL MATERIALS:', 120, yPos + 4);
        pdf.text(`$${materialTotal.toFixed(2)}`, 170, yPos + 4);
        yPos += 12;
      }

      // Equipment Section
      if (formData.equipmentEntries && formData.equipmentEntries.length > 0) {
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(11);
        pdf.text('EQUIPMENT', 15, yPos);
        yPos += 6;
        
        // Equipment table with borders
        pdf.setFontSize(8);
        pdf.rect(15, yPos, 50, 8); // Equipment name
        pdf.rect(65, yPos, 25, 8); // Pieces
        pdf.rect(90, yPos, 25, 8); // Unit
        pdf.rect(115, yPos, 25, 8); // Qty
        pdf.rect(140, yPos, 25, 8); // Total
        pdf.rect(165, yPos, 30, 8); // Date
        
        pdf.text('Equipment Name', 17, yPos + 5);
        pdf.text('Pieces', 72, yPos + 5);
        pdf.text('Unit', 97, yPos + 5);
        pdf.text('Quantity', 122, yPos + 5);
        pdf.text('Total', 147, yPos + 5);
        pdf.text('Date', 172, yPos + 5);
        
        yPos += 8;
        
        // Equipment entries
        pdf.setFont(undefined, 'normal');
        formData.equipmentEntries.forEach((entry) => {
          pdf.rect(15, yPos, 50, 6);
          pdf.rect(65, yPos, 25, 6);
          pdf.rect(90, yPos, 25, 6);
          pdf.rect(115, yPos, 25, 6);
          pdf.rect(140, yPos, 25, 6);
          pdf.rect(165, yPos, 30, 6);
          
          pdf.text(entry.equipmentName || '', 17, yPos + 4);
          pdf.text(entry.piecesOfEquipment?.toString() || '0', 72, yPos + 4);
          pdf.text(entry.unitOfMeasure || '', 97, yPos + 4);
          pdf.text(entry.quantity?.toString() || '0', 122, yPos + 4);
          pdf.text(entry.total?.toFixed(2) || '0.00', 147, yPos + 4);
          pdf.text(entry.dateOfWork?.substring(0, 8) || '', 172, yPos + 4);
          yPos += 6;
        });
        yPos += 6;
      }

      // Other Section
      if (formData.otherEntries && formData.otherEntries.length > 0) {
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(11);
        pdf.text('OTHER', 15, yPos);
        yPos += 6;
        
        // Other table with borders
        pdf.setFontSize(8);
        pdf.rect(15, yPos, 50, 8); // Other name
        pdf.rect(65, yPos, 25, 8); // Qty of Other
        pdf.rect(90, yPos, 25, 8); // Unit
        pdf.rect(115, yPos, 25, 8); // Qty of Unit
        pdf.rect(140, yPos, 25, 8); // Total
        pdf.rect(165, yPos, 30, 8); // Date
        
        pdf.text('Other Name', 17, yPos + 5);
        pdf.text('Qty Other', 72, yPos + 5);
        pdf.text('Unit', 97, yPos + 5);
        pdf.text('Qty Unit', 122, yPos + 5);
        pdf.text('Total', 147, yPos + 5);
        pdf.text('Date', 172, yPos + 5);
        
        yPos += 8;
        
        // Other entries
        pdf.setFont(undefined, 'normal');
        formData.otherEntries.forEach((entry) => {
          pdf.rect(15, yPos, 50, 6);
          pdf.rect(65, yPos, 25, 6);
          pdf.rect(90, yPos, 25, 6);
          pdf.rect(115, yPos, 25, 6);
          pdf.rect(140, yPos, 25, 6);
          pdf.rect(165, yPos, 30, 6);
          
          pdf.text(entry.otherName || '', 17, yPos + 4);
          pdf.text(entry.quantityOfOther?.toString() || '0', 72, yPos + 4);
          pdf.text(entry.unitOfMeasure || '', 97, yPos + 4);
          pdf.text(entry.quantityOfUnit?.toString() || '0', 122, yPos + 4);
          pdf.text(entry.total?.toFixed(2) || '0.00', 147, yPos + 4);
          pdf.text(entry.dateOfWork?.substring(0, 8) || '', 172, yPos + 4);
          yPos += 6;
        });
        yPos += 6;
      }
      
      // Signature section
      yPos += 10;
      pdf.setFont(undefined, 'bold');
      pdf.setFontSize(10);
      
      // Signature boxes like ClearStory - improved sizing
      pdf.rect(15, yPos, 90, 25); // Foreman signature box (taller for signature)
      pdf.rect(110, yPos, 85, 25); // Date box
      
      pdf.text('FOREMAN SIGNATURE:', 17, yPos + 5);
      pdf.text('DATE:', 112, yPos + 5);
      
      // Add signature if available
      if (formData.signature) {
        try {
          // Add actual signature image
          pdf.addImage(formData.signature, 'PNG', 17, yPos + 7, 70, 15);
        } catch (error) {
          console.error('Error adding signature to PDF:', error);
          pdf.setFontSize(8);
          pdf.text('(Digital signature captured)', 17, yPos + 15);
        }
      }
      
      pdf.text(new Date().toLocaleDateString(), 112, yPos + 15);
      
      yPos += 30;
      
      // Foreman print name section - add signer name if available
      pdf.rect(15, yPos, 180, 15); // Full width for foreman name
      pdf.text('FOREMAN PRINT NAME:', 17, yPos + 8);
      
      if (formData.signerName) {
        pdf.setFont(undefined, 'normal');
        pdf.setFontSize(9);
        pdf.text(formData.signerName, 17, yPos + 12);
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(10);
      }
      
      yPos += 20;
      
      // Company representative signature section - much larger
      pdf.setFontSize(10);
      pdf.rect(15, yPos, 90, 20); // Company signature box (same size as foreman)
      pdf.rect(110, yPos, 85, 20); // Company date box
      
      pdf.text('COMPANY REPRESENTATIVE SIGNATURE:', 17, yPos + 5);
      pdf.text('COMPANY DATE:', 112, yPos + 5);
      
      yPos += 25;
      
      // Company representative print name - larger
      pdf.rect(15, yPos, 180, 15); // Full width for company name
      pdf.text('COMPANY REPRESENTATIVE PRINT NAME:', 17, yPos + 8);
      
      yPos += 15;
      
      // Footer with professional styling and logo
      pdf.setDrawColor(0, 0, 0);
      pdf.setLineWidth(0.5);
      pdf.line(15, yPos, 195, yPos);
      
      yPos += 10;
      
      // Add footer logo and text with improved loading
      try {
        const footerLogoUrl = 'https://customer-assets.emergentagent.com/job_b98f6205-b977-4a20-97e0-9a9b9eeea432/artifacts/yzknuqy_TITLEBLOCKRHINOFIRE1.png';
        
        // Use the same canvas approach for consistency
        const footerCanvas = document.createElement('canvas');
        const footerCtx = footerCanvas.getContext('2d');
        const footerImg = new Image();
        footerImg.crossOrigin = 'anonymous';
        
        await new Promise((resolve) => {
          const footerTimeout = setTimeout(() => {
            console.log('⚠️ Footer logo loading timeout, using fallback');
            resolve();
          }, 5000);
          
          footerImg.onload = function() {
            clearTimeout(footerTimeout);
            try {
              // Draw to canvas and convert to base64
              footerCanvas.width = footerImg.width;
              footerCanvas.height = footerImg.height;
              footerCtx.drawImage(footerImg, 0, 0);
              const footerBase64 = footerCanvas.toDataURL('image/png');
              
              // Add small logo in footer
              pdf.addImage(footerBase64, 'PNG', 15, yPos - 5, 25, 12);
              
              // Footer text next to logo
              pdf.setTextColor(0, 0, 0);
              pdf.setFontSize(10);
              pdf.setFont(undefined, 'bold');
              pdf.text('RHINO FIRE PROTECTION T&M TAG APP', 50, yPos + 2);
              
              console.log('✅ Footer logo added successfully');
            } catch (logoError) {
              console.log('❌ Footer logo error:', logoError);
              // Fallback text only
              pdf.setTextColor(0, 0, 0);
              pdf.setFontSize(10);
              pdf.setFont(undefined, 'bold');
              pdf.text('RHINO FIRE PROTECTION T&M TAG APP', 105, yPos + 2, { align: 'center' });
            }
            resolve();
          };
          
          footerImg.onerror = function() {
            clearTimeout(footerTimeout);
            console.log('❌ Footer logo loading failed, using fallback text');
            // Fallback text only
            pdf.setTextColor(0, 0, 0);
            pdf.setFontSize(10);
            pdf.setFont(undefined, 'bold');
            pdf.text('RHINO FIRE PROTECTION T&M TAG APP', 105, yPos + 2, { align: 'center' });
            resolve();
          };
          
          footerImg.src = footerLogoUrl;
        });
        
      } catch (error) {
        console.log('❌ Footer logo loading error:', error);
        // Fallback text only
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(10);
        pdf.setFont(undefined, 'bold');
        pdf.text('RHINO FIRE PROTECTION T&M TAG APP', 105, yPos + 2, { align: 'center' });
      }
      
      // Save/download with single method to prevent duplicates
      const dateStr = formData.dateOfWork?.toISOString().split('T')[0].replace(/-/g, '');
      const filename = `TM_Tag_${dateStr}.pdf`;
      
      try {
        // Use blob URL method for reliable download
        const pdfBlob = pdf.output('blob');
        const blobUrl = URL.createObjectURL(pdfBlob);
        
        // Create download link and trigger download
        const downloadLink = document.createElement('a');
        downloadLink.href = blobUrl;
        downloadLink.download = filename;
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        // Clean up the blob URL after a short delay
        setTimeout(() => {
          URL.revokeObjectURL(blobUrl);
        }, 1000);
        
        console.log(`✅ PDF download initiated: ${filename}`);
        
      } catch (downloadError) {
        console.error('Download error:', downloadError);
        
        // Fallback: Open PDF in new tab
        const pdfDataUri = pdf.output('datauristring');
        const newWindow = window.open();
        if (newWindow) {
          newWindow.document.write(`
            <html>
              <head><title>${filename}</title></head>
              <body style="margin:0;">
                <embed src="${pdfDataUri}" type="application/pdf" width="100%" height="100%" />
              </body>
            </html>
          `);
        } else {
          alert('Please allow popups to view the PDF, or check your downloads folder for the file.');
        }
      }
      
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