// src/pages/MaterialPages/MaterialPronunciationPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
  IconButton,
  CircularProgress,
  Alert,
  Button,
  Tooltip,
  Chip,
  Grid,
  Paper
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import UploadIcon from "@mui/icons-material/Upload";
import RefreshIcon from "@mui/icons-material/Refresh";
import AddIcon from "@mui/icons-material/Add";
import Swal from "sweetalert2";
import TemplateDownloadHelper from "../../utils/TemplateDownloadHelper";

import TableComponent from "../../components/Elements/TableComponent";
import CustomButton from "../../components/Elements/CustomButton";
import CustomTabs from "../../components/Elements/CustomTabs";
import CustomSearchbar from "../../components/Elements/CustomSearchbar";
import ImprovedImportModal from "../../components/Elements/ImprovedImportModal";
import InstructionModal from "../../components/Elements/InstructionModal";
import AddPhonemeMaterialForm from "./Form/AddMaterialPhoneme";
import AddExerciseMaterialForm from "./Form/AddExercisePhoneme";
import AddExamMaterialForm from "./Form/AddExamPhoneme";
import { materialService } from "../../services/materialService";

const TABS_CONFIG = [
  {
    label: "PHONEME MATERIAL",
    service: materialService.getPhonemeWordMaterials,
    dataKey: "phonemeMaterials",
    addService: materialService.addPhonemeWordMaterial,
    templateService: materialService.getPhonemeWordTemplate,
    importService: materialService.importPhonemeWordMaterial,
    routePrefix: "/material/pronunciation",
    materialType: "Phoneme Material",
    description: "Manage individual words with phoneme categories and transcriptions"
  },
  {
    label: "EXERCISE PHONEME",
    service: materialService.getPhonemeSentenceMaterials,
    dataKey: "exercisePhonemes",
    addService: materialService.addPhonemeSentenceMaterial,
    templateService: materialService.getExercisePhonemeTemplate,
    importService: materialService.importPhonemeSentenceMaterial,
    routePrefix: "/material/exercise",
    materialType: "Exercise Phoneme",
    description: "Manage practice sentences for similar phonemes training"
  },
  {
    label: "EXAM PHONEME",
    service: materialService.getPhonemeExamMaterials,
    dataKey: "examPhonemes",
    addService: materialService.addPhonemeExamMaterial,
    templateService: materialService.getExamPhonemeTemplate,
    importService: materialService.importPhonemeExamMaterial,
    routePrefix: "/exam-phoneme",
    materialType: "Exam Phoneme",
    description: "Manage exam sets with 10 sentences for assessment"
  },
];

const MaterialPronunciationPage = () => {
  const [tabIndex, setTabIndex] = useState(0);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isInstructionOpen, setIsInstructionOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalItems, setTotalItems] = useState(0);
  const navigate = useNavigate();

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { service, dataKey } = TABS_CONFIG[tabIndex];
      const response = await service({
        search: searchTerm,
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });

      let responseData = response.data?.[dataKey] || response.data?.data?.[dataKey] || response.data?.data || response.data || [];
      let paginationData = response.data?.pagination || response.data?.data?.pagination || {};

      setRows(responseData);
      setTotalItems(paginationData.totalRecords || responseData.length || 0);
    } catch (err) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [tabIndex, searchTerm, paginationModel]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleTabChange = (_, newIndex) => {
    setTabIndex(newIndex);
    setSearchTerm("");
    setPaginationModel({ page: 0, pageSize: 10 });
  };

  const handleAddSubmit = async (data) => {
    try {
      const { addService } = TABS_CONFIG[tabIndex];
      await addService(data);
      Swal.fire("Success!", "Material added successfully.", "success");
      fetchData();
      setIsAddOpen(false);
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to add material.", "error");
    }
  };

  const handleImportMaterials = async (file) => {
    try {
      const { importService } = TABS_CONFIG[tabIndex];
      const response = await importService(file);
      setIsImportOpen(false);
  
      let html = `<div style="text-align: left;">
          <p><strong>Total Data Diproses:</strong> ${response.data.totalProcessed}</p>
          <p style="color: green;"><strong>Berhasil Ditambahkan:</strong> ${response.data.successCount}</p>
          <p style="color: red;"><strong>Gagal:</strong> ${response.data.errorCount}</p>`;
  
      if (response.data.errorCount > 0 && response.data.errors) {
        html += `<h5 style="margin-top: 15px;">Detail Kegagalan:</h5><ul style="max-height: 150px; overflow-y: auto; padding-left: 20px;">`;
        response.data.errors.forEach(err => { html += `<li>Baris ${err.row}: ${err.error}</li>`; });
        html += `</ul>`;
      }
      html += `</div>`;
  
      Swal.fire({
        title: "Hasil Impor",
        html: html,
        icon: response.data.errorCount > 0 ? "warning" : "success",
      }).then(() => {
        if (response.data.successCount > 0) fetchData();
      });
    } catch (error) {
      setIsImportOpen(false);
      Swal.fire("Error!", error.message || "Gagal mengimpor data.", "error");
    }
  };

  const handleShowImportInstructions = () => {
    setIsImportOpen(false);
    setIsInstructionOpen(true);
  };
  
  const handleCloseInstructions = () => {
    setIsInstructionOpen(false);
    setIsImportOpen(true);
  };

  const getColumns = () => {
    const { routePrefix } = TABS_CONFIG[tabIndex];
    const baseColumns = [
      { field: "phonemeCategory", headerName: "Category", flex: 2, renderCell: (params) => <Typography variant="body2" sx={{ fontFamily: "monospace", fontWeight: 600 }}>{params.value}</Typography> },
      { field: "lastUpdate", headerName: "Last Update", flex: 1 }
    ];
    const actionColumn = {
      field: "action", headerName: "Action", width: 100, sortable: false,
      renderCell: (params) => (
        <Tooltip title="View Details">
          <IconButton onClick={() => navigate(`${routePrefix}/${encodeURIComponent(params.row.phonemeCategory)}`)} size="small" sx={{ color: "primary.main" }}><VisibilityIcon /></IconButton>
        </Tooltip>
      ),
    };
    switch (tabIndex) {
      case 0: return [{...baseColumns[0]}, { field: "totalWords", headerName: "Total Words", flex: 1 }, {...baseColumns[1]}, actionColumn];
      case 1: return [{...baseColumns[0]}, { field: "totalSentence", headerName: "Total Sentences", flex: 1 }, {...baseColumns[1]}, actionColumn];
      case 2: return [{...baseColumns[0]}, { field: "totalExam", headerName: "Total Exams", flex: 1 }, {...baseColumns[1]}, actionColumn];
      default: return baseColumns;
    }
  };

  const renderAddForm = () => {
    if (!isAddOpen) return null;
    switch (tabIndex) {
      case 0: return <AddPhonemeMaterialForm open={isAddOpen} onClose={() => setIsAddOpen(false)} onSubmit={handleAddSubmit} />;
      case 1: return <AddExerciseMaterialForm open={isAddOpen} onClose={() => setIsAddOpen(false)} onSubmit={handleAddSubmit} />;
      case 2: return <AddExamMaterialForm open={isAddOpen} onClose={() => setIsAddOpen(false)} onSubmit={handleAddSubmit} />;
      default: return null;
    }
  };

  const currentTabConfig = TABS_CONFIG[tabIndex];

  return (
    <Box p={4}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h6" fontWeight={600}>PRONUNCIATION MATERIAL MANAGEMENT</Typography>
          <Typography variant="body2" color="text.secondary">Manage phoneme materials, exercises, and exams</Typography>
        </Box>
        <IconButton onClick={fetchData} disabled={loading} title="Refresh Data"><RefreshIcon /></IconButton>
      </Box>

      <CustomTabs value={tabIndex} onChange={handleTabChange} tabs={TABS_CONFIG.map((t) => ({ label: t.label }))} />

      <Card sx={{ mt: 3, borderRadius: 3 }}>
        <CardContent>
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={8}><Typography variant="subtitle1" fontWeight={600}>{currentTabConfig.label}</Typography><Typography variant="body2" color="text.secondary">{currentTabConfig.description}</Typography></Grid>
              <Grid item xs={12} md={4}><Box display="flex" justifyContent="flex-end"><Chip label={`${totalItems} items`} color="primary" size="small" /></Box></Grid>
            </Grid>
          </Paper>

          <Stack direction="row" justifyContent="space-between" spacing={2} mb={3}>
            <CustomSearchbar placeholder={`Search ${currentTabConfig.label.toLowerCase()}...`} searchValue={searchTerm} onSearchChange={(e) => setSearchTerm(e.target.value)} />
            <Stack direction="row" spacing={1}>
              <CustomButton colorScheme="bgBlue" startIcon={<AddIcon />} onClick={() => setIsAddOpen(true)} disabled={loading}>Add</CustomButton>
              <CustomButton colorScheme="bgOrange" startIcon={<UploadIcon />} onClick={() => setIsImportOpen(true)} disabled={loading}>Import</CustomButton>
            </Stack>
          </Stack>

          {loading ? <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box> :
           error ? <Alert severity="error">{error}<Button onClick={fetchData} size="small" sx={{ ml: 2 }}>Retry</Button></Alert> :
           <TableComponent
              rows={rows.map((row, i) => ({ id: row.phonemeCategory || i, ...row }))}
              columns={getColumns()}
              paginationEnabled
              paginationModel={paginationModel}
              onPaginationModelChange={setPaginationModel}
              rowCount={totalItems}
              loading={loading}
           />
          }
        </CardContent>
      </Card>

      {renderAddForm()}

      <ImprovedImportModal
        open={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        uploadLabel={`Import ${currentTabConfig.materialType}`}
        materialType={currentTabConfig.materialType}
        onFileUpload={handleImportMaterials}
        templateService={currentTabConfig.templateService}
        onShowInstructions={handleShowImportInstructions}
      />

      <InstructionModal
        open={isInstructionOpen}
        onClose={handleCloseInstructions}
        title={`${currentTabConfig.materialType} Import Guide`}
        content={TemplateDownloadHelper.getImportInstructions(currentTabConfig.materialType)}
      />
    </Box>
  );
};

export default MaterialPronunciationPage;