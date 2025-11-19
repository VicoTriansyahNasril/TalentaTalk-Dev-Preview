// src/pages/MaterialPages/Form/AddExamPhoneme.jsx
import React, { useState } from "react";
import CustomModal from "../../../components/Elements/CustomModal";
import CustomInput from "../../../components/Elements/CustomInput";
import { Box, Grid, Typography, Alert, Chip, Accordion, AccordionSummary, AccordionDetails, TextField } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

const AddExamPhoneme = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({ 
    category: "", 
    sentenceItems: Array(10).fill({ sentence: "", phoneme: "" })
  });
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e, index, field) => {
    if (e.target.name === "category") {
      setFormData({ 
        ...formData, 
        category: e.target.value,
        sentenceItems: Array(10).fill({ sentence: "", phoneme: "" })
      });
      setValidationErrors({});
    } else {
      const newItems = [...formData.sentenceItems];
      newItems[index] = {
        ...newItems[index],
        [field]: e.target.value
      };
      setFormData({ ...formData, sentenceItems: newItems });
      
      if (validationErrors[`sentence${index}_${field}`]) {
        setValidationErrors(prev => ({ ...prev, [`sentence${index}_${field}`]: "" }));
      }
    }
  };

  const getCategoryPhonemes = (category) => {
    if (!category || !category.includes("-")) {
      return [];
    }
    return category.split("-").map(p => p.trim());
  };

  const validatePhonemeTranscription = (transcription, category) => {
    if (!transcription.trim() || !category) {
      return { isValid: false, missingPhonemes: [] };
    }
    
    const categoryPhonemes = getCategoryPhonemes(category);
    const missingPhonemes = categoryPhonemes.filter(phoneme => !transcription.includes(phoneme));
    
    return {
      isValid: missingPhonemes.length === 0,
      missingPhonemes
    };
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.category.trim()) {
      errors.category = "Phoneme category is required";
    } else if (!formData.category.includes("-")) {
      errors.category = "Exam materials must use similar phonemes categories (e.g., 'i-ɪ', 'p-b', 'ə-ʌ-ɚ')";
    }
    
    const filledSentences = formData.sentenceItems.filter(s => s.sentence.trim() !== "");
    if (filledSentences.length !== 10) {
      errors.sentences = `Exam must have exactly 10 sentences (current: ${filledSentences.length})`;
    }
    
    formData.sentenceItems.forEach((item, index) => {
      if (item.sentence.trim() === "") {
        errors[`sentence${index}_sentence`] = "Sentence is required";
      } else {
        const wordCount = item.sentence.trim().split(/\s+/).length;
        if (wordCount < 10) {
          errors[`sentence${index}_sentence`] = `Must have at least 10 words (current: ${wordCount})`;
        }
      }
      
      if (item.phoneme.trim() === "") {
        errors[`sentence${index}_phoneme`] = "Phoneme transcription is required";
      } else if (formData.category) {
        const validation = validatePhonemeTranscription(item.phoneme, formData.category);
        if (!validation.isValid) {
          errors[`sentence${index}_phoneme`] = `Must contain ALL phonemes: ${validation.missingPhonemes.join(", ")}`;
        }
      }
    });
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) {
      return;
    }

    const submissionData = {
      category: formData.category.trim(),
      items: formData.sentenceItems.map(item => ({
        sentence: item.sentence.trim(),
        phoneme: item.phoneme.trim()
      }))
    };
    
    onSubmit(submissionData);
    
    setFormData({ category: "", sentenceItems: Array(10).fill({ sentence: "", phoneme: "" }) });
    setValidationErrors({});
  };

  const handleClose = () => {
    setFormData({ category: "", sentenceItems: Array(10).fill({ sentence: "", phoneme: "" }) });
    setValidationErrors({});
    onClose();
  };

  const categoryOptions = [
    { value: "i-ɪ", label: "i-ɪ (beat vs bit)" },
    { value: "æ-ɛ", label: "æ-ɛ (bat vs bet)" },
    { value: "u-ʊ", label: "u-ʊ (boot vs book)" },
    { value: "b-p", label: "b-p (buy vs pie)" },
    { value: "d-t", label: "d-t (day vs tie)" },
    { value: "g-k", label: "g-k (go vs key)" },
    { value: "f-v", label: "f-v (fan vs van)" },
    { value: "ð-θ", label: "ð-θ (then vs thin)" },
    { value: "s-z", label: "s-z (sip vs zip)" },
    { value: "ʒ-ʃ", label: "ʒ-ʃ (vision vs ship)" },
    { value: "dʒ-tʃ", label: "dʒ-tʃ (jam vs chain)" },
    { value: "m-n", label: "m-n (my vs nine)" },
    { value: "n-ŋ", label: "n-ŋ (sun vs sung)" },
    { value: "l-r", label: "l-r (light vs right)" },
    { value: "i-j", label: "i-j (east vs yeast)" },
    { value: "u-w", label: "u-w (ooze vs wooze)" },
    { value: "ə-ʌ-ɚ", label: "ə-ʌ-ɚ (about, cup, bird)" },
    { value: "ɑ-ɔ-ʌ", label: "ɑ-ɔ-ʌ (hot, caught, hut)" },
    { value: "ɑ-ɔ-oʊ", label: "ɑ-ɔ-oʊ (hot, caught, boat)" },
    { value: "oʊ-ɔ-ʊ", label: "oʊ-ɔ-ʊ (boat, bought, book)" },
    { value: "oʊ-u-ʊ", label: "oʊ-u-ʊ (boat, boot, book)" },
    { value: "ɛ-i-ɪ", label: "ɛ-i-ɪ (bet, beat, bit)" },
    { value: "æ-ɛ-ɪ", label: "æ-ɛ-ɪ (bat, bet, bit)" },
    { value: "eɪ-ɛ-ɪ", label: "eɪ-ɛ-ɪ (bait, bet, bit)" },
    { value: "aɪ-ɑ-ɪ", label: "aɪ-ɑ-ɪ (bite, bot, bit)" },
    { value: "ɔ-ɔɪ-ɪ", label: "ɔ-ɔɪ-ɪ (bought, boy, bit)" },
    { value: "aʊ-ɑ-ʊ", label: "aʊ-ɑ-ʊ (bout, bot, book)" },
    { value: "m-n-ŋ", label: "m-n-ŋ (sum, sun, sung)" },
  ];

  const getSentenceWordCount = (sentence) => {
    if (!sentence.trim()) return 0;
    return sentence.trim().split(/\s+/).length;
  };

  const getFilledSentencesCount = () => {
    return formData.sentenceItems.filter(s => s.sentence.trim() !== "").length;
  };

  const getCategoryPhonemesDisplay = () => {
    if (!formData.category) return [];
    return getCategoryPhonemes(formData.category);
  };

  const filledCount = getFilledSentencesCount();
  const categoryPhonemes = getCategoryPhonemesDisplay();
  const isFormValid = formData.category && filledCount === 10 && 
    formData.sentenceItems.every(s => s.sentence.trim() !== "" && s.phoneme.trim() !== "" && 
      getSentenceWordCount(s.sentence) >= 10 && 
      validatePhonemeTranscription(s.phoneme, formData.category).isValid);

  return (
    <CustomModal open={open} onClose={handleClose}>
      <CustomModal.Header onClose={handleClose}>
        ADD NEW EXAM SENTENCE SET
      </CustomModal.Header>
      <Box px={3}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Create an exam with exactly 10 sentences for phoneme assessment. Each sentence must contain ALL phonemes from the selected category.
        </Alert>
        
        <CustomInput
          name="category"
          label="Similar Phonemes Category *"
          type="select"
          options={categoryOptions}
          value={formData.category}
          onChange={(e) => handleChange(e)}
          fullWidth
          required
          error={!!validationErrors.category}
          helperText={validationErrors.category || "Choose similar phonemes for exam assessment"}
        />
        
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
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Each sentence and its phoneme transcription must contain ALL of these sounds.
            </Typography>
          </Box>
        )}

        <Box sx={{ mt: 2, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Exam Sentences ({filledCount}/10) *
          </Typography>
          
          {validationErrors.sentences && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {validationErrors.sentences}
            </Alert>
          )}
          
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="body2" fontWeight={600}>
                Sentence Input ({filledCount}/10 completed)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ maxHeight: "500px", overflowY: "auto", pr: 1 }}>
                <Grid container spacing={2}>
                  {formData.sentenceItems.map((item, index) => {
                    const wordCount = getSentenceWordCount(item.sentence);
                    const phonemeValidation = validatePhonemeTranscription(item.phoneme, formData.category);
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
                            value={item.sentence}
                            onChange={(e) => handleChange(e, index, 'sentence')}
                            placeholder={`Enter sentence ${index + 1} containing ALL target phonemes (min 10 words)...`}
                            error={hasSentenceError}
                            helperText={validationErrors[`sentence${index}_sentence`]}
                            sx={{ mb: 2 }}
                          />
                          
                          <TextField
                            label="Phoneme Transcription *"
                            fullWidth
                            multiline
                            rows={2}
                            value={item.phoneme}
                            onChange={(e) => handleChange(e, index, 'phoneme')}
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
                                {item.phoneme && categoryPhonemes.length > 0 && (
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
            </AccordionDetails>
          </Accordion>
        </Box>
      </Box>
      <CustomModal.Footer 
        onClose={handleClose} 
        onSubmit={handleSave}
        disableSubmit={!isFormValid}
      >
        Save Exam Set
      </CustomModal.Footer>
    </CustomModal>
  );
};

export default AddExamPhoneme;