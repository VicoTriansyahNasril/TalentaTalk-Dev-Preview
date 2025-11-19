// src/pages/TalentPages/TalentListPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Stack,
  IconButton,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import UploadIcon from "@mui/icons-material/Upload";
import VisibilityIcon from "@mui/icons-material/Visibility";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import RefreshIcon from "@mui/icons-material/Refresh";
import Swal from "sweetalert2";
import { useNavigate } from "react-router-dom";

import CustomTypography from "../../components/Elements/CustomTypography";
import CustomSearchbar from "../../components/Elements/CustomSearchbar";
import CustomButton from "../../components/Elements/CustomButton";
import TableComponent from "../../components/Elements/TableComponent";
import AddOrEditTalentForm from "./AddOrEditTalentForm";
import ImprovedImportModal from "../../components/Elements/ImprovedImportModal"; 
import InstructionModal from "../../components/Elements/InstructionModal";
import { talentService } from "../../services/talentService";
import TemplateDownloadHelper from "../../utils/TemplateDownloadHelper";

const TalentListPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isInstructionOpen, setIsInstructionOpen] = useState(false);
  const [selectedTalent, setSelectedTalent] = useState(null);
  const [isEdit, setIsEdit] = useState(false);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [talents, setTalents] = useState([]);
  const [totalTalents, setTotalTalents] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchTalents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await talentService.getTalentList({
        search: searchTerm,
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });
      setTalents(response.talents || []);
      setTotalTalents(response.pagination?.totalRecords || 0);
    } catch (err) {
      setError(err.message || "Failed to load talents");
      setTalents([]);
      setTotalTalents(0);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, paginationModel]);

  useEffect(() => {
    fetchTalents();
  }, [fetchTalents]);
  
  const handleRefresh = () => fetchTalents();

  const handleAddOpen = () => {
    setSelectedTalent(null);
    setIsEdit(false);
    setIsAddOpen(true);
  };

  const handleEditOpen = (row) => {
    setSelectedTalent(row);
    setIsEdit(true);
    setIsAddOpen(true);
  };

  const handleViewTalent = (row) => {
    navigate(`/talent/${row.id}`);
  };

  const handleDelete = async (row) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: `Delete ${row.talentName}? This action cannot be undone.`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      confirmButtonText: "Yes, delete it!",
    });

    if (result.isConfirmed) {
      try {
        await talentService.deleteTalent(row.id);
        Swal.fire("Deleted!", `${row.talentName} has been removed.`, "success");
        fetchTalents();
      } catch (error) {
        Swal.fire("Error!", error.message || "Failed to delete talent.", "error");
      }
    }
  };

  const handleAddTalent = async (data) => {
    try {
      await talentService.addTalent(data);
      setIsAddOpen(false);
      Swal.fire("Success!", "Talent added successfully.", "success").then(() => {
        fetchTalents();
      });
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to add talent.", "error");
    }
  };

  const handleEditProfile = async (data) => {
    try {
      await talentService.editTalent(selectedTalent.id, data);
      setIsAddOpen(false);
      Swal.fire("Success!", "Talent profile updated successfully.", "success").then(() => {
        fetchTalents();
      });
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to update profile.", "error");
      throw error;
    }
  };

  const handleChangePassword = async (data) => {
    try {
      await talentService.changeTalentPassword(selectedTalent.id, data);
      setIsAddOpen(false);
      Swal.fire("Success!", "Talent password changed successfully.", "success");
    } catch (error) {
      Swal.fire("Error!", error.message || "Failed to change password.", "error");
      throw error;
    }
  };
  
  const handleImportTalents = async (file) => {
    try {
      const response = await talentService.importTalents(file);
      setIsImportOpen(false);

      let html = `
        <div style="text-align: left;">
          <p><strong>Total Data Diproses:</strong> ${response.totalProcessed}</p>
          <p style="color: green;"><strong>Berhasil Ditambahkan:</strong> ${response.successCount}</p>
          <p style="color: red;"><strong>Gagal:</strong> ${response.errorCount}</p>
      `;

      if (response.errorCount > 0 && response.errors) {
        html += `
          <h5 style="margin-top: 15px;">Detail Kegagalan:</h5>
          <ul style="max-height: 150px; overflow-y: auto; padding-left: 20px;">
        `;
        response.errors.forEach(err => {
          html += `<li>Baris ${err.row}: ${err.error}</li>`;
        });
        html += `</ul>`;
      }
      html += `</div>`;

      Swal.fire({
        title: "Hasil Impor",
        html: html,
        icon: response.errorCount > 0 ? "warning" : "success",
      }).then(() => {
        if (response.successCount > 0) {
          fetchTalents();
        }
      });
    } catch (error) {
      setIsImportOpen(false);
      Swal.fire("Error!", error.message || "Gagal mengimpor data talenta.", "error");
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
  
  const getProgressColor = (progress) => {
    const value = parseFloat(progress?.replace('%', '') || 0);
    if (value >= 80) return "success";
    if (value >= 50) return "warning";
    return "error";
  };

  const columns = [
    { field: "talentName", headerName: "Talent Name", flex: 1.5 },
    { field: "pretest", headerName: "Pretest", flex: 1 },
    // PERUBAHAN DI SINI: Mengganti field dan headerName
    { field: "highestExam", headerName: "Highest Exam Score", flex: 1 },
    {
      field: "progress",
      headerName: "Progress",
      flex: 1,
      renderCell: (params) => (<Chip label={params.row.progress} size="small" color={getProgressColor(params.row.progress)} />),
    },
    {
      field: "action",
      headerName: "Action",
      sortable: false,
      flex: 1,
      renderCell: (params) => (
        <Box>
          <IconButton onClick={() => handleViewTalent(params.row)} title="View Details" size="small"><VisibilityIcon /></IconButton>
          <IconButton onClick={() => handleEditOpen(params.row)} title="Edit Talent" size="small"><EditIcon /></IconButton>
          <IconButton onClick={() => handleDelete(params.row)} title="Delete Talent" size="small" sx={{ color: "error.main" }}><DeleteIcon /></IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box p={4}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <CustomTypography variant="h5" fontWeight={600}>Talent Management</CustomTypography>
        <IconButton onClick={handleRefresh} disabled={loading} title="Refresh Data"><RefreshIcon /></IconButton>
      </Box>
      <Card sx={{ p: 3, borderRadius: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" mb={3} gap={2}>
            <Box width="300px">
              <CustomSearchbar searchValue={searchTerm} onSearchChange={(e) => setSearchTerm(e.target.value)} placeholder="Search by name or email" />
            </Box>
            <Stack direction="row" spacing={1}>
              <CustomButton colorScheme="bgBlue" startIcon={<AddIcon />} onClick={handleAddOpen} disabled={loading}>Add Talent</CustomButton>
              <CustomButton colorScheme="bgOrange" startIcon={<UploadIcon />} onClick={() => setIsImportOpen(true)} disabled={loading}>Import Excel</CustomButton>
            </Stack>
          </Stack>
          {loading ? <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box> :
           error ? <Alert severity="error">{error}</Alert> :
           <TableComponent
              rows={talents.map(t => ({...t, id: t.id}))}
              columns={columns}
              getRowId={(row) => row.id}
              paginationModel={paginationModel}
              onPaginationModelChange={setPaginationModel}
              rowCount={totalTalents}
              paginationEnabled
              loading={loading}
            />
          }
        </CardContent>
      </Card>
      <AddOrEditTalentForm
        open={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onSubmit={handleAddTalent}
        onEditProfile={handleEditProfile}
        onChangePassword={handleChangePassword}
        defaultValues={selectedTalent}
        isEdit={isEdit}
      />
      <ImprovedImportModal
        open={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        uploadLabel="Import Talent Data"
        materialType="Talent"
        onFileUpload={handleImportTalents}
        templateService={talentService.getTalentTemplate}
        onShowInstructions={handleShowImportInstructions}
      />
      <InstructionModal
        open={isInstructionOpen}
        onClose={handleCloseInstructions}
        title="Talent Import Guide"
        content={TemplateDownloadHelper.getImportInstructions('Talent')}
      />
    </Box>
  );
};

export default TalentListPage;