// src/pages/Home/DashboardHomePage.jsx
import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
  Stack,
  CircularProgress,
  Alert,
  TableContainer,
  Paper,
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Tooltip,
  Badge,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import PeopleIcon from "@mui/icons-material/People";
import BookIcon from "@mui/icons-material/MenuBook";
import AssignmentIcon from "@mui/icons-material/Assignment";
import QuestionAnswerIcon from "@mui/icons-material/QuestionAnswer";
import RefreshIcon from "@mui/icons-material/Refresh";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import MicIcon from "@mui/icons-material/Mic";
import QuizIcon from "@mui/icons-material/Quiz";
import ChatIcon from "@mui/icons-material/Chat";
import SettingsIcon from "@mui/icons-material/Settings";
import InfoIcon from "@mui/icons-material/Info";
import { dashboardService } from "../../services/dashboardService";
import DashboardEnhancements from "../../utils/dashboardEnhancements";

const DashboardHomePage = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [activitySettings, setActivitySettings] = useState(
    DashboardEnhancements.loadSettings()
  );
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [tempSettings, setTempSettings] = useState(activitySettings);

  const limitOptions = DashboardEnhancements.limitOptions;

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        activityLimit: activitySettings.customLimit ? 
          activitySettings.customLimitValue : 
          activitySettings.activityLimit,
        daysBack: activitySettings.daysBack,
        page: 1
      };
      
      const response = await dashboardService.getDashboardData(params);
      setDashboardData(response);
    } catch (err) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }, [activitySettings]);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const handleCardClick = (path) => navigate(path);

  const handleRowClick = (activity) => {
    if (activity.talentId) {
      navigate(`/talent/${activity.talentId}`);
    }
  };

  const handleOpenSettings = () => {
    setTempSettings({ ...activitySettings });
    setSettingsDialogOpen(true);
  };

  const handleCloseSettings = () => {
    setSettingsDialogOpen(false);
    setTempSettings(activitySettings);
  };

  const handleApplySettings = () => {
    const oldSettings = { ...activitySettings };
    setActivitySettings({ ...tempSettings });
    DashboardEnhancements.saveSettings(tempSettings);
    DashboardEnhancements.trackSettingsChange(oldSettings, tempSettings);
    setSettingsDialogOpen(false);
  };

  const handleQuickLimit = (limit) => {
    const oldSettings = { ...activitySettings };
    const newSettings = {
      ...activitySettings,
      activityLimit: limit,
      customLimit: false
    };
    setActivitySettings(newSettings);
    DashboardEnhancements.saveSettings(newSettings);
    DashboardEnhancements.trackSettingsChange(oldSettings, newSettings);
  };

  const getActivityTypeIcon = (activityType) => {
    const iconProps = { 
      fontSize: "small",
      sx: { width: 16, height: 16 }
    };
    
    switch (activityType) {
      case 'Word Practice':
      case 'Sentence Practice':
        return <BookIcon {...iconProps} />;
      case 'Phoneme Exam':
        return <QuizIcon {...iconProps} />;
      case 'Conversation':
        return <ChatIcon {...iconProps} />;
      case 'Interview':
        return <MicIcon {...iconProps} />;
      default:
        return <TrendingUpIcon {...iconProps} />;
    }
  };

  const getActivityTypeColor = (activityType) => {
    const config = DashboardEnhancements.activityTypeConfigs[activityType];
    return config ? config.color : 'default';
  };

  const getScoreColor = (score) => {
    const { color } = DashboardEnhancements.getScoreColorAndMessage(score);
    return color;
  };

  const getWPMColor = (wpm) => {
    const { color } = DashboardEnhancements.getWPMColorAndMessage(wpm);
    return color;
  };

  const formatWPM = (wpm) => {
    if (!wpm) return "0 WPM";
    if (String(wpm).includes('WPM')) return wpm;
    return `${parseFloat(wpm).toFixed(0)} WPM`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    try {
      return new Date(dateString).toLocaleString("id-ID", { 
        year: "numeric", 
        month: "short", 
        day: "numeric", 
        hour: "2-digit", 
        minute: "2-digit" 
      });
    } catch {
      return "Invalid Date";
    }
  };

  if (loading && !dashboardData) {
    return (
      <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress size={40} />
        <Typography variant="body2" sx={{ ml: 2 }}>Loading dashboard...</Typography>
      </Box>
    );
  }

  if (error && !dashboardData) {
    return (
      <Box p={4}>
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        <Button onClick={fetchDashboardData} variant="contained">Retry</Button>
      </Box>
    );
  }

  const statistics = dashboardData?.statistics || {};
  const pronunciationActivities = dashboardData?.pronunciationActivities || [];
  const speakingActivities = dashboardData?.speakingActivities || [];
  const totalActivities = dashboardData?.totalActivities || 0;
  const dateRange = dashboardData?.dateRange || "Last 30 days";
  const hasError = dashboardData?.hasError || false;
  const activitySettingsData = dashboardData?.activitySettings || {};

  const stats = [
    { 
      label: "Total Talent", 
      value: statistics.totalTalent || 0, 
      icon: <PeopleIcon sx={{ fontSize: 32, color: "#1976d2" }} />, 
      to: "/talents" 
    },
    { 
      label: "Total Pronunciation Material", 
      value: statistics.totalPronunciationMaterial || 0, 
      icon: <BookIcon sx={{ fontSize: 32, color: "#1976d2" }} />, 
      to: "/pronunciation-material" 
    },
    { 
      label: "Total Exam Phoneme Material", 
      value: statistics.totalExamPhonemMaterial || 0, 
      icon: <AssignmentIcon sx={{ fontSize: 32, color: "#1976d2" }} />, 
      to: "/pronunciation-material" 
    },
    { 
      label: "Total Interview Question", 
      value: statistics.totalInterviewQuestion || 0, 
      icon: <QuestionAnswerIcon sx={{ fontSize: 32, color: "#1976d2" }} />, 
      to: "/conversation-material" 
    },
  ];

  const currentLimit = activitySettings.customLimit ? 
    activitySettings.customLimitValue : 
    activitySettings.activityLimit;

  const infoMessage = DashboardEnhancements.generateInfoMessage(
    activitySettings, 
    totalActivities, 
    dateRange
  );

  const emptyStateMessage = DashboardEnhancements.generateEmptyStateMessage(
    dateRange, 
    currentLimit
  );

  const quickButtons = DashboardEnhancements.renderQuickLimitButtons(
    currentLimit,
    activitySettings.customLimit,
    handleQuickLimit
  );

  return (
    <Box sx={{ backgroundColor: "#f5f5f5", minHeight: "100vh", p: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h5" fontWeight={600}>Dashboard Overview</Typography>
        <Stack direction="row" spacing={2} alignItems="center">
          {/* Quick Limit Controls */}
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="body2" color="text.secondary">Show:</Typography>
            {quickButtons.map((buttonProps) => (
              <Button
                key={buttonProps.key}
                variant={buttonProps.variant}
                size={buttonProps.size}
                onClick={buttonProps.onClick}
                sx={buttonProps.sx}
              >
                {buttonProps.text}
              </Button>
            ))}
            <Tooltip title="Customize activity display settings">
              <IconButton 
                onClick={handleOpenSettings}
                size="small"
                sx={{ 
                  backgroundColor: activitySettings.customLimit ? 'primary.main' : 'action.hover',
                  color: activitySettings.customLimit ? 'white' : 'inherit',
                  '&:hover': { backgroundColor: activitySettings.customLimit ? 'primary.dark' : 'action.selected' }
                }}
              >
                <SettingsIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
          
          <Divider orientation="vertical" flexItem />
          
          <IconButton 
            onClick={fetchDashboardData} 
            disabled={loading}
            title="Refresh Dashboard"
            sx={{ 
              backgroundColor: loading ? 'transparent' : 'action.hover',
              '&:hover': { backgroundColor: 'action.selected' }
            }}
          >
            <RefreshIcon />
          </IconButton>
        </Stack>
      </Box>

      <Alert 
        severity="info" 
        sx={{ mb: 3 }}
        icon={<InfoIcon />}
        action={
          <Button 
            color="inherit" 
            size="small" 
            onClick={handleOpenSettings}
            endIcon={<SettingsIcon />}
          >
            Configure
          </Button>
        }
      >
        <Typography variant="body2">
          <strong>Current Settings:</strong> {infoMessage}
        </Typography>
      </Alert>

      <Grid container spacing={3} mb={4}>
        {stats.map((item, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ 
              height: "100%", 
              borderRadius: 2, 
              transition: "transform 0.2s, box-shadow 0.2s", 
              "&:hover": { 
                transform: "translateY(-2px)",
                boxShadow: 3
              } 
            }}>
              <CardActionArea onClick={() => handleCardClick(item.to)} sx={{ p: 3, height: "100%" }}>
                <Stack direction="row" spacing={2} alignItems="center" width="100%" mb={1}>
                  <Box sx={{ 
                    width: 56, 
                    height: 56, 
                    borderRadius: 2, 
                    backgroundColor: "#f0f7ff", 
                    display: "flex", 
                    alignItems: "center", 
                    justifyContent: "center" 
                  }}>
                    {item.icon}
                  </Box>
                  <Box flex={1}>
                    <Typography variant="h4" fontWeight={700} color="primary">
                      {item.value.toLocaleString()}
                    </Typography>
                  </Box>
                </Stack>
                <Typography variant="body2" fontWeight={500} color="text.secondary">
                  {item.label}
                </Typography>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {hasError && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Some recent activity data may be incomplete. Please check the logs or try refreshing.
        </Alert>
      )}

      {/* Pronunciation Activities Card */}
      <Card sx={{ borderRadius: 2, boxShadow: 2, mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                📚 Recent Pronunciation Activities
                <Badge 
                  badgeContent={pronunciationActivities.length} 
                  color="primary" 
                  sx={{ ml: 2 }} 
                />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Latest phoneme exercises, practice sessions, and exam results ({dateRange})
              </Typography>
            </Box>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => navigate("/view-detail")}
              endIcon={<TrendingUpIcon />}
            >
              VIEW DETAIL
            </Button>
          </Box>
          
          <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid', borderColor: 'divider' }}>
            <Table size="medium">
              <TableHead>
                <TableRow sx={{ backgroundColor: "#f8f9fa" }}>
                  <TableCell sx={{ fontWeight: 600 }}>Talent Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Activity Type</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Latest Score</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Best Score</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pronunciationActivities.length > 0 ? (
                  pronunciationActivities.map((activity, index) => (
                    <TableRow 
                      key={index} 
                      hover 
                      sx={{ 
                        cursor: "pointer",
                        '&:hover': {
                          backgroundColor: 'action.hover'
                        }
                      }} 
                      onClick={() => handleRowClick(activity)}
                    >
                      <TableCell>
                        {/* ✅ FIX: Only show talent name, no ID */}
                        <Typography variant="body2" fontWeight={500} color="primary">
                          {activity.talentName}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={activity.activityType}
                          size="small"
                          color={getActivityTypeColor(activity.activityType)}
                          icon={getActivityTypeIcon(activity.activityType)}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {activity.category}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={activity.latestScore}
                          size="small"
                          color={getScoreColor(activity.latestScore)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={activity.bestScore}
                          size="small"
                          color={getScoreColor(activity.bestScore)}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(activity.lastActivity)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                      <Box>
                        <BookIcon sx={{ fontSize: 48, color: "#bdbdbd", mb: 2 }} />
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                          No Recent Pronunciation Activity
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          No phoneme exercises or exams completed in the {dateRange.toLowerCase()}.
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {pronunciationActivities.length > 0 && (
            <Box mt={2} p={2} sx={{ backgroundColor: '#f0f7ff', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {DashboardEnhancements.generateTableFooterInfo(pronunciationActivities, currentLimit, "pronunciation")}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                🎤 Recent Speaking Practice
                <Badge 
                  badgeContent={speakingActivities.length} 
                  color="success" 
                  sx={{ ml: 2 }} 
                />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Latest conversation and interview practice sessions ({dateRange})
              </Typography>
            </Box>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => navigate("/view-detail")}
              endIcon={<TrendingUpIcon />}
            >
              VIEW DETAIL
            </Button>
          </Box>
          
          <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid', borderColor: 'divider' }}>
            <Table size="medium">
              <TableHead>
                <TableRow sx={{ backgroundColor: "#f8f9fa" }}>
                  <TableCell sx={{ fontWeight: 600 }}>Talent Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Practice Type</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>WPM</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Grammar/Feedback</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {speakingActivities.length > 0 ? (
                  speakingActivities.map((activity, index) => (
                    <TableRow 
                      key={index} 
                      hover 
                      sx={{ 
                        cursor: "pointer",
                        '&:hover': {
                          backgroundColor: 'action.hover'
                        }
                      }} 
                      onClick={() => handleRowClick(activity)}
                    >
                      <TableCell>
                        {/* ✅ FIX: Only show talent name, no ID */}
                        <Typography variant="body2" fontWeight={500} color="primary">
                          {activity.talentName}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={activity.activityType}
                          size="small"
                          color={getActivityTypeColor(activity.activityType)}
                          icon={getActivityTypeIcon(activity.activityType)}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={formatWPM(activity.wpm)}
                          size="small"
                          color={getWPMColor(activity.wpm)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography 
                          variant="body2" 
                          noWrap 
                          title={activity.grammarFeedback}
                          sx={{ maxWidth: 200 }}
                        >
                          {activity.grammarFeedback}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(activity.lastActivity)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                      <Box>
                        <MicIcon sx={{ fontSize: 48, color: '#bdbdbd', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                          No Recent Speaking Practice
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          No conversation or interview sessions in the {dateRange.toLowerCase()}.
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {speakingActivities.length > 0 && (
            <Box mt={2} p={2} sx={{ backgroundColor: '#f0fff0', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {DashboardEnhancements.generateTableFooterInfo(speakingActivities, currentLimit, "speaking")}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Footer Information */}
      {(pronunciationActivities.length > 0 || speakingActivities.length > 0) && (
        <Box mt={3} p={2} sx={{ backgroundColor: '#fafafa', borderRadius: 1, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            💡 <strong>Tip:</strong> Click on any row to view detailed talent profile and progress. 
            Total activities tracked: {totalActivities} ({dateRange.toLowerCase()})
            {currentLimit !== 10 && ` • Displaying ${currentLimit} activities per category`}
          </Typography>
        </Box>
      )}

      {/* Empty State */}
      {pronunciationActivities.length === 0 && speakingActivities.length === 0 && !loading && (
        <Card sx={{ borderRadius: 2, boxShadow: 1, mt: 3 }}>
          <CardContent sx={{ p: 6, textAlign: 'center' }}>
            <TrendingUpIcon sx={{ fontSize: 64, color: '#bdbdbd', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Recent Learning Activity
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              {emptyStateMessage}
            </Typography>
            <Stack direction="row" spacing={2} justifyContent="center">
              <Button 
                variant="contained" 
                onClick={() => navigate("/talents")}
                startIcon={<PeopleIcon />}
              >
                View All Talents
              </Button>
              <Button 
                variant="outlined" 
                onClick={handleOpenSettings}
                startIcon={<SettingsIcon />}
              >
                Adjust Settings
              </Button>
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Settings Dialog */}
      <Dialog open={settingsDialogOpen} onClose={handleCloseSettings} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <SettingsIcon />
            {DashboardEnhancements.settingsDialogConfig.title}
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={3}>
            <Box>
              <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                Activities per Category
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Choose how many activities to display for each category (pronunciation and speaking)
              </Typography>
              
              <FormControl fullWidth>
                <InputLabel>Activity Limit</InputLabel>
                <Select
                  value={tempSettings.customLimit ? "custom" : tempSettings.activityLimit}
                  label="Activity Limit"
                  onChange={(e) => {
                    if (e.target.value === "custom") {
                      setTempSettings(prev => ({ ...prev, customLimit: true }));
                    } else {
                      setTempSettings(prev => ({ 
                        ...prev, 
                        activityLimit: Number(e.target.value), 
                        customLimit: false 
                      }));
                    }
                  }}
                >
                  {limitOptions.predefinedLimits.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label} - {option.description}
                    </MenuItem>
                  ))}
                  <MenuItem value="custom">
                    {limitOptions.customLimit.label} - {limitOptions.customLimit.description}
                  </MenuItem>
                </Select>
              </FormControl>

              {tempSettings.customLimit && (
                <TextField
                  fullWidth
                  label="Custom Limit"
                  type="number"
                  value={tempSettings.customLimitValue}
                  onChange={(e) => setTempSettings(prev => ({ 
                    ...prev, 
                    customLimitValue: DashboardEnhancements.validateActivityLimit(e.target.value)
                  }))}
                  inputProps={{ 
                    min: limitOptions.customLimit.min, 
                    max: limitOptions.customLimit.max,
                    step: limitOptions.customLimit.step
                  }}
                  helperText={`Enter a number between ${limitOptions.customLimit.min} and ${limitOptions.customLimit.max}`}
                  sx={{ mt: 2 }}
                />
              )}
            </Box>

            <Box>
              <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                Time Range
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Select how far back to look for recent activities
              </Typography>
              
              <FormControl fullWidth>
                <InputLabel>Days Back</InputLabel>
                <Select
                  value={tempSettings.daysBack}
                  label="Days Back"
                  onChange={(e) => setTempSettings(prev => ({ 
                    ...prev, 
                    daysBack: Number(e.target.value) 
                  }))}
                >
                  {limitOptions.daysBackOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Preview:</strong> This will show up to{" "}
                <strong>
                  {tempSettings.customLimit ? tempSettings.customLimitValue : tempSettings.activityLimit}
                </strong>{" "}
                activities per category from the last{" "}
                <strong>{tempSettings.daysBack} days</strong>.
              </Typography>
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSettings}>Cancel</Button>
          <Button 
            onClick={handleApplySettings} 
            variant="contained"
            startIcon={<SettingsIcon />}
          >
            Apply Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardHomePage;