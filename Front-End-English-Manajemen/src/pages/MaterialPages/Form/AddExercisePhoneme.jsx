// src/pages/MaterialPages/Form/AddExercisePhoneme.jsx
import React, { useState } from "react";
import CustomModal from "../../../components/Elements/CustomModal";
import CustomInput from "../../../components/Elements/CustomInput";
import { Box, Alert, Typography, Chip, TextField } from "@mui/material";

const AddExercisePhoneme = ({ open, onClose, onSubmit, defaultCategory = "" }) => {
  const [formData, setFormData] = useState({ 
    category: defaultCategory, 
    sentence: "", 
    phoneme: "" 
  });
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: "" }));
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
      errors.category = "Exercise materials must use similar phonemes categories (e.g., 'i-ɪ', 'p-b', 'ə-ʌ-ɚ')";
    }
    
    if (!formData.sentence.trim()) {
      errors.sentence = "Sentence is required";
    } else {
      const wordCount = formData.sentence.trim().split(/\s+/).length;
      if (wordCount < 10) {
        errors.sentence = `Sentence must contain at least 10 words (current: ${wordCount} words)`;
      }
    }
    
    if (!formData.phoneme.trim()) {
      errors.phoneme = "Phoneme transcription is required";
    } else if (formData.category) {
      const validation = validatePhonemeTranscription(formData.phoneme, formData.category);
      if (!validation.isValid) {
        errors.phoneme = `Phoneme transcription must contain ALL phonemes from category: ${validation.missingPhonemes.join(", ")}`;
      }
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) {
      return;
    }

    const submissionData = {
      phoneme_category: formData.category.trim(),
      sentence: formData.sentence.trim(),
      phoneme: formData.phoneme.trim()
    };
    
    onSubmit(submissionData);
    
    setFormData({ category: "", sentence: "", phoneme: "" });
    setValidationErrors({});
  };

  const handleClose = () => {
    setFormData({ category: "", sentence: "", phoneme: "" });
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

  const getSentenceWordCount = () => {
    if (!formData.sentence.trim()) return 0;
    return formData.sentence.trim().split(/\s+/).length;
  };

  const getCategoryPhonemesDisplay = () => {
    if (!formData.category) return [];
    return getCategoryPhonemes(formData.category);
  };

  const getPhonemeValidation = () => {
    return validatePhonemeTranscription(formData.phoneme, formData.category);
  };

  const wordCount = getSentenceWordCount();
  const categoryPhonemes = getCategoryPhonemesDisplay();
  const phonemeValidation = getPhonemeValidation();
  const isFormValid = formData.category && formData.sentence.trim() && formData.phoneme.trim() && wordCount >= 10 && phonemeValidation.isValid;

  return (
    <CustomModal open={open} onClose={handleClose}>
      <CustomModal.Header onClose={handleClose}>
        ADD NEW EXERCISE SENTENCE
      </CustomModal.Header>
      <Box px={3}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Create a practice sentence for similar phonemes training. The sentence must contain ALL phonemes from the selected category for effective contrastive learning.
        </Alert>
        
        <CustomInput
          name="category"
          label="Similar Phonemes Category *"
          type="select"
          options={categoryOptions}
          value={formData.category}
          onChange={handleChange}
          fullWidth
          required
          error={!!validationErrors.category}
          helperText={validationErrors.category || "Choose similar phonemes for contrastive practice"}
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
              Your sentence and phoneme transcription must contain ALL of these sounds.
            </Typography>
          </Box>
        )}
        
        <CustomInput
          name="sentence"
          label="Practice Sentence *"
          value={formData.sentence}
          onChange={handleChange}
          fullWidth
          multiline
          required
          placeholder={`Enter a sentence containing all target phonemes (minimum 10 words)${categoryPhonemes.length > 0 ? ` - must include: ${categoryPhonemes.join(", ")}` : ""}`}
          error={!!validationErrors.sentence}
          helperText={
            validationErrors.sentence || 
            <Box component="span" display="flex" justifyContent="space-between">
              <span>Sentence must contain at least 10 words</span>
              <Chip 
                label={`${wordCount} words`}
                color={wordCount >= 10 ? "success" : "default"}
                size="small"
              />
            </Box>
          }
        />
        
        <TextField
          name="phoneme"
          label="Phoneme Transcription *"
          value={formData.phoneme}
          onChange={handleChange}
          fullWidth
          multiline
          rows={2}
          required
          placeholder={categoryPhonemes.length > 0 ? 
            `Enter the phoneme transcription of your sentence (must contain: ${categoryPhonemes.join(", ")})` : 
            "Enter the phoneme transcription of your sentence"
          }
          error={!!validationErrors.phoneme}
          helperText={
            validationErrors.phoneme ||
            <Box>
              <Typography variant="caption">
                {categoryPhonemes.length > 0 ? 
                  `Must contain ALL phonemes: ${categoryPhonemes.join(", ")}` :
                  "Enter the full phoneme transcription"
                }
              </Typography>
              {formData.phoneme && categoryPhonemes.length > 0 && (
                <Box mt={1}>
                  {phonemeValidation.isValid ? (
                    <Chip label="Valid transcription ✓" color="success" size="small" />
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
          sx={{ mt: 2 }}
        />
      </Box>
      <CustomModal.Footer 
        onClose={handleClose} 
        onSubmit={handleSave}
        disableSubmit={!isFormValid}
      >
        Save Exercise
      </CustomModal.Footer>
    </CustomModal>
  );
};

export default AddExercisePhoneme;