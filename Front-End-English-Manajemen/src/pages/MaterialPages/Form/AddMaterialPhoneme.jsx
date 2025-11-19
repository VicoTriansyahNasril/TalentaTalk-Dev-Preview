// src/pages/MaterialPages/Form/AddMaterialPhoneme.jsx
import React, { useState } from "react";
import CustomModal from "../../../components/Elements/CustomModal";
import CustomInput from "../../../components/Elements/CustomInput";
import { Box, Grid, Alert, Typography, Chip, TextField } from "@mui/material";

const AddMaterialPhoneme = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({ 
    phoneme_category: "", 
    word: "", 
    meaning: "", 
    phoneme: "", 
    definition: ""
  });
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  const validatePhonemeTranscription = (transcription, category) => {
    if (!transcription.trim() || !category) {
      return { isValid: false, error: "Both category and transcription are required" };
    }
    
    if (!transcription.includes(category)) {
      return { 
        isValid: false, 
        error: `Phoneme transcription must contain the target category phoneme '${category}'` 
      };
    }
    
    return { isValid: true, error: null };
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.phoneme_category.trim()) {
      errors.phoneme_category = "Phoneme category is required";
    }
    
    if (!formData.word.trim()) {
      errors.word = "Word is required";
    } else if (formData.word.trim().length < 2) {
      errors.word = "Word must be at least 2 characters long";
    }
    
    if (!formData.meaning.trim()) {
      errors.meaning = "Word meaning is required";
    }
    
    if (!formData.phoneme.trim()) {
      errors.phoneme = "Phoneme transcription is required";
    } else if (formData.phoneme_category) {
      const validation = validatePhonemeTranscription(formData.phoneme, formData.phoneme_category);
      if (!validation.isValid) {
        errors.phoneme = validation.error;
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
      phoneme_category: formData.phoneme_category.trim(),
      word: formData.word.trim(),
      meaning: formData.meaning.trim(),
      word_definition: formData.definition.trim(),
      phoneme: formData.phoneme.trim()
    };
    
    onSubmit(submissionData);
    
    setFormData({ 
      phoneme_category: "", 
      word: "", 
      meaning: "", 
      phoneme: "",  
      definition: "" 
    });
    setValidationErrors({});
  };

  const handleClose = () => {
    setFormData({ 
      phoneme_category: "", 
      word: "", 
      meaning: "", 
      phoneme: "",  
      definition: "" 
    });
    setValidationErrors({});
    onClose();
  };

  const phonemeOptions = [
    // Vowels
    { value: "i", label: "i - as in 'beat', 'see'" },
    { value: "ɪ", label: "ɪ - as in 'bit', 'sit'" },
    { value: "ɛ", label: "ɛ - as in 'bet', 'head'" },
    { value: "æ", label: "æ - as in 'bat', 'cat'" },
    { value: "ə", label: "ə - Schwa, as in 'about', 'sofa'" },
    { value: "ɚ", label: "ɚ - as in 'bird', 'first'" },
    { value: "ʌ", label: "ʌ - as in 'but', 'cup'" },
    { value: "ɑ", label: "ɑ - as in 'father', 'cot'" }, // Termasuk fonem baru
    { value: "ɔ", label: "ɔ - as in 'bought', 'saw'" },
    { value: "ʊ", label: "ʊ - as in 'book', 'put'" },
    { value: "u", label: "u - as in 'boot', 'blue'" },
    // Diphthongs
    { value: "eɪ", label: "eɪ - as in 'bait', 'say'" },
    { value: "aɪ", label: "aɪ - as in 'bite', 'my'" },
    { value: "ɔɪ", label: "ɔɪ - as in 'boy', 'coin'" },
    { value: "aʊ", label: "aʊ - as in 'bout', 'now'" },
    { value: "oʊ", label: "oʊ - as in 'boat', 'go'" },
    // Consonants
    { value: "p", label: "p - as in 'pat', 'lip'" },
    { value: "b", label: "b - as in 'bat', 'lab'" },
    { value: "t", label: "t - as in 'tap', 'pet'" },
    { value: "d", label: "d - as in 'dip', 'bad'" },
    { value: "k", label: "k - as in 'kit', 'back'" },
    { value: "g", label: "g - as in 'get', 'bag'" },
    { value: "f", label: "f - as in 'fat', 'leaf'" },
    { value: "v", label: "v - as in 'vet', 'live'" },
    { value: "θ", label: "θ - as in 'thin', 'bath'" },
    { value: "ð", label: "ð - as in 'this', 'breathe'" },
    { value: "s", label: "s - as in 'sip', 'bus'" },
    { value: "z", label: "z - as in 'zip', 'buzz'" },
    { value: "ʃ", label: "ʃ - as in 'ship', 'hush'" },
    { value: "ʒ", label: "ʒ - as in 'measure', 'vision'" },
    { value: "tʃ", label: "tʃ - as in 'chip', 'match'" },
    { value: "dʒ", label: "dʒ - as in 'judge', 'gem'" },
    { value: "h", label: "h - as in 'hat', 'ahead'" },
    { value: "m", label: "m - as in 'mat', 'hum'" },
    { value: "n", label: "n - as in 'nap', 'sun'" },
    { value: "ŋ", label: "ŋ - as in 'sing', 'hanger'" },
    { value: "l", label: "l - as in 'lap', 'ball'" },
    { value: "r", label: "r - as in 'rap', 'car'" },
    { value: "j", label: "j - as in 'yap', 'yes'" },
    { value: "w", label: "w - as in 'wet', 'away'" },
  ];

  const getPhonemeValidation = () => {
    return validatePhonemeTranscription(formData.phoneme, formData.phoneme_category);
  };

  const phonemeValidation = getPhonemeValidation();
  const isFormValid = formData.phoneme_category && formData.word.trim() && formData.meaning.trim() && formData.phoneme.trim() && phonemeValidation.isValid;

  return (
    <CustomModal open={open} onClose={handleClose}>
      <CustomModal.Header onClose={handleClose}>
        ADD NEW PHONEME WORD MATERIAL
      </CustomModal.Header>
      <Box px={3}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Add a word with its phoneme category and actual phoneme transcription. The transcription must contain the target category phoneme for validation.
        </Alert>
        
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <CustomInput
              name="phoneme_category"
              label="Phoneme Category *"
              type="select"
              options={phonemeOptions}
              value={formData.phoneme_category}
              onChange={handleChange}
              fullWidth
              required
              error={!!validationErrors.phoneme_category}
              helperText={validationErrors.phoneme_category || "Select the phoneme category for this word"}
            />
          </Grid>

          {formData.phoneme_category && (
            <Grid item xs={12}>
              <Box sx={{ mb: 1, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
                <Typography variant="body2" color="primary.main" fontWeight={600}>
                  Target Category Phoneme:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Chip 
                    label={formData.phoneme_category}
                    color="primary"
                    size="small"
                    variant="outlined"
                  />
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Your phoneme transcription must contain this sound: <strong>{formData.phoneme_category}</strong>
                </Typography>
              </Box>
            </Grid>
          )}

          <Grid item xs={12}>
            <CustomInput
              name="word"
              label="Word *"
              value={formData.word}
              onChange={handleChange}
              fullWidth
              required
              placeholder="Enter the English word (e.g., application, management)"
              error={!!validationErrors.word}
              helperText={validationErrors.word}
            />
          </Grid>
          
          <Grid item xs={12}>
            <CustomInput
              name="meaning"
              label="Word Meaning *"
              value={formData.meaning}
              onChange={handleChange}
              fullWidth
              required
              placeholder="Enter the meaning in Indonesian (e.g., aplikasi, manajemen)"
              error={!!validationErrors.meaning}
              helperText={validationErrors.meaning}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              name="phoneme"
              label="Phoneme Transcription *"
              value={formData.phoneme}
              onChange={handleChange}
              fullWidth
              required
              placeholder={formData.phoneme_category ? 
                `Enter phoneme transcription containing '${formData.phoneme_category}' (e.g., ${formData.phoneme_category}plɪˈkeɪʃən)` :
                "Enter the phoneme transcription for this word"
              }
              error={!!validationErrors.phoneme}
              helperText={
                validationErrors.phoneme ||
                <Box>
                  <Typography variant="caption">
                    {formData.phoneme_category ? 
                      `Must contain the phoneme: ${formData.phoneme_category}` :
                      "Enter the complete phoneme transcription"
                    }
                  </Typography>
                  {formData.phoneme && formData.phoneme_category && (
                    <Box mt={0.5}>
                      {phonemeValidation.isValid ? (
                        <Chip label={`Valid - contains '${formData.phoneme_category}' ✓`} color="success" size="small" />
                      ) : (
                        <Chip 
                          label={`Missing '${formData.phoneme_category}' in transcription`} 
                          color="error" 
                          size="small" 
                        />
                      )}
                    </Box>
                  )}
                </Box>
              }
            />
          </Grid>
          
          <Grid item xs={12}>
            <CustomInput
              name="definition"
              label="Word Definition (Optional)"
              value={formData.definition}
              onChange={handleChange}
              fullWidth
              multiline
              placeholder="Enter detailed definition (optional)"
              helperText="Provide a more detailed explanation of the word"
            />
          </Grid>
        </Grid>
      </Box>
      <CustomModal.Footer 
        onClose={handleClose} 
        onSubmit={handleSave}
        disableSubmit={!isFormValid}
      >
        Save Material
      </CustomModal.Footer>
    </CustomModal>
  );
};

export default AddMaterialPhoneme;