// src/pages/MaterialPages/PhonemeDetailPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import { useParams, Link as RouterLink } from "react-router-dom";
import { Box, Typography, Paper, IconButton, Breadcrumbs, Link as MuiLink, CircularProgress, Alert, Button, Stack } from "@mui/material";
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

  const fetchWords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await materialService.getPhonemeWordsByCategory(decodedPhoneme, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });
      setWords(response.data.data || []);
      setTotalItems(response.data.pagination?.totalRecords || 0);
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

  const columns = [
    { field: "word", headerName: "Word", flex: 1 },
    { field: "meaning", headerName: "Word Meaning", flex: 2 },
    { field: "definition", headerName: "Definition", flex: 3 },
    {
      field: "action",
      headerName: "Action",
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={1}>
          <IconButton size="small" title="Edit Word"><EditIcon /></IconButton>
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
        <CustomTypography color="text.primary">Phoneme: {decodedPhoneme}</CustomTypography>
      </Breadcrumbs>
      
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Phoneme Word Detail</Typography>
        <IconButton onClick={fetchWords} disabled={loading} title="Refresh Data">
          <RefreshIcon />
        </IconButton>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
      ) : error ? (
        <Alert severity="error">{error}<Button onClick={fetchWords} sx={{ ml: 2 }}>Retry</Button></Alert>
      ) : (
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <TableComponent
            rows={words}
            columns={columns}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalItems}
            loading={loading}
          />
        </Paper>
      )}
    </Box>
  );
};

export default PhonemeDetailPage;