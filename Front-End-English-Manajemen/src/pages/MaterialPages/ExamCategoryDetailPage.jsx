// src/pages/MaterialPages/ExamCategoryDetailPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import { 
  Box, Typography, Paper, IconButton, Breadcrumbs, Link as MuiLink, CircularProgress, Alert, Button, Stack, Chip, Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, ListItemText, Grid
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import RefreshIcon from "@mui/icons-material/Refresh";
import VisibilityIcon from "@mui/icons-material/Visibility";
import AddIcon from "@mui/icons-material/Add";
import { useParams, Link as RouterLink } from "react-router-dom";
import CustomTypography from "../../components/Elements/CustomTypography";
import CustomButton from "../../components/Elements/CustomButton";
import { materialService } from "../../services/materialService";
import Swal from "sweetalert2";
import TableComponent from "../../components/Elements/TableComponent";
import AddExamMaterialForm from "./Form/AddExamPhoneme";
import EditExamPhoneme from "./Form/EditExamPhoneme";

const ExamCategoryDetailPage = () => {
  const { category } = useParams();
  const decodedCategory = decodeURIComponent(category || "");
  
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalItems, setTotalItems] = useState(0);
  
  const [addFormOpen, setAddFormOpen] = useState(false);
  const [sentenceDialogOpen, setSentenceDialogOpen] = useState(false);
  const [selectedExamSentences, setSelectedExamSentences] = useState([]);
  const [selectedExamInfo, setSelectedExamInfo] = useState(null);

  const [editFormOpen, setEditFormOpen] = useState(false);
  const [editingExam, setEditingExam] = useState(null);
  const [editExamData, setEditExamData] = useState(null);

  const fetchExams = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await materialService.getPhonemeExamsByCategory(decodedCategory, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });
      
      let examsData = response.data?.exams || response.data?.data || [];
      let paginationData = response.data?.pagination || {};
      
      const transformedExams = examsData.map((exam, index) => ({
        id: exam.exam_id || exam.id || index,
        testId: exam.exam_id || exam.id || index,
        testTo: exam.test_number || `Test ${index + 1}`,
        totalSentence: exam.total_sentence || 0,
        lastUpdate: exam.last_update ? new Date(exam.last_update).toLocaleDateString("id-ID") : "N/A",
        examId: exam.exam_id || exam.id || index
      }));
      
      setExams(transformedExams);
      setTotalItems(paginationData.totalRecords || examsData.length);
      
    } catch (err) {
      setError(err.message || "Failed to load exam data");
      setExams([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [decodedCategory, paginationModel]);

  useEffect(() => {
    fetchExams();
  }, [fetchExams]);

  const handleDeleteExam = async (examId) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: "This will permanently delete the exam set and all its sentences.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      confirmButtonText: "Yes, delete it!",
    });
    if (result.isConfirmed) {
      try {
        await materialService.deletePhonemeExam(decodedCategory, examId);
        Swal.fire("Deleted!", "The exam set has been deleted.", "success");
        fetchExams();
      } catch (error) {
        Swal.fire("Error!", error.message || "Failed to delete the exam.", "error");
      }
    }
  };

  const handleViewSentences = async (exam) => {
    try {
      const response = await materialService.getExamSentenceDetail(decodedCategory, exam.examId);
      if (response.data && response.data.sentences) {
        setSelectedExamSentences(response.data.sentences);
        setSelectedExamInfo(response.data.testInfo || { testId: exam.testId, phonemeCategory: decodedCategory });
        setSentenceDialogOpen(true);
      } else {
        Swal.fire("Info", "No sentences found for this exam.", "info");
      }
    } catch (error) {
      Swal.fire("Error!", "Failed to load exam sentences.", "error");
    }
  };

  const handleEditExam = async (exam) => {
    try {
      const response = await materialService.getExamSentenceDetail(decodedCategory, exam.examId);
      if (response.data && response.data.sentences) {
        setEditingExam(exam);
        setEditExamData({
          sentences: response.data.sentences.map(sentence => ({
            id_sentence: sentence.sentenceId || sentence.id_sentence,
            sentence: sentence.sentence || "",
            phoneme: sentence.phoneme || ""
          }))
        });
        setEditFormOpen(true);
      } else {
        Swal.fire("Error!", "Failed to load exam data for editing.", "error");
      }
    } catch (error) {
      Swal.fire("Error!", "Failed to load exam data for editing.", "error");
    }
  };

  const handleEditSubmit = async (updateData) => {
    try {
      await materialService.updatePhonemeExam(decodedCategory, editingExam.examId, updateData);
      Swal.fire("Success!", "Exam has been updated successfully.", "success");
      setEditFormOpen(false);
      fetchExams();
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to update exam.", "error");
    }
  };

  const handleAddSubmit = async (data) => {
    try {
      await materialService.addPhonemeExamMaterial(data);
      Swal.fire("Success!", "Exam set added successfully.", "success");
      setAddFormOpen(false);
      fetchExams();
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to add exam set.", "error");
    }
  };

  const getCategoryPhonemes = () => (decodedCategory.includes("-") ? decodedCategory.split("-") : [decodedCategory]);
  const categoryPhonemes = getCategoryPhonemes();

  const columns = [
    { field: "testTo", headerName: "Test Number", flex: 1, renderCell: (params) => <Typography variant="body2" fontWeight={600} color="primary.main">{params.value}</Typography> },
    { field: "totalSentence", headerName: "Total Questions", flex: 1, renderCell: (params) => <Chip label={`${params.value} sentences`} color={params.value === 10 ? "success" : "warning"} size="small" /> },
    { field: "lastUpdate", headerName: "Last Updated", flex: 1 },
    {
      field: "action",
      headerName: "Actions",
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={1}>
          <IconButton onClick={() => handleViewSentences(params.row)} title="View Sentences" size="small" sx={{ color: "info.main" }}><VisibilityIcon /></IconButton>
          <IconButton onClick={() => handleEditExam(params.row)} title="Edit Exam" size="small" sx={{ color: "primary.main" }}><EditIcon /></IconButton>
          <IconButton onClick={() => handleDeleteExam(params.row.examId)} title="Delete Exam" size="small" sx={{ color: "error.main" }}><DeleteIcon /></IconButton>
        </Stack>
      ),
    },
  ];

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" mb={2}>
        <MuiLink component={RouterLink} to="/material/pronunciation" underline="hover" color="inherit">PRONUNCIATION MATERIAL</MuiLink>
        <CustomTypography color="text.primary">Exam Phoneme: {decodedCategory}</CustomTypography>
      </Breadcrumbs>
      
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Phoneme Exam Detail</Typography>
        <Stack direction="row" spacing={1}>
          <CustomButton colorScheme="bgBlue" startIcon={<AddIcon />} onClick={() => setAddFormOpen(true)} disabled={loading} size="small">Add Exam Set</CustomButton>
          <IconButton onClick={fetchExams} disabled={loading} title="Refresh Data" sx={{ color: "primary.main" }}><RefreshIcon /></IconButton>
        </Stack>
      </Box>

      <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Total: <strong>{totalItems}</strong> exam sets</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
              <Typography variant="body2" color="text.secondary">Target phonemes:</Typography>
              {categoryPhonemes.map((phoneme, index) => (<Chip key={index} label={phoneme} size="small" color="primary" variant="outlined" />))}
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Alert severity="info" sx={{ py: 1 }}>
              <Typography variant="caption">
                <strong>Assessment Focus:</strong> Each exam must have exactly 10 sentences containing ALL target phonemes for comprehensive testing.
              </Typography>
            </Alert>
          </Grid>
        </Grid>
      </Paper>
      
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>
        ) : error ? (
          <Alert severity="error">{error}<Button onClick={fetchExams} sx={{ ml: 2 }}>Retry</Button></Alert>
        ) : exams.length === 0 ? (
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={8} sx={{ border: '2px dashed', borderColor: 'grey.300', borderRadius: 2, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>No Exam Sets Found</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>No exams for category "{decodedCategory}". Add the first set!</Typography>
            <CustomButton colorScheme="bgBlue" startIcon={<AddIcon />} onClick={() => setAddFormOpen(true)} size="small">Add First Exam Set</CustomButton>
          </Box>
        ) : (
          <TableComponent
            rows={exams}
            columns={columns}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalItems}
            loading={loading}
            disableRowSelectionOnClick
            getRowId={(row) => row.id}
          />
        )}
      </Paper>

      <AddExamMaterialForm open={addFormOpen} onClose={() => setAddFormOpen(false)} onSubmit={handleAddSubmit} />
      <EditExamPhoneme open={editFormOpen} onClose={() => setEditFormOpen(false)} onSubmit={handleEditSubmit} examData={editExamData} category={decodedCategory} />

      <Dialog open={sentenceDialogOpen} onClose={() => setSentenceDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={600}>Exam Sentences Detail</Typography>
          {selectedExamInfo && <Typography variant="body2" color="text.secondary">{selectedExamInfo.testId} - Category: {selectedExamInfo.phonemeCategory}</Typography>}
        </DialogTitle>
        <DialogContent>
          <List>
            {selectedExamSentences.map((sentence, index) => (
              <ListItem key={index} divider>
                <ListItemText
                  primary={<Typography variant="body1" sx={{ mb: 1 }}><strong>Sentence {sentence.sentenceOrder || index + 1}:</strong> {sentence.sentence}</Typography>}
                  secondary={sentence.phoneme && <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>Phoneme: {sentence.phoneme}</Typography>}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSentenceDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExamCategoryDetailPage;