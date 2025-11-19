// src/components/Elements/ImportDialog.jsx - ENHANCED IMPORT DIALOG COMPONENT
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Grid,
  IconButton,
  Collapse,
  Step,
  Stepper,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Download as DownloadIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon,
  InsertDriveFile as FileIcon,
  Description as TemplateIcon
} from '@mui/icons-material';
import { materialService } from '../../services/materialService';

const ImportDialog = ({ 
  open, 
  onClose, 
  materialType, 
  onImportSuccess,
  title = "Import Material"
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [showErrors, setShowErrors] = useState(false);
  const [validationInfo, setValidationInfo] = useState(null);
  const fileInputRef = useRef(null);

  const steps = [
    'Download Template',
    'Prepare Data',
    'Upload File',
    'Review Results'
  ];

  const materialTypeConfig = {
    'phoneme-material': {
      templateEndpoint: materialService.getPhonemeWordTemplate,
      importEndpoint: materialService.importPhonemeWordMaterial,
      fileName: 'phoneme_material_template.xlsx',
      description: 'Import phoneme words with categories, meanings, and transcriptions',
      requiredColumns: ['kategori', 'kata', 'fonem', 'arti', 'definisi'],
      rules: [
        'Category must be a single phoneme (e.g., i, ɪ, p, b)',
        'Phoneme transcription must contain the category phoneme',
        'All columns are required',
        'One row = one word'
      ]
    },
    'exercise-phoneme': {
      templateEndpoint: materialService.getExercisePhonemeTemplate,
      importEndpoint: materialService.importPhonemeSentenceMaterial,
      fileName: 'exercise_phoneme_template.xlsx',
      description: 'Import exercise sentences for similar phonemes training',
      requiredColumns: ['kategori', 'kalimat', 'fonem'],
      rules: [
        'Category must be similar phonemes (e.g., i-ɪ, p-b, ə-ʌ-ɚ)',
        'Sentences must contain at least 10 words',
        'Phoneme transcription must contain ALL category phonemes',
        'One row = one practice sentence'
      ]
    },
    'exam-phoneme': {
      templateEndpoint: materialService.getExamPhonemeTemplate,
      importEndpoint: materialService.importPhonemeExamMaterial,
      fileName: 'exam_phoneme_template.xlsx',
      description: 'Import exam sets with exactly 10 sentences each',
      requiredColumns: ['kategori', 'kalimat_1 to kalimat_10', 'fonem_1 to fonem_10'],
      rules: [
        'Category must be similar phonemes (e.g., i-ɪ, p-b, ə-ʌ-ɚ)',
        'Each exam must have exactly 10 sentences',
        'Each sentence must contain at least 10 words',
        'All phoneme transcriptions must contain ALL category phonemes',
        'One row = one complete exam set'
      ]
    },
    'interview-questions': {
      templateEndpoint: materialService.getInterviewQuestionsTemplate,
      importEndpoint: materialService.importInterviewQuestionsMaterial,
      fileName: 'interview_questions_template.xlsx',
      description: 'Import interview questions for talent assessment',
      requiredColumns: ['pertanyaan'],
      rules: [
        'Questions must contain at least 5 words',
        'Use clear English language',
        'Avoid overly personal questions',
        'One row = one interview question'
      ]
    }
  };

  const currentConfig = materialTypeConfig[materialType] || {};

  const handleDownloadTemplate = async () => {
    if (!currentConfig.templateEndpoint) {
      alert('Template not available for this material type');
      return;
    }

    setDownloadingTemplate(true);
    try {
      const response = await currentConfig.templateEndpoint();
      
      if (response.data?.downloadUrl) {
        // If backend provides download URL
        const link = document.createElement('a');
        link.href = response.data.downloadUrl;
        link.download = response.data.fileName || currentConfig.fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Fallback: generate client-side template
        generateFallbackTemplate();
      }
      
      setActiveStep(1);
      setValidationInfo(response.data?.templateInfo);
    } catch (error) {
      console.error('Download template error:', error);
      generateFallbackTemplate();
    } finally {
      setDownloadingTemplate(false);
    }
  };

  const generateFallbackTemplate = () => {
    // Generate a basic CSV template as fallback
    const headers = currentConfig.requiredColumns;
    let csvContent = headers.join(',') + '\n';
    
    // Add example row based on material type
    if (materialType === 'phoneme-material') {
      csvContent += 'i,beat,biːt,mengalahkan,to strike repeatedly\n';
      csvContent += 'ɪ,bit,bɪt,sedikit,a small piece or amount\n';
    } else if (materialType === 'exercise-phoneme') {
      csvContent += 'i-ɪ,"The team will beat everyone in this incredible bit of championship game today.",tiːm wɪl biːt ˈɛvrɪwʌn ɪn ðɪs ɪnˈkrɛdəbəl bɪt əv ˈtʃæmpɪənʃɪp geɪm təˈdeɪ\n';
    } else if (materialType === 'interview-questions') {
      csvContent += '"Tell me about yourself and your background in detail."\n';
      csvContent += '"What are your greatest strengths and how do they help you?"\n';
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = currentConfig.fileName.replace('.xlsx', '.csv');
    link.click();
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/csv'
      ];
      
      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
        alert('Please select a valid Excel (.xlsx, .xls) or CSV file');
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must not exceed 10MB');
        return;
      }
      
      setSelectedFile(file);
      setActiveStep(2);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile || !currentConfig.importEndpoint) {
      return;
    }

    setUploading(true);
    setImportResult(null);

    try {
      const result = await currentConfig.importEndpoint(selectedFile);
      
      setImportResult({
        success: true,
        data: result.data,
        message: result.message
      });
      
      setActiveStep(3);
      
      if (onImportSuccess) {
        onImportSuccess(result.data);
      }
    } catch (error) {
      console.error('Import error:', error);
      setImportResult({
        success: false,
        message: error.response?.data?.message || error.message || 'Import failed',
        data: error.response?.data?.data || null
      });
      setActiveStep(3);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setSelectedFile(null);
    setImportResult(null);
    setShowErrors(false);
    setValidationInfo(null);
    onClose();
  };

  const getStepIcon = (stepIndex) => {
    if (stepIndex < activeStep) {
      return <SuccessIcon color="success" />;
    }
    if (stepIndex === activeStep) {
      return <InfoIcon color="primary" />;
    }
    return <InfoIcon color="disabled" />;
  };

  const renderStepContent = (stepIndex) => {
    switch (stepIndex) {
      case 0:
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              Download the template file to ensure your data is formatted correctly.
            </Alert>
            <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
              <Typography variant="subtitle2" gutterBottom>
                <TemplateIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Template Information
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {currentConfig.description}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  Required Columns:
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
                  {currentConfig.requiredColumns?.map((col, index) => (
                    <Chip key={index} label={col} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
            </Paper>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadTemplate}
              disabled={downloadingTemplate}
              fullWidth
              sx={{ mb: 1 }}
            >
              {downloadingTemplate ? 'Downloading...' : 'Download Template'}
            </Button>
            {downloadingTemplate && <LinearProgress sx={{ mt: 1 }} />}
          </Box>
        );

      case 1:
        return (
          <Box>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Please prepare your data according to the template format before uploading.
            </Alert>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle2">Import Rules & Guidelines</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {currentConfig.rules?.map((rule, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <InfoIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={rule}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>

            {validationInfo && (
              <Accordion sx={{ mt: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle2">Column Descriptions</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {Object.entries(validationInfo.columnDescriptions || {}).map(([col, desc]) => (
                      <ListItem key={col}>
                        <ListItemText 
                          primary={col}
                          secondary={desc}
                          primaryTypographyProps={{ variant: 'body2', fontWeight: 600 }}
                          secondaryTypographyProps={{ variant: 'caption' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            <Box sx={{ mt: 2 }}>
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={() => fileInputRef.current?.click()}
                fullWidth
              >
                Select File to Upload
              </Button>
            </Box>
          </Box>
        );

      case 2:
        return (
          <Box>
            {selectedFile && (
              <Paper sx={{ p: 2, mb: 2, bgcolor: 'success.50' }}>
                <Box display="flex" alignItems="center" gap={2}>
                  <FileIcon color="success" />
                  <Box flex={1}>
                    <Typography variant="subtitle2" color="success.main">
                      {selectedFile.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            )}
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Ready to import your data. This process will validate and add your materials to the system.
            </Alert>

            <Button
              variant="contained"
              onClick={handleFileUpload}
              disabled={uploading || !selectedFile}
              fullWidth
              startIcon={<UploadIcon />}
            >
              {uploading ? 'Importing...' : 'Start Import'}
            </Button>
            
            {uploading && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress />
                <Typography variant="caption" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
                  Processing your file...
                </Typography>
              </Box>
            )}
          </Box>
        );

      case 3:
        return (
          <Box>
            {importResult && (
              <>
                <Alert 
                  severity={importResult.success ? "success" : "error"} 
                  sx={{ mb: 2 }}
                  icon={importResult.success ? <SuccessIcon /> : <ErrorIcon />}
                >
                  <Typography variant="subtitle2">
                    {importResult.message}
                  </Typography>
                </Alert>

                {importResult.data && (
                  <Paper sx={{ p: 2, mb: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Box textAlign="center">
                          <Typography variant="h4" color="success.main">
                            {importResult.data.successCount || 0}
                          </Typography>
                          <Typography variant="caption">Successful</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={4}>
                        <Box textAlign="center">
                          <Typography variant="h4" color="error.main">
                            {importResult.data.errorCount || 0}
                          </Typography>
                          <Typography variant="caption">Errors</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={4}>
                        <Box textAlign="center">
                          <Typography variant="h4" color="primary.main">
                            {importResult.data.totalProcessed || 0}
                          </Typography>
                          <Typography variant="caption">Total</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </Paper>
                )}

                {importResult.data?.errors && importResult.data.errors.length > 0 && (
                  <Box>
                    <Button
                      variant="outlined"
                      startIcon={showErrors ? <ExpandMoreIcon sx={{ transform: 'rotate(180deg)' }} /> : <ExpandMoreIcon />}
                      onClick={() => setShowErrors(!showErrors)}
                      size="small"
                      sx={{ mb: 1 }}
                    >
                      {showErrors ? 'Hide' : 'Show'} Error Details ({importResult.data.errors.length})
                    </Button>
                    
                    <Collapse in={showErrors}>
                      <Paper sx={{ maxHeight: 200, overflow: 'auto', p: 1 }}>
                        <List dense>
                          {importResult.data.errors.map((error, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <ErrorIcon color="error" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText
                                primary={`Row ${error.row}: ${error.error}`}
                                primaryTypographyProps={{ variant: 'caption' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Paper>
                    </Collapse>
                  </Box>
                )}

                {importResult.data?.successfulExams && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Successfully Imported Exams:
                    </Typography>
                    <List dense>
                      {importResult.data.successfulExams.map((exam, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <SuccessIcon color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={`${exam.category} - ${exam.sentencesCount} sentences`}
                            secondary={`Exam ID: ${exam.examId}`}
                            primaryTypographyProps={{ variant: 'body2' }}
                            secondaryTypographyProps={{ variant: 'caption' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: 500 }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" fontWeight={600}>
            {title}
          </Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {currentConfig.description}
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel
                icon={getStepIcon(index)}
                optional={
                  index === 3 ? (
                    <Typography variant="caption">Last step</Typography>
                  ) : null
                }
              >
                {label}
              </StepLabel>
              <StepContent>
                {renderStepContent(index)}
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={handleClose}>
          {activeStep === 3 ? 'Close' : 'Cancel'}
        </Button>
        {activeStep === 3 && importResult?.success && (
          <Button 
            variant="contained" 
            onClick={() => {
              handleClose();
              if (onImportSuccess) {
                onImportSuccess(importResult.data);
              }
            }}
          >
            Done
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ImportDialog;