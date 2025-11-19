// src/pages/MaterialPages/MaterialInterviewPage.jsx

import React, { useState, useEffect, useCallback } from "react";
import { 
  Box, 
  Typography, 
  IconButton, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  TextField, 
  Paper, 
  Stack, 
  CircularProgress, 
  Alert,
  Chip,
  Tooltip,
  Switch,
  FormControlLabel
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import RefreshIcon from "@mui/icons-material/Refresh";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import PhoneAndroidIcon from "@mui/icons-material/PhoneAndroid";
import Swal from "sweetalert2";
import TableComponent from "../../components/Elements/TableComponent";
import CustomButton from "../../components/Elements/CustomButton";
import { materialService } from "../../services/materialService";

const MaterialInterviewPage = () => {
  const [questions, setQuestions] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalItems, setTotalItems] = useState(0);
  const [swapLoading, setSwapLoading] = useState(null);
  const [toggleLoading, setToggleLoading] = useState(null);

  const fetchInterviewMaterials = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await materialService.getInterviewMaterials({
        page: paginationModel.page + 1,
        pageSize: paginationModel.pageSize,
      });
      
      if (response.data && response.data.interviewQuestions) {
        setQuestions(response.data.interviewQuestions);
        setTotalItems(response.data.pagination?.totalRecords || 0);
      } else {
        setQuestions([]);
        setTotalItems(0);
      }
    } catch (err) {
      setError(err.message || "Failed to load interview materials");
      setQuestions([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [paginationModel]);

  useEffect(() => {
    fetchInterviewMaterials();
  }, [fetchInterviewMaterials]);

  const handleOpenAdd = () => {
    setEditItem(null);
    setInputValue("");
    setDialogOpen(true);
  };

  const handleOpenEdit = (item) => {
    setEditItem(item);
    setInputValue(item.interviewQuestion || "");
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditItem(null);
    setInputValue("");
  };

  const handleDelete = async (item) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: "You won't be able to revert this!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "Cancel"
    });
    
    if (result.isConfirmed) {
      try {
        const questionId = parseInt(item.questionId.replace('QST', ''));
        await materialService.deleteInterviewMaterial(questionId);
        Swal.fire("Deleted!", "Question has been deleted.", "success");
        fetchInterviewMaterials();
      } catch (error) {
        Swal.fire("Error!", error.message || "Failed to delete question.", "error");
      }
    }
  };

  const handleSwap = async (item, direction) => {
    const questionId = parseInt(item.questionId.replace('QST', ''));
    setSwapLoading(questionId);
    
    try {
      await materialService.swapQuestionOrder(questionId, direction);
      Swal.fire({
        title: "Success!",
        text: `Question moved ${direction} successfully`,
        icon: "success",
        timer: 1500,
        showConfirmButton: false
      });
      fetchInterviewMaterials();
    } catch (error) {
      let errorMessage = "Failed to swap question order";
      if (error.message && error.message.includes("already at the")) {
        errorMessage = error.message;
      }
      Swal.fire("Error!", errorMessage, "error");
    } finally {
      setSwapLoading(null);
    }
  };

  const handleToggleStatus = async (questionId, currentStatus) => {
    const id = parseInt(questionId.replace('QST', ''));
    setToggleLoading(id);
    try {
      await materialService.toggleInterviewQuestionStatus(id);
      
      setQuestions(prev => 
        prev.map(q => 
          q.questionId === questionId ? { ...q, isActive: !q.isActive } : q
        )
      );
      
      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: `Question status changed to ${!currentStatus ? 'Active' : 'Inactive'}`,
        showConfirmButton: false,
        timer: 2000
      });
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to update status.", "error");
    } finally {
      setToggleLoading(null);
    }
  };

  const handleViewMobileOrder = async () => {
    try {
      const response = await materialService.getQuestionsForMobile();
      
      if (response.data && response.data.questions) {
        const orderList = response.data.questions.map((q, index) => 
          `${index + 1}. ${q.question}`
        ).join('\n');
        
        Swal.fire({
          title: "Mobile Question Order (Active Only)",
          html: `
            <div style="text-align: left; max-height: 400px; overflow-y: auto;">
              <p style="margin-bottom: 15px; font-weight: bold;">Only active questions will be delivered to the mobile app in this order:</p>
              <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.4;">${orderList}</pre>
            </div>
          `,
          width: '600px',
          confirmButtonText: "OK"
        });
      }
    } catch (error) {
      Swal.fire("Error!", "Failed to load mobile question order", "error");
    }
  };

  const validateInput = (text) => {
    if (!text.trim()) {
      return "Question cannot be empty.";
    }
    if (text.trim().split(' ').length < 5) {
      return "Question must contain at least 5 words.";
    }
    return null;
  };

  const handleSave = async () => {
    try {
      const validationError = validateInput(inputValue);
      if (validationError) {
        Swal.fire("Error!", validationError, "error");
        return;
      }

      if (editItem) {
        const questionId = parseInt(editItem.questionId.replace('QST', ''));
        await materialService.updateInterviewMaterial(questionId, { 
          interview_question: inputValue.trim() 
        });
        Swal.fire("Success!", "Question updated successfully.", "success");
      } else {
        await materialService.addInterviewMaterial({ 
          interview_question: inputValue.trim() 
        });
        Swal.fire("Success!", "Question added successfully.", "success");
      }
      
      handleCloseDialog();
      fetchInterviewMaterials();
    } catch (error) {
      let errorMessage = "Failed to save question.";
      if (error.message && error.message.includes("already exists")) {
        errorMessage = "This question already exists.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      Swal.fire("Error!", errorMessage, "error");
    }
  };

  const getWordCount = (text) => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  const interviewColumns = [
    {
      field: "orderPosition",
      headerName: "#",
      width: 60,
      renderCell: (params) => (
        <Box 
          display="flex" 
          alignItems="center" 
          justifyContent="center" 
          sx={{ 
            fontWeight: 600, 
            color: "primary.main",
            minHeight: "100%"
          }}
        >
          {params.value}
        </Box>
      )
    },
    { 
      field: "interviewQuestion", 
      headerName: "Interview Question", 
      flex: 3,
      renderCell: (params) => (
        <Typography 
          variant="body2" 
          sx={{ 
            wordBreak: "break-word",
            whiteSpace: "normal",
            lineHeight: 1.4,
            py: 1
          }}
        >
          {params.value}
        </Typography>
      )
    },
    {
      field: "isActive",
      headerName: "Status",
      width: 150,
      renderCell: (params) => (
        <FormControlLabel
          control={
            <Switch
              checked={params.value}
              onChange={() => handleToggleStatus(params.row.questionId, params.value)}
              disabled={toggleLoading === parseInt(params.row.questionId.replace('QST', ''))}
            />
          }
          label={
            <Chip 
              label={params.value ? "Active" : "Inactive"}
              color={params.value ? "success" : "default"}
              size="small"
            />
          }
        />
      )
    },
    { 
      field: "createdAt", 
      headerName: "Last Update", 
      width: 120,
      renderCell: (params) => {
        try {
          return new Date(params.value).toLocaleDateString("id-ID");
        } catch (e) {
          return params.value || "N/A";
        }
      }
    },
    {
      field: "action",
      headerName: "Action",
      width: 150,
      sortable: false,
      renderCell: (params) => {
        const questionId = parseInt(params.row.questionId.replace('QST', ''));
        const isSwapLoading = swapLoading === questionId;
        
        return (
          <Stack direction="row" spacing={0.5}>
            <Tooltip title="Move Up">
              <IconButton 
                onClick={() => handleSwap(params.row, "up")} 
                size="small"
                disabled={isSwapLoading}
                sx={{ color: "success.main" }}
              >
                {isSwapLoading ? <CircularProgress size={16} /> : <KeyboardArrowUpIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Move Down">
              <IconButton 
                onClick={() => handleSwap(params.row, "down")} 
                size="small"
                disabled={isSwapLoading}
                sx={{ color: "warning.main" }}
              >
                {isSwapLoading ? <CircularProgress size={16} /> : <KeyboardArrowDownIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Edit Question">
              <IconButton 
                onClick={() => handleOpenEdit(params.row)} 
                size="small"
                sx={{ color: "primary.main" }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Delete Question">
              <IconButton 
                onClick={() => handleDelete(params.row)} 
                size="small" 
                sx={{ color: "error.main" }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        );
      }
    }
  ];

  const transformedQuestions = questions.map((q, index) => ({
    id: q.questionId || `question-${index}`,
    ...q
  }));

  const wordCount = getWordCount(inputValue);
  const isValidInput = wordCount >= 5;

  return (
    <Box p={4}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h6" fontWeight={600}>
            Interview Material Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage interview questions for talent assessment (Order determines mobile delivery sequence)
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Tooltip title="View Mobile Question Order (Active Only)">
            <IconButton 
              onClick={handleViewMobileOrder}
              sx={{ color: "info.main" }}
            >
              <PhoneAndroidIcon />
            </IconButton>
          </Tooltip>
          <IconButton 
            onClick={fetchInterviewMaterials} 
            disabled={loading} 
            title="Refresh Data"
            sx={{ color: "primary.main" }}
          >
            <RefreshIcon />
          </IconButton>
        </Stack>
      </Box>
      
      <Paper elevation={2} sx={{ p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              Interview Questions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total: {totalItems} questions • Use ↑↓ arrows to reorder for mobile delivery
            </Typography>
          </Box>
          <CustomButton 
            colorScheme="bgBlue" 
            startIcon={<AddIcon />} 
            onClick={handleOpenAdd} 
            disabled={loading}
          >
            Add Question
          </CustomButton>
        </Stack>
        
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" p={8}>
            <CircularProgress />
            <Typography variant="body2" sx={{ ml: 2 }}>
              Loading interview questions...
            </Typography>
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
            <Button 
              size="small" 
              onClick={fetchInterviewMaterials} 
              sx={{ ml: 2 }}
            >
              Retry
            </Button>
          </Alert>
        ) : (
          <TableComponent
          rows={transformedQuestions}
          columns={interviewColumns}
          paginationEnabled={true}
          paginationModel={paginationModel}
          onPaginationModelChange={setPaginationModel}
          rowCount={totalItems}
          loading={loading}
          disableRowSelectionOnClick
          getRowId={(row) => row.id}
        />
        )}
      </Paper>
      
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { minHeight: 400 }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight={600}>
            {editItem ? "Edit Interview Question" : "Add New Interview Question"}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {editItem ? "Update the interview question" : "Create a new interview question for talent assessment"}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <TextField 
            label="Interview Question" 
            fullWidth 
            multiline 
            minRows={4}
            maxRows={8}
            value={inputValue} 
            onChange={(e) => setInputValue(e.target.value)} 
            autoFocus 
            sx={{ mt: 2 }}
            placeholder="Enter an interview question with at least 5 words..."
            helperText={
              <Box component="span" display="flex" justifyContent="space-between" alignItems="center">
                <span>Question must contain at least 5 words</span>
                <Chip 
                  label={`${wordCount} words`}
                  color={isValidInput ? "success" : "default"}
                  size="small"
                />
              </Box>
            }
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSave} 
            disabled={!isValidInput}
            startIcon={editItem ? <EditIcon /> : <AddIcon />}
          >
            {editItem ? "Update" : "Add"} Question
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MaterialInterviewPage;