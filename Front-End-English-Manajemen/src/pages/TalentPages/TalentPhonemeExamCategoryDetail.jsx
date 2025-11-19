// src/pages/TalentPages/TalentPhonemeExamCategoryDetail.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Box, Grid, Breadcrumbs, Link, Avatar, Paper, CircularProgress, Alert, Button, Chip, IconButton } from "@mui/material";
import { useNavigate, useParams, Link as RouterLink } from "react-router-dom";
import RefreshIcon from "@mui/icons-material/Refresh";
import VisibilityIcon from "@mui/icons-material/Visibility";
import TableComponent from "../../components/Elements/TableComponent";
import CustomTypography from "../../components/Elements/CustomTypography";
import { talentService } from "../../services/talentService";

const TalentPhonemeExamCategoryDetail = () => {
  const navigate = useNavigate();
  const { id, category } = useParams();
  const [talentData, setTalentData] = useState(null);
  const [examData, setExamData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalData, setTotalData] = useState(0);

  const decodedCategory = decodeURIComponent(category || "");

  const fetchData = useCallback(async () => {
    if (!id || !decodedCategory) return;
    setLoading(true);
    setError(null);
    try {
      const response = await talentService.getTalentDetailProgress(id, "phoneme-exam", decodedCategory, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });

      setTalentData(response.talentInfo);
      setExamData(response.examDetail?.examTotals || []);
      setTotalData(response.pagination?.totalRecords || 0);
    } catch (err) {
      setError(err.message || "Failed to load phoneme exam details");
    } finally {
      setLoading(false);
    }
  }, [id, decodedCategory, paginationModel]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getScoreColor = (score) => {
    const value = parseFloat(score?.replace('%', '') || 0);
    if (value >= 80) return "success";
    if (value >= 70) return "warning";
    return "error";
  };

  const getInitials = (name) => (name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : 'T');

  const columns = [
    { field: "examName", headerName: "Exam Name", flex: 2, renderCell: (params) => <CustomTypography variant="body2" fontWeight={500}>{params.row.examName}</CustomTypography> },
    { field: "date", headerName: "Date", flex: 1.5 },
    { field: "score", headerName: "Score", flex: 1, renderCell: (params) => <Chip label={params.row.score} size="small" color={getScoreColor(params.row.score)} /> },
    {
      field: "action",
      headerName: "Action",
      sortable: false,
      renderCell: (params) => (
        <IconButton 
          onClick={() => navigate(`/talent/${id}/phoneme-exam/attempt/${params.row.examId}/detail`)}
          title="View Attempt Details"
        >
          <VisibilityIcon />
        </IconButton>
      )
    },
  ];

  if (loading && !talentData) {
    return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;
  }

  if (error && !talentData) {
    return <Box p={4}><Alert severity="error">{error}</Alert></Box>;
  }

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/talents" underline="hover" color="inherit">Talent List</Link>
        <Link component={RouterLink} to={`/talent/${id}`} underline="hover" color="inherit">{talentData?.nama}</Link>
        <CustomTypography color="text.primary">Phoneme Exam Detail</CustomTypography>
      </Breadcrumbs>
      <Grid container spacing={2} alignItems="center" mb={3}>
        <Grid item><Avatar sx={{ width: 64, height: 64, bgcolor: "primary.main" }}>{getInitials(talentData?.nama)}</Avatar></Grid>
        <Grid item xs>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box>
              <CustomTypography variant="h6" fontWeight={600}>{talentData?.nama}</CustomTypography>
              <CustomTypography variant="body2" color="text.secondary">{talentData?.email}</CustomTypography>
            </Box>
            <IconButton onClick={fetchData} disabled={loading} title="Refresh Data"><RefreshIcon /></IconButton>
          </Box>
        </Grid>
      </Grid>
      <Paper elevation={1} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <CustomTypography variant="subtitle1" fontWeight={600}>Phoneme Exam Detail: {decodedCategory}</CustomTypography>
          <CustomTypography variant="body2" color="text.secondary">Total Attempts: {totalData}</CustomTypography>
        </Box>
        {loading ? <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box> :
         error ? <Alert severity="error" sx={{ mb: 2 }}>{error}<Button onClick={fetchData} size="small" sx={{ ml: 2 }}>Retry</Button></Alert> :
         <TableComponent
            rows={examData.map((ex, i) => ({ id: ex.examId || i, ...ex }))}
            columns={columns}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalData}
            loading={loading}
          />
        }
      </Paper>
    </Box>
  );
};

export default TalentPhonemeExamCategoryDetail;