import React, { useState, useEffect, useCallback } from "react";
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
import { useParams, Link as RouterLink } from "react-router-dom";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import RefreshIcon from "@mui/icons-material/Refresh";
import CustomTypography from "../../components/Elements/CustomTypography";
import { materialService } from "../../services/materialService";
import Swal from "sweetalert2";
import TableComponent from "../../components/Elements/TableComponent";

const ExercisePhonemeDetailPage = () => {
  const { category } = useParams();
  const decodedCategory = decodeURIComponent(category || "");
  
  const [sentences, setSentences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalItems, setTotalItems] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingSentence, setEditingSentence] = useState(null);
  const [editForm, setEditForm] = useState({ sentence: "", phoneme: "" });

  const fetchSentences = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await materialService.getPhonemeSentencesByCategory(decodedCategory, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });
      
      let sentencesData = [];
      let paginationData = {};
      
      if (response.data) {
        sentencesData = response.data.data || [];
        paginationData = response.data.pagination || {};
      }
      
      setSentences(sentencesData);
      setTotalItems(paginationData.totalRecords || sentencesData.length);
      
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to load sentence data");
      setSentences([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [decodedCategory, paginationModel]);

  useEffect(() => {
    fetchSentences();
  }, [fetchSentences]);

  const handleDelete = async (sentenceId, sentenceText) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: `Delete sentence: "${sentenceText.substring(0, 30)}..."?`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      confirmButtonText: "Yes, delete it!",
    });

    if (result.isConfirmed) {
      try {
        await materialService.deletePhonemeSentence(sentenceId);
        Swal.fire("Deleted!", "The sentence has been deleted.", "success");
        fetchSentences();
      } catch (err) {
        Swal.fire("Error!", err.message || "Failed to delete the sentence.", "error");
      }
    }
  };

  const handleEdit = (row) => {
    setEditingSentence(row);
    setEditForm({
      sentence: row.sentence || row.kalimat || "",
      phoneme: row.phoneme || row.fonem || ""
    });
    setEditDialogOpen(true);
  };

  const handleEditClose = () => {
    setEditDialogOpen(false);
    setEditingSentence(null);
    setEditForm({ sentence: "", phoneme: "" });
  };

  const handleEditSubmit = async () => {
    try {
      if (!editForm.sentence.trim() || !editForm.phoneme.trim()) {
        Swal.fire("Validation Error!", "All fields are required.", "error");
        return;
      }
      
      await materialService.updatePhonemeSentence(editingSentence.id, {
        sentence: editForm.sentence.trim(),
        phoneme: editForm.phoneme.trim()
      });
      
      Swal.fire("Success!", "Sentence updated successfully.", "success");
      handleEditClose();
      fetchSentences();
      
    } catch (err) {
      Swal.fire("Error!", err.message || "Failed to update sentence.", "error");
    }
  };

  const columns = [
    { 
      field: "sentence", 
      headerName: "Sentence", 
      flex: 3,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ whiteSpace: "normal", py: 1 }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: "phoneme", 
      headerName: "Phoneme Transcription", 
      flex: 1.5,
      renderCell: (params) => (
        <Chip 
          label={params.value || ""}
          variant="outlined"
          size="small"
          sx={{ fontFamily: 'monospace', bgcolor: 'background.paper' }}
        />
      )
    },
    {
      field: "action",
      headerName: "Action",
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={1}>
          <IconButton size="small" title="Edit" onClick={() => handleEdit(params.row)} sx={{ color: "primary.main" }}>
            <EditIcon />
          </IconButton>
          <IconButton size="small" title="Delete" onClick={() => handleDelete(params.row.id, params.row.sentence)} sx={{ color: "error.main" }}>
            <DeleteIcon />
          </IconButton>
        </Stack>
      ),
    },
  ];

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" mb={2}>
        <MuiLink component={RouterLink} to="/material/exercise" underline="hover" color="inherit">
          EXERCISE MATERIAL
        </MuiLink>
        <CustomTypography color="text.primary">
          Category: {decodedCategory}
        </CustomTypography>
      </Breadcrumbs>
      
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Exercise Sentence Detail</Typography>
        <IconButton onClick={fetchSentences} disabled={loading} title="Refresh Data" sx={{ color: "primary.main" }}>
          <RefreshIcon />
        </IconButton>
      </Box>

      <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Total: <strong>{totalItems}</strong> sentences</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
              <Typography variant="body2" color="text.secondary">Target phonemes:</Typography>
              <Chip label={decodedCategory} size="small" color="primary" variant="outlined" />
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Alert severity="info" sx={{ py: 1 }}>
              <Typography variant="caption">
                <strong>Instruction:</strong> These sentences are used for <em>Sentence Practice</em> mode to train similar phonemes.
              </Typography>
            </Alert>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>
        ) : error ? (
          <Alert severity="error">{error}<Button onClick={fetchSentences} sx={{ ml: 2 }}>Retry</Button></Alert>
        ) : sentences.length === 0 ? (
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={8} sx={{ border: '2px dashed', borderColor: 'grey.300', borderRadius: 2, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>No Sentences Found</Typography>
            <Typography variant="body2" color="text.secondary">There are no practice sentences for category "{decodedCategory}".</Typography>
          </Box>
        ) : (
          <TableComponent
            rows={sentences.map(s => ({ id: s.id, ...s }))}
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

      <Dialog open={editDialogOpen} onClose={handleEditClose} maxWidth="md" fullWidth>
        <DialogTitle>Edit Sentence</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Sentence"
              fullWidth
              multiline
              rows={2}
              value={editForm.sentence}
              onChange={(e) => setEditForm({ ...editForm, sentence: e.target.value })}
            />
            <TextField
              label="Phoneme Transcription"
              fullWidth
              value={editForm.phoneme}
              onChange={(e) => setEditForm({ ...editForm, phoneme: e.target.value })}
              helperText={`Must contain phonemes: ${decodedCategory}`}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditClose}>Cancel</Button>
          <Button variant="contained" onClick={handleEditSubmit}>Update</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExercisePhonemeDetailPage;