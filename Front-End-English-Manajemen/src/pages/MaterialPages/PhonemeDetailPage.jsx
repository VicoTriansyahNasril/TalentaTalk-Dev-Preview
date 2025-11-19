// src/pages/MaterialPages/PhonemeDetailPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import { useParams, Link as RouterLink } from "react-router-dom";
import { 
  Box, 
  Typography, 
  Paper, 
  IconButton, 
  Breadcrumbs, 
  Link as MuiLink, 
  CircularProgress, 
  Alert, 
  Button, 
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import RefreshIcon from "@mui/icons-material/Refresh";
import CustomTypography from "../../components/Elements/CustomTypography";
import { materialService } from "../../services/materialService";
import Swal from "sweetalert2";
import TableComponent from "../../components/Elements/TableComponent";

const PhonemeDetailPage = () => {
  const { phoneme } = useParams();
  const decodedPhoneme = decodeURIComponent(phoneme || "");
  
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalItems, setTotalItems] = useState(0);
  
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingWord, setEditingWord] = useState(null);
  const [editForm, setEditForm] = useState({ word: "", meaning: "", definition: "", phoneme: "" });

  const fetchWords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await materialService.getPhonemeWordsByCategory(decodedPhoneme, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });
      
      let wordsData = [];
      let paginationData = {};
      
      if (response.data) {
        if (Array.isArray(response.data.data)) {
          wordsData = response.data.data;
          paginationData = response.data.pagination || {};
        } else if (Array.isArray(response.data)) {
          wordsData = response.data;
        } else if (response.data.words && Array.isArray(response.data.words)) {
          wordsData = response.data.words;
          paginationData = response.data.pagination || {};
        }
      }
      
      setWords(wordsData);
      setTotalItems(paginationData.totalRecords || wordsData.length);
      
    } catch (err) {
      setError(err.message || "Failed to load word data");
      setWords([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [decodedPhoneme, paginationModel]);

  useEffect(() => {
    fetchWords();
  }, [fetchWords]);

  const handleDelete = async (wordId, wordName) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: `You are about to delete the word "${wordName}". This action cannot be undone.`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
    });

    if (result.isConfirmed) {
      try {
        await materialService.deletePhonemeWord(wordId);
        Swal.fire("Deleted!", `The word "${wordName}" has been deleted.`, "success");
        fetchWords();
      } catch (err) {
        Swal.fire("Error!", err.message || "Failed to delete the word.", "error");
      }
    }
  };

  const handleEdit = (word) => {
    setEditingWord(word);
    setEditForm({
      word: word.word || "",
      meaning: word.meaning || "",
      definition: word.definition || "",
      phoneme: word.phoneme || word.fonem || ""
    });
    setEditDialogOpen(true);
  };

  const handleEditClose = () => {
    setEditDialogOpen(false);
    setEditingWord(null);
    setEditForm({ word: "", meaning: "", definition: "", phoneme: "" });
  };

  const handleEditSubmit = async () => {
    try {
      if (!editForm.word.trim() || !editForm.meaning.trim()) {
        Swal.fire("Validation Error!", "Word and meaning are required fields.", "error");
        return;
      }
      
      await materialService.updatePhonemeWord(decodedPhoneme, editingWord.id, {
        word: editForm.word.trim(),
        meaning: editForm.meaning.trim(),
        definition: editForm.definition.trim(),
        phoneme: editForm.phoneme.trim()
      });
      
      Swal.fire("Success!", "Word has been updated successfully.", "success");
      handleEditClose();
      fetchWords();
      
    } catch (err) {
      Swal.fire("Error!", err.message || "Failed to update the word.", "error");
    }
  };

  const handleEditFormChange = (field, value) => {
    setEditForm(prev => ({ ...prev, [field]: value }));
  };

  const columns = [
    { 
      field: "word", 
      headerName: "Word", 
      flex: 1,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 600, color: "primary.main" }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: "meaning", 
      headerName: "Word Meaning", 
      flex: 2,
      renderCell: (params) => <Typography variant="body2">{params.value}</Typography>
    },
    { 
      field: "phoneme", 
      headerName: "Phoneme Transcription", 
      flex: 1,
      renderCell: (params) => {
        const phonemeValue = params.value || params.row.fonem || "";
        return (
          <Chip 
            label={phonemeValue}
            variant="outlined"
            size="small"
            sx={{ fontFamily: 'monospace', fontWeight: 600, backgroundColor: 'success.50', color: 'success.main', border: '1px solid', borderColor: 'success.main', fontSize: '0.75rem' }}
          />
        );
      }
    },
    { 
      field: "definition", 
      headerName: "Definition", 
      flex: 2,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={params.value}>
          {params.value || "No definition provided"}
        </Typography>
      )
    },
    {
      field: "action",
      headerName: "Action",
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={1}>
          <IconButton size="small" title="Edit Word" onClick={() => handleEdit(params.row)} sx={{ color: "primary.main" }}>
            <EditIcon />
          </IconButton>
          <IconButton size="small" title="Delete Word" onClick={() => handleDelete(params.row.id, params.row.word)} sx={{ color: "error.main" }}>
            <DeleteIcon />
          </IconButton>
        </Stack>
      ),
    },
  ];

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" mb={2}>
        <MuiLink component={RouterLink} to="/material/pronunciation" underline="hover" color="inherit">
          PRONUNCIATION MATERIAL
        </MuiLink>
        <CustomTypography color="text.primary">
          Phoneme Category: {decodedPhoneme}
        </CustomTypography>
      </Breadcrumbs>
      
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Phoneme Word Detail</Typography>
        <IconButton onClick={fetchWords} disabled={loading} title="Refresh Data" sx={{ color: "primary.main" }}>
          <RefreshIcon />
        </IconButton>
      </Box>

      <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Total: <strong>{totalItems}</strong> words</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
              <Typography variant="body2" color="text.secondary">Target phoneme:</Typography>
              <Chip label={decodedPhoneme} size="small" color="primary" variant="outlined" />
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Alert severity="info" sx={{ py: 1 }}>
              <Typography variant="caption">
                <strong>Focus:</strong> This list contains individual words where the main pronunciation focus is the category phoneme.
              </Typography>
            </Alert>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>
        ) : error ? (
          <Alert severity="error">{error}<Button onClick={fetchWords} sx={{ ml: 2 }}>Retry</Button></Alert>
        ) : words.length === 0 ? (
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={8} sx={{ border: '2px dashed', borderColor: 'grey.300', borderRadius: 2, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>No Words Found</Typography>
            <Typography variant="body2" color="text.secondary">There are no words available for the category "{decodedPhoneme}".</Typography>
          </Box>
        ) : (
          <TableComponent
            rows={words.map(word => ({ id: word.id, ...word, phoneme: word.phoneme || word.fonem || "" }))}
            columns={columns}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalItems}
            loading={loading}
            disableRowSelectionOnClick
            getRowId={(row) => row.id}
            rowHeight={80}
          />
        )}
      </Paper>

      <Dialog open={editDialogOpen} onClose={handleEditClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={600}>Edit Word</Typography>
          <Typography variant="body2" color="text.secondary">Update the word details for category {decodedPhoneme}</Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}><TextField label="Word *" fullWidth value={editForm.word} onChange={(e) => handleEditFormChange("word", e.target.value)} placeholder="Enter the word" /></Grid>
            <Grid item xs={12}><TextField label="Word Meaning *" fullWidth value={editForm.meaning} onChange={(e) => handleEditFormChange("meaning", e.target.value)} placeholder="Enter the meaning in Indonesian" /></Grid>
            <Grid item xs={12}><TextField label="Phoneme Transcription" fullWidth value={editForm.phoneme} onChange={(e) => handleEditFormChange("phoneme", e.target.value)} placeholder="Enter the phoneme transcription" helperText="The actual phoneme sound/transcription for this specific word" /></Grid>
            <Grid item xs={12}><TextField label="Definition" fullWidth multiline rows={3} value={editForm.definition} onChange={(e) => handleEditFormChange("definition", e.target.value)} placeholder="Enter detailed definition (optional)" /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={handleEditClose}>Cancel</Button>
          <Button variant="contained" onClick={handleEditSubmit} disabled={!editForm.word.trim() || !editForm.meaning.trim()} startIcon={<EditIcon />}>Update Word</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PhonemeDetailPage;