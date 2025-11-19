// src/pages/TalentPages/TalentInterviewDetail.jsx
import React, { useState, useEffect, useCallback } from "react";
import { 
  Box, Grid, Breadcrumbs, Link, Avatar, Paper, CircularProgress, Alert, 
  Typography, Divider, Chip, Stack, List, ListItem, ListItemIcon, ListItemText 
} from "@mui/material";
import { useParams, Link as RouterLink } from "react-router-dom";
import { talentService } from "../../services/talentService";

// Import Icons for better UI
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined';
import BarChartOutlinedIcon from '@mui/icons-material/BarChartOutlined';
import SpeedOutlinedIcon from '@mui/icons-material/SpeedOutlined';
import SpellcheckOutlinedIcon from '@mui/icons-material/SpellcheckOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

// Helper component for displaying key metrics
const MetricDisplay = ({ icon, title, value, chipProps }) => (
  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', height: '100%' }}>
    <Stack direction="row" spacing={1.5} alignItems="center" justifyContent="center" mb={1}>
      {icon}
      <Typography variant="body2" color="text.secondary">{title}</Typography>
    </Stack>
    <Chip {...chipProps} label={value} sx={{ fontWeight: 'bold', fontSize: '1rem', px: 1, height: 32 }} />
  </Paper>
);

const FeedbackSection = ({ icon, title, content }) => {
  const points = content.split('•').filter(point => point.trim() !== '');

  return (
    <Box>
      <Stack direction="row" spacing={1.5} alignItems="center" mb={1}>
        {icon}
        <Typography variant="h6" fontWeight={600}>{title}</Typography>
      </Stack>
      <List dense sx={{ pl: 2 }}>
        {points.length > 0 ? points.map((point, index) => (
          <ListItem key={index} sx={{ py: 0.5 }}>
            <ListItemIcon sx={{ minWidth: 32 }}><CheckCircleOutlineIcon fontSize="small" color="action" /></ListItemIcon>
            <ListItemText primary={point.trim()} />
          </ListItem>
        )) : (
          <ListItem>
            <ListItemText primary={content} sx={{ fontStyle: 'italic', color: 'text.secondary' }} />
          </ListItem>
        )}
      </List>
    </Box>
  );
};


const TalentInterviewDetail = () => {
  const { id, attemptId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detail, setDetail] = useState(null);

  const fetchData = useCallback(async () => {
    if (!id || !attemptId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await talentService.getTalentInterviewDetail(id, attemptId);
      setDetail(response);
    } catch (err) {
      setError(err.message || "Failed to load interview details");
    } finally {
      setLoading(false);
    }
  }, [id, attemptId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getInitials = (name) => (name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : 'T');

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    try {
      return new Date(dateString).toLocaleString('id-ID', {
        day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch (error) { return dateString; }
  };

  const getWpmChipProps = (wpm) => {
    const value = parseInt(wpm, 10) || 0;
    if (value >= 140) return { color: "success", icon: <SpeedOutlinedIcon /> };
    if (value >= 100) return { color: "warning", icon: <SpeedOutlinedIcon /> };
    return { color: "default", icon: <SpeedOutlinedIcon /> };
  };

  const getGrammarChipProps = (grammar) => {
    const value = grammar?.toLowerCase() || "";
    if (value === "good" || value === "excellent") return { color: "success", icon: <SpellcheckOutlinedIcon /> };
    if (value === "fair") return { color: "warning", icon: <SpellcheckOutlinedIcon /> };
    return { color: "error", icon: <SpellcheckOutlinedIcon /> };
  };

  if (loading) {
    return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;
  }

  if (error) {
    return <Box p={4}><Alert severity="error">{error}</Alert></Box>;
  }

  if (!detail || !detail.interviewDetail) {
    return <Box p={4}><Alert severity="info">No interview detail data found.</Alert></Box>;
  }

  const { talentInfo, interviewDetail } = detail;
  const feedback = interviewDetail.feedback || {};

  const cleanPerformanceText = (text) => {
    if (!text) return "Not evaluated";
    return text.split('INTERVIEW STATISTICS:')[0].trim();
  };

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/talents" underline="hover" color="inherit">Talent List</Link>
        <Link component={RouterLink} to={`/talent/${id}`} underline="hover" color="inherit">{talentInfo?.nama}</Link>
        <Typography color="text.primary">Interview Attempt #{interviewDetail.attemptNumber}</Typography>
      </Breadcrumbs>
      
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Avatar sx={{ width: 64, height: 64, bgcolor: "primary.main" }}>{getInitials(talentInfo?.nama)}</Avatar>
              <Box>
                <Typography variant="h5" fontWeight={600}>{talentInfo?.nama}</Typography>
                <Typography variant="body1" color="text.secondary">{talentInfo?.email}</Typography>
              </Box>
            </Stack>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
            <Typography variant="h6">Interview Attempt #{interviewDetail.attemptNumber}</Typography>
            <Typography variant="body2" color="text.secondary">Date: {formatDate(interviewDetail.date)}</Typography>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h5" gutterBottom fontWeight={600} color="primary.main">Key Metrics</Typography>
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6}>
            <MetricDisplay 
              icon={<SpeedOutlinedIcon color="primary"/>}
              title="Words Per Minute (WPM)"
              value={`${feedback.wpm || 0} WPM`}
              chipProps={getWpmChipProps(feedback.wpm)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <MetricDisplay
              icon={<SpellcheckOutlinedIcon color="primary"/>}
              title="Grammar Assessment"
              value={feedback.grammar || "N/A"}
              chipProps={getGrammarChipProps(feedback.grammar)}
            />
          </Grid>
        </Grid>

        <Typography variant="h5" gutterBottom fontWeight={600} color="primary.main">Performance Analysis</Typography>
        <Grid container spacing={4}>
          <Grid item xs={12}>
            <FeedbackSection 
              icon={<ThumbUpOutlinedIcon color="success" />}
              title="Strengths"
              content={feedback.strength || "Not evaluated"}
            />
          </Grid>
          <Grid item xs={12}>
            <FeedbackSection 
              icon={<ReportProblemOutlinedIcon color="warning" />}
              title="Areas for Improvement"
              content={feedback.weakness || "Not evaluated"}
            />
          </Grid>
          <Grid item xs={12}>
            <FeedbackSection 
              icon={<BarChartOutlinedIcon color="info" />}
              title="Overall Performance"
              content={cleanPerformanceText(feedback.performance)}
            />
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default TalentInterviewDetail;