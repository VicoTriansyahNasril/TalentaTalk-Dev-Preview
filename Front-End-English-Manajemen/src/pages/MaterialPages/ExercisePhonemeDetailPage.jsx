// src/pages/TalentPages/TalentPhonemeMaterialExerciseDetail.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Box, Grid, Breadcrumbs, Link, Avatar, Paper, CircularProgress, Alert, Button, Chip, IconButton, Typography, Divider, Stack } from "@mui/material";
import { useNavigate, useParams, Link as RouterLink } from "react-router-dom";
import RefreshIcon from "@mui/icons-material/Refresh";
import TableComponent from "../../components/Elements/TableComponent";
import CustomTypography from "../../components/Elements/CustomTypography";
import { talentService } from "../../services/talentService";
import StarIcon from '@mui/icons-material/Star';

const TalentPhonemeMaterialExerciseDetail = () => {
  const navigate = useNavigate();
  const { id, phoneme } = useParams();
  const [talentData, setTalentData] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalData, setTotalData] = useState(0);
  const [categoryStats, setCategoryStats] = useState({ avgScore: '0%', attempted: '0/0' });

  const decodedPhoneme = decodeURIComponent(phoneme || "");

  const fetchData = useCallback(async () => {
    if (!id || !decodedPhoneme) return;
    setLoading(true);
    setError(null);
    try {
      const response = await talentService.getTalentDetailProgress(id, "phoneme-material-exercise", decodedPhoneme, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });

      const wordsData = response.phonemeDetail?.words || [];
      setTalentData(response.talentInfo);
      setExercises(wordsData);
      setTotalData(response.pagination?.totalRecords || 0);

      // Calculate statistics on the frontend from the fetched page data
      if (wordsData.length > 0) {
        let totalScore = 0;
        let attemptedCount = 0;
        wordsData.forEach(word => {
          if (word.latestAttempted !== "N/A") {
            totalScore += parseFloat(word.bestScore.replace('%', '')) || 0;
            attemptedCount++;
          }
        });
        const avgScore = attemptedCount > 0 ? totalScore / attemptedCount : 0;
        setCategoryStats({
          avgScore: `${Math.round(avgScore)}%`,
          attempted: `${attemptedCount} attempted`
        });
      } else {
        setCategoryStats({ avgScore: '0%', attempted: '0 attempted' });
      }

    } catch (err) {
      setError(err.message || "Failed to load phoneme material details");
    } finally {
      setLoading(false);
    }
  }, [id, decodedPhoneme, paginationModel]);

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
    { field: "word", headerName: "Word", flex: 1, renderCell: (params) => <CustomTypography variant="body2" fontWeight={500}>{params.row.word}</CustomTypography> },
    { field: "latestAttempted", headerName: "Latest Attempted", flex: 1.5, renderCell: (params) => <CustomTypography variant="body2">{params.row.latestAttempted}</CustomTypography> },
    { field: "bestScore", headerName: "Best Score", flex: 1, renderCell: (params) => <Chip label={params.row.bestScore} size="small" color={getScoreColor(params.row.bestScore)} /> },
    { field: "latestScore", headerName: "Latest Score", flex: 1, renderCell: (params) => <Chip label={params.row.latestScore} size="small" color={getScoreColor(params.row.latestScore)} /> },
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
        <CustomTypography color="text.primary">Phoneme Material Detail</CustomTypography>
      </Breadcrumbs>

      <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar sx={{ width: 56, height: 56, bgcolor: "primary.main" }}>{getInitials(talentData?.nama)}</Avatar>
            <Box>
              <CustomTypography variant="h6" fontWeight={600}>{talentData?.nama}</CustomTypography>
              <CustomTypography variant="body2" color="text.secondary">{talentData?.email}</CustomTypography>
            </Box>
          </Stack>
          <IconButton onClick={fetchData} disabled={loading} title="Refresh Data"><RefreshIcon /></IconButton>
        </Stack>
      </Paper>
      
      <Paper elevation={1} sx={{ p: 3 }}>
        <Box>
          <Typography variant="h6" fontWeight={600}>Phoneme Material: {decodedPhoneme}</Typography>
          <Typography variant="body2" color="text.secondary">Detailed performance on individual word pronunciation.</Typography>
        </Box>
        <Divider sx={{ my: 2 }} />
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6} md={4}>
            <Typography variant="caption" color="text.secondary">Avg. Accuracy (this page)</Typography>
            <Chip icon={<StarIcon />} label={categoryStats.avgScore} color={getScoreColor(categoryStats.avgScore)} sx={{ fontWeight: 600, mt: 0.5 }} />
          </Grid>
          <Grid item xs={6} md={4}>
            <Typography variant="caption" color="text.secondary">Words Attempted (this page)</Typography>
            <Typography variant="body1" fontWeight={600}>{categoryStats.attempted}</Typography>
          </Grid>
        </Grid>
        
        {loading ? <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box> :
         error ? <Alert severity="error" sx={{ mb: 2 }}>{error}<Button onClick={fetchData} size="small" sx={{ ml: 2 }}>Retry</Button></Alert> :
         exercises.length === 0 ? (
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={8} sx={{ border: '2px dashed', borderColor: 'grey.300', borderRadius: 2, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>No Activity Yet</Typography>
            <Typography variant="body2" color="text.secondary">This talent has not practiced any words in the "{decodedPhoneme}" category.</Typography>
          </Box>
         ) : (
          <TableComponent
            rows={exercises.map((ex, i) => ({ id: i, ...ex }))}
            columns={columns}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalData}
            loading={loading}
          />
        )}
      </Paper>
    </Box>
  );
};

export default TalentPhonemeMaterialExerciseDetail;