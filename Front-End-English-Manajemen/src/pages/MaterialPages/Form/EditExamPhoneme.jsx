// src/pages/MaterialPages/Form/EditExamPhoneme.jsx
import React, { useState, useEffect } from "react";
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  TextField, 
  Typography, 
  Alert, 
  Chip, 
  Box, 
  Grid,
  CircularProgress 
} from "@mui/material";

const EditExamPhoneme = ({ open, onClose, onSubmit, examData, category }) => {
  const [formData, setFormData] = useState({ sentences: [] });
  const [validationErrors, setValidationErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (examData && examData.sentences) {
    setFormData({
      sentences: examData.sentences.map(sentence => ({
        id_sentence: sentence.id_sentence || 
          (typeof sentence.sentenceId === 'string' ? 
            parseInt(sentence.sentenceId.replace("SEN", "")) : 
            sentence.sentenceId),
        sentence: sentence.sentence || "",
        phoneme: sentence.phoneme || ""
        }))
      });
    }
  }, [examData]);

  const getCategoryPhonemes = () => {
    if (!category || !category.includes("-")) {
      return [category];
    }
    return category.split("-").map(p => p.trim());
  };

  const validatePhonemeTranscription = (transcription) => {
    if (!transcription.trim() || !category) {
      return { isValid: false, missingPhonemes: [] };
    }
    
    const categoryPhonemes = getCategoryPhonemes();
    const missingPhonemes = categoryPhonemes.filter(phoneme => !transcription.includes(phoneme));
    
    return {
      isValid: missingPhonemes.length === 0,
      missingPhonemes
    };
  };

  const handleSentenceChange = (index, field, value) => {
    const newSentences = [...formData.sentences];
    newSentences[index] = {
      ...newSentences[index],
      [field]: value
    };
    setFormData({ sentences: newSentences });
    
    // Clear validation error
    if (validationErrors[`sentence${index}_${field}`]) {
      setValidationErrors(prev => ({ ...prev, [`sentence${index}_${field}`]: "" }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    formData.sentences.forEach((sentence, index) => {
      if (!sentence.sentence.trim()) {
        errors[`sentence${index}_sentence`] = "Sentence is required";
      } else {
        const wordCount = sentence.sentence.trim().split(/\s+/).length;
        if (wordCount < 10) {
          errors[`sentence${index}_sentence`] = `Must have at least 10 words (current: ${wordCount})`;
        }
      }
      
      if (!sentence.phoneme.trim()) {
        errors[`sentence${index}_phoneme`] = "Phoneme transcription is required";
      } else {
        const validation = validatePhonemeTranscription(sentence.phoneme);
        if (!validation.isValid) {
          errors[`sentence${index}_phoneme`] = `Must contain ALL phonemes: ${validation.missingPhonemes.join(", ")}`;
        }
      }
    });
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      await onSubmit({
        sentences: formData.sentences,
        category: category
      });
      
      onClose();
    } catch (error) {
      console.error("Submit error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ sentences: [] });
    setValidationErrors({});
    onClose();
  };

  const getSentenceWordCount = (sentence) => {
    if (!sentence.trim()) return 0;
    return sentence.trim().split(/\s+/).length;
  };

  const categoryPhonemes = getCategoryPhonemes();
  const isFormValid = formData.sentences.length === 10 && 
    formData.sentences.every(s => 
      s.sentence.trim() !== "" && 
      s.phoneme.trim() !== "" && 
      getSentenceWordCount(s.sentence) >= 10 && 
      validatePhonemeTranscription(s.phoneme).isValid
    );

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        <Typography variant="h6" fontWeight={600}>
          Edit Exam Sentences
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Category: {category} | Total: {formData.sentences.length} sentences
        </Typography>
      </DialogTitle>
      
      <DialogContent dividers>
        <Alert severity="info" sx={{ mb: 2 }}>
          Edit the exam sentences. Each sentence must contain ALL phonemes from the category and have at least 10 words.
        </Alert>
        
        {categoryPhonemes.length > 0 && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'info.50', borderRadius: 1 }}>
            <Typography variant="body2" color="info.main" fontWeight={600}>
              Target Phonemes:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
              {categoryPhonemes.map((phoneme, index) => (
                <Chip 
                  key={index}
                  label={phoneme}
                  color="info"
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}

        <Box sx={{ maxHeight: "60vh", overflowY: "auto", pr: 1 }}>
          <Grid container spacing={2}>
            {formData.sentences.map((sentence, index) => {
              const wordCount = getSentenceWordCount(sentence.sentence);
              const phonemeValidation = validatePhonemeTranscription(sentence.phoneme);
              const hasSentenceError = !!validationErrors[`sentence${index}_sentence`];
              const hasPhonemeError = !!validationErrors[`sentence${index}_phoneme`];
              
              return (
                <Grid item xs={12} key={index}>
                  <Box sx={{ p: 2, border: 1, borderColor: 'grey.300', borderRadius: 2, mb: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Sentence {index + 1}
                    </Typography>
                    
                    <TextField
                      label={
                        <Box component="span" display="flex" justifyContent="space-between" alignItems="center">
                          <span>Exam Sentence *</span>
                          <Chip 
                            label={`${wordCount} words`}
                            color={wordCount >= 10 ? "success" : "default"}
                            size="small"
                          />
                        </Box>
                      }
                      fullWidth
                      multiline
                      rows={2}
                      value={sentence.sentence}
                      onChange={(e) => handleSentenceChange(index, 'sentence', e.target.value)}
                      error={hasSentenceError}
                      helperText={validationErrors[`sentence${index}_sentence`]}
                      sx={{ mb: 2 }}
                    />
                    
                    <TextField
                      label="Phoneme Transcription *"
                      fullWidth
                      multiline
                      rows={2}
                      value={sentence.phoneme}
                      onChange={(e) => handleSentenceChange(index, 'phoneme', e.target.value)}
                      placeholder={categoryPhonemes.length > 0 ? 
                        `Enter phoneme transcription (must contain: ${categoryPhonemes.join(", ")})` : 
                        "Enter phoneme transcription"
                      }
                      error={hasPhonemeError}
                      helperText={
                        validationErrors[`sentence${index}_phoneme`] ||
                        <Box>
                          <Typography variant="caption">
                            {categoryPhonemes.length > 0 ? 
                              `Must contain ALL: ${categoryPhonemes.join(", ")}` :
                              "Enter the full phoneme transcription"
                            }
                          </Typography>
                          {sentence.phoneme && categoryPhonemes.length > 0 && (
                            <Box mt={0.5}>
                              {phonemeValidation.isValid ? (
                                <Chip label="Valid ✓" color="success" size="small" />
                              ) : (
                                <Chip 
                                  label={`Missing: ${phonemeValidation.missingPhonemes.join(", ")}`} 
                                  color="error" 
                                  size="small" 
                                />
                              )}
                            </Box>
                          )}
                        </Box>
                      }
                    />
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={!isFormValid || loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? "Updating..." : "Update Exam"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditExamPhoneme;