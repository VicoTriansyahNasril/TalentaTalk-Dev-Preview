// src/pages/TalentPages/TalentPhonemeExamAttemptDetail.jsx
import React, { useState, useEffect, useCallback } from "react";
import { 
  Box, Grid, Breadcrumbs, Link, Avatar, Paper, CircularProgress, Alert, 
  Typography, Divider, Chip, Stack
} from "@mui/material";
import { useParams, Link as RouterLink } from "react-router-dom";
import { talentService } from "../../services/talentService";
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import WorkspacePremiumIcon from '@mui/icons-material/WorkspacePremium';

const ScoreChip = ({ score }) => {
  const value = parseFloat(String(score).replace('%', ''));
  let color = 'default';
  let icon = <StarBorderIcon sx={{ fontSize: '1rem' }} />;
  let label = score;

  if (value >= 90) {
    color = 'success';
    icon = <WorkspacePremiumIcon sx={{ fontSize: '1rem' }} />;
  } else if (value >= 80) {
    color = 'success';
    icon = <CheckCircleOutlineIcon sx={{ fontSize: '1rem' }} />;
  } else if (value >= 70) {
    color = 'warning';
  } else {
    color = 'error';
    icon = <HighlightOffIcon sx={{ fontSize: '1rem' }} />;
  }
  
  return <Chip icon={icon} label={label} color={color} sx={{ fontWeight: 600, minWidth: '75px' }} />;
};

const TalentPhonemeExamAttemptDetail = () => {
  const { id, attemptId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detail, setDetail] = useState(null);

  const fetchData = useCallback(async () => {
    if (!id || !attemptId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await talentService.getTalentExamAttemptDetail(id, attemptId);
      setDetail(response);
    } catch (err) {
      setError(err.message || "Failed to load exam attempt details");
    } finally {
      setLoading(false);
    }
  }, [id, attemptId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getInitials = (name) => (name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : 'T');

  if (loading) {
    return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;
  }

  if (error) {
    return <Box p={4}><Alert severity="error">{error}</Alert></Box>;
  }

  if (!detail || !detail.examAttemptDetail) {
    return <Box p={4}><Alert severity="info">No exam detail data found.</Alert></Box>;
  }

  const { talentInfo, examAttemptDetail } = detail;

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/talents" underline="hover" color="inherit">Talent List</Link>
        <Link component={RouterLink} to={`/talent/${id}`} underline="hover" color="inherit">{talentInfo?.nama}</Link>
        <Link component={RouterLink} to={`/talent/${id}/phoneme-exam/${encodeURIComponent(examAttemptDetail.phonemeCategory)}`} underline="hover" color="inherit">Phoneme Exam</Link>
        <Typography color="text.primary">Attempt Detail</Typography>
      </Breadcrumbs>
      
      <Paper sx={{ p: 3, borderRadius: 3, backgroundColor: 'white' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Avatar sx={{ width: 64, height: 64, bgcolor: "primary.main", fontSize: '2rem' }}>{getInitials(talentInfo?.nama)}</Avatar>
              <Box>
                <Typography variant="h5" fontWeight={600} sx={{ fontFamily: 'monospace' }}>{examAttemptDetail.phonemeCategory}</Typography>
                <Typography variant="body1" color="text.secondary">Exam Attempt Detail</Typography>
              </Box>
            </Stack>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
            <Typography variant="overline" color="text.secondary" display="block">Total Score</Typography>
            <Typography variant="h4" fontWeight={700} color="primary.main">{examAttemptDetail.totalScore}</Typography>
            <Typography variant="caption" color="text.secondary">Date: {examAttemptDetail.date}</Typography>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom fontWeight={600} color="primary.main">Sentence Breakdown</Typography>
        
        <Stack spacing={2} mt={2}>
          {examAttemptDetail.sentences.map((item, index) => (
            <Paper key={index} variant="outlined" sx={{ p: 2.5, borderRadius: 2, display: 'flex', alignItems: 'center', gap: 2.5, transition: 'box-shadow 0.2s', '&:hover': { boxShadow: '0 2px 8px rgba(0,0,0,0.05)' } }}>
              <Avatar sx={{ bgcolor: 'grey.200', color: 'text.secondary', fontWeight: 600 }}>{index + 1}</Avatar>
              <Box flexGrow={1}>
                <Typography variant="body1" fontWeight={500} gutterBottom>{item.sentence}</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'text.secondary', opacity: 0.8 }}>{item.phonemeTranscription}</Typography>
              </Box>
              <Box sx={{ ml: 2 }}>
                <ScoreChip score={item.score} />
              </Box>
            </Paper>
          ))}
        </Stack>
      </Paper>
    </Box>
  );
};

export default TalentPhonemeExamAttemptDetail;