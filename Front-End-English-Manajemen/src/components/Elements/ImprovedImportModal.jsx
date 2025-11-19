// src/components/Elements/ImprovedImportModal.jsx
import React, { useState, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
  LinearProgress,
  Chip,
  Stack,
  IconButton,
  Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import InfoIcon from '@mui/icons-material/Info';
import CloseIcon from '@mui/icons-material/Close';
import Swal from 'sweetalert2';

const ImprovedImportModal = ({ 
  open, 
  onClose, 
  onFileUpload, 
  uploadLabel = "Import File",
  materialType = "Material",
  acceptedFileTypes = ".xlsx,.csv",
  maxFileSizeMB = 10,
  templateService = null,
  onShowInstructions,
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    const fileExtension = file.name.toLowerCase().split('.').pop();
    const allowedExtensions = acceptedFileTypes.split(',').map(ext => ext.replace('.', '').trim());
    
    if (!allowedExtensions.includes(fileExtension)) {
      Swal.fire("Invalid File", `Please select a valid file type: ${acceptedFileTypes}`, "error");
      return;
    }

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxFileSizeMB) {
      Swal.fire("File Too Large", `File size must not exceed ${maxFileSizeMB}MB. Current size: ${fileSizeMB.toFixed(2)}MB`, "error");
      return;
    }

    setSelectedFile(file);
  };

  const handleFileInputChange = (event) => {
    const file = event.target.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const file = event.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      Swal.fire("No File Selected", 'Please select a file first', "warning");
      return;
    }

    setUploading(true);
    try {
      await onFileUpload(selectedFile);
    } catch (error) {
      console.error('Upload error:', error);
      Swal.fire("Upload Failed", error.message || "Failed to upload file", "error");
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    if (!templateService) {
      if(onShowInstructions) onShowInstructions();
      return;
    }
  
    try {
      const response = await templateService();
      const blob = response.data;

      if (blob.type.includes('application/json')) {
        const errorText = await blob.text();
        const errorJson = JSON.parse(errorText);
        throw new Error(errorJson.detail || errorJson.message || "Server failed to generate the template.");
      }
  
      const defaultFileName = `${materialType.toLowerCase().replace(/\s+/g, '_')}_template.xlsx`;
      let fileName = defaultFileName;
      
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename[*]?=['"]?([^'";\n]+)['"]?/);
        if (fileNameMatch && fileNameMatch.length > 1) {
          fileName = fileNameMatch[1];
        }
      }
  
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
  
      Swal.fire({
        title: "Template Downloaded",
        text: "The template has been downloaded successfully!",
        icon: "success",
        timer: 2000,
        showConfirmButton: false
      });
  
    } catch (error) {
      console.error('Template download error:', error);
      Swal.fire("Download Failed", error.message || "Could not download template from the server. Please try again.", "error");
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setUploading(false);
    setDragOver(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onClose();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{ sx: { minHeight: 400 } }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" fontWeight={600}>{uploadLabel}</Typography>
          <IconButton onClick={handleClose} size="small"><CloseIcon /></IconButton>
        </Box>
        <Typography variant="body2" color="text.secondary">Import {materialType.toLowerCase()} from Excel or CSV file</Typography>
      </DialogTitle>

      <DialogContent>
        <Box mb={3}>
          <Typography variant="subtitle2" gutterBottom fontWeight={600}>Step 1: Download Template</Typography>
          <Alert severity="info" sx={{ mb: 2 }}>Download the template first to ensure your data is in the correct format.</Alert>
          <Stack direction="row" spacing={2}>
            <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={handleDownloadTemplate} size="small">Download Template</Button>
            {onShowInstructions && (
              <Button variant="text" startIcon={<InfoIcon />} onClick={onShowInstructions} size="small">View Instructions</Button>
            )}
          </Stack>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box>
          <Typography variant="subtitle2" gutterBottom fontWeight={600}>Step 2: Upload Your File</Typography>
          <Box
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: 2, borderColor: dragOver ? 'primary.main' : 'grey.300', borderStyle: 'dashed', borderRadius: 2, p: 4,
              textAlign: 'center', cursor: 'pointer', backgroundColor: dragOver ? 'primary.50' : 'grey.50',
              transition: 'all 0.2s ease', '&:hover': { borderColor: 'primary.main', backgroundColor: 'primary.50' }
            }}
          >
            <CloudUploadIcon sx={{ fontSize: 48, color: dragOver ? 'primary.main' : 'grey.400', mb: 1 }} />
            <Typography variant="body1" gutterBottom>{dragOver ? 'Drop your file here' : 'Drag & drop your file here'}</Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>or click to browse files</Typography>
            <Typography variant="caption" color="text.secondary">Supported formats: {acceptedFileTypes} (Max {maxFileSizeMB}MB)</Typography>
          </Box>
          <input ref={fileInputRef} type="file" accept={acceptedFileTypes} onChange={handleFileInputChange} style={{ display: 'none' }} />
          {selectedFile && (
            <Box mt={2}>
              <Alert severity="success">
                <Typography variant="body2" fontWeight={600}>Selected File:</Typography>
                <Box display="flex" alignItems="center" gap={1} mt={1}>
                  <Typography variant="body2">{selectedFile.name}</Typography>
                  <Chip label={formatFileSize(selectedFile.size)} size="small" color="primary" />
                </Box>
              </Alert>
            </Box>
          )}
          {uploading && (
            <Box mt={2}>
              <Typography variant="body2" gutterBottom>Uploading file...</Typography>
              <LinearProgress />
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={handleClose} disabled={uploading}>Cancel</Button>
        <Button variant="contained" onClick={handleUpload} disabled={!selectedFile || uploading} startIcon={<CloudUploadIcon />}>
          {uploading ? 'Uploading...' : 'Upload & Import'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImprovedImportModal;