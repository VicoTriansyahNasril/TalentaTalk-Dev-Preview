// src/pages/TalentPages/TalentDetailPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import {
  Box, Avatar, Grid, Breadcrumbs, Link, IconButton, CircularProgress, Alert, Chip, Button, Paper, Typography, Divider, Stack
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import RefreshIcon from "@mui/icons-material/Refresh";
import EmailIcon from '@mui/icons-material/Email';
import WorkIcon from '@mui/icons-material/Work';
import StarIcon from '@mui/icons-material/Star';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";
import TableComponent from "../../components/Elements/TableComponent";
import CustomTypography from "../../components/Elements/CustomTypography";
import CustomTabs from "../../components/Elements/CustomTabs";
import { talentService } from "../../services/talentService";

const TABS_CONFIG = [
  { 
    label: "PHONEME MATERIAL", 
    category: "phoneme-material-exercise", 
    dataKey: "phonemeCategories", 
    detailPath: "phoneme-material",
    contentTitle: "Phoneme Material Progress",
    contentDescription: "Overview of talent's progress across different phoneme word categories."
  },
  { 
    label: "PHONEME EXERCISE", 
    category: "phoneme-exercise", 
    dataKey: "phonemeExercises", 
    detailPath: "pronunciation",
    contentTitle: "Phoneme Exercise Progress",
    contentDescription: "Summary of practice on sentences with similar phonemes."
  },
  { 
    label: "PHONEME EXAM", 
    category: "phoneme-exam", 
    dataKey: "phonemeExams", 
    detailPath: "phoneme-exam",
    contentTitle: "Phoneme Exam Results",
    contentDescription: "Performance history in phoneme examination sets."
  },
  { 
    label: "CONVERSATION", 
    category: "conversation", 
    dataKey: "conversations",
    contentTitle: "Conversation Practice History",
    contentDescription: "Records of conversation sessions, including WPM and grammar feedback."
  },
  { 
    label: "INTERVIEW", 
    category: "interview", 
    dataKey: "interviews", 
    detailPath: "interview",
    contentTitle: "Interview Practice History",
    contentDescription: "Records of interview practice attempts with performance feedback."
  },
];

const KpiCard = ({ icon, label, value, color }) => (
  <Paper variant="outlined" sx={{ p: 2, display: 'flex', alignItems: 'center', height: '100%', borderRadius: 2 }}>
    <Avatar sx={{ bgcolor: `${color}.lighter`, color: `${color}.darker`, mr: 2 }}>
      {icon}
    </Avatar>
    <Box>
      <Typography variant="h6" fontWeight={700} sx={{ color: `${color}.dark` }}>{value}</Typography>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
    </Box>
  </Paper>
);

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`talent-tabpanel-${index}`}
      aria-labelledby={`talent-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const TalentDetailPage = () => {
  const [tabIndex, setTabIndex] = useState(0);
  const [talentData, setTalentData] = useState(null);
  const [tabData, setTabData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [totalData, setTotalData] = useState(0);
  const navigate = useNavigate();
  const { id } = useParams();

  const fetchTabData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const { category, dataKey } = TABS_CONFIG[tabIndex];
      const response = await talentService.getTalentProgress(id, category, {
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });

      setTalentData(response.talentInfo);
      setTabData(response[dataKey] || []);
      setTotalData(response.pagination?.totalRecords || 0);
    } catch (err) {
      setError(err.message || "Failed to load data");
      if (err.response?.status === 404) {
        setTimeout(() => navigate("/talents"), 2000);
      }
    } finally {
      setLoading(false);
    }
  }, [id, tabIndex, paginationModel, navigate]);

  useEffect(() => {
    fetchTabData();
  }, [fetchTabData]);

  const handleTabChange = (_, newValue) => {
    setTabIndex(newValue);
    setPaginationModel({ page: 0, pageSize: 10 });
  };
  
  const getScoreColor = (score) => {
    const value = parseFloat(score?.replace('%', '') || 0);
    if (value >= 80) return "success";
    if (value >= 70) return "warning";
    return "error";
  };

  const getColumnsForTab = () => {
    const { detailPath } = TABS_CONFIG[tabIndex];
    const baseActionColumn = {
      field: "action",
      headerName: "Action",
      sortable: false,
      renderCell: (params) => (
        <IconButton onClick={() => navigate(`/talent/${id}/${detailPath}/${encodeURIComponent(params.row.phonemeCategory)}`)}>
          <VisibilityIcon />
        </IconButton>
      )
    };

    switch (tabIndex) {
      case 0: return [{ field: "phonemeCategory", headerName: "Category", flex: 1.5 }, { field: "wordsAttempted", headerName: "Words Attempted", flex: 1 }, { field: "averageAccuracy", headerName: "Avg. Accuracy", flex: 1, renderCell: (params) => <Chip label={params.value || "0%"} size="small" color={getScoreColor(params.value)} /> }, baseActionColumn];
      case 1: return [{ field: "phonemeCategory", headerName: "Category", flex: 1.5 }, { field: "sentenceAttempted", headerName: "Sentences Attempted", flex: 1 }, { field: "averageAccuracy", headerName: "Avg. Accuracy", flex: 1, renderCell: (params) => <Chip label={params.value || "0%"} size="small" color={getScoreColor(params.value)} /> }, baseActionColumn];
      case 2: return [{ field: "phonemeCategory", headerName: "Category", flex: 1.5 }, { field: "bestScore", headerName: "Best Score", flex: 1, renderCell: (params) => <Chip label={params.value || "0%"} size="small" color={getScoreColor(params.value)} /> }, { field: "latestScore", headerName: "Latest Score", flex: 1, renderCell: (params) => <Chip label={params.value || "0%"} size="small" color={getScoreColor(params.value)} /> }, baseActionColumn];
      case 3: return [
        { field: "topic", headerName: "Topic", flex: 1.5 }, 
        { 
          field: "wpm", 
          headerName: "WPM", 
          flex: 0.5,
          renderCell: (params) => (
            <Typography variant="body2">{`${params.value} WPM`}</Typography>
          )
        }, 
        { 
          field: "grammarIssue", 
          headerName: "Grammar Issues", 
          flex: 2,
          renderCell: (params) => (
            <Box title={params.value} sx={{ whiteSpace: 'normal', lineHeight: 1.4, py: 1 }}>
              <Typography variant="body2">{params.value}</Typography>
            </Box>
          )
        }, 
        { field: "date", headerName: "Date", flex: 1 }
      ];
      case 4: return [
        { field: "attempt", headerName: "Attempt", flex: 0.5 }, 
        { 
          field: "wordProducePerMinute", 
          headerName: "WPM", 
          flex: 0.5,
          renderCell: (params) => (
            <Typography variant="body2">{`${params.value} WPM`}</Typography>
          )
        }, 
        { 
          field: "feedback", 
          headerName: "Feedback", 
          flex: 2, 
          renderCell: (params) => (
            <Box title={params.value} sx={{ whiteSpace: 'normal', lineHeight: 1.4, py: 1 }}>
              <Typography variant="body2">{params.value}</Typography>
            </Box>
          )
        }, 
        { field: "date", headerName: "Date", flex: 1 },
        {
          field: "action",
          headerName: "Action",
          sortable: false,
          renderCell: (params) => (
            <IconButton onClick={() => navigate(`/talent/${id}/interview/${params.row.attemptId}/detail`)}>
              <VisibilityIcon />
            </IconButton>
          )
        }
      ];
      default: return [];
    }
  };
  
  const getInitials = (name) => (name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : 'T');
  
  if (loading && !talentData) {
    return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;
  }

  if (error) {
    return <Box p={4}><Alert severity="error">{error}</Alert></Box>;
  }

  return (
    <Box p={4}>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/talents" underline="hover" color="inherit">Talent List</Link>
        <CustomTypography color="text.primary">{talentData?.nama}</CustomTypography>
      </Breadcrumbs>
      
      <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={5} sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ width: 80, height: 80, bgcolor: "primary.main", fontSize: '2.5rem', mr: 3 }}>
              {getInitials(talentData?.nama)}
            </Avatar>
            <Box>
              <CustomTypography variant="h5" fontWeight={600}>{talentData?.nama}</CustomTypography>
              <Stack direction="row" spacing={1} alignItems="center" mt={0.5}>
                <WorkIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">{talentData?.role}</Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center" mt={0.5}>
                <EmailIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">{talentData?.email}</Typography>
              </Stack>
            </Box>
          </Grid>
          <Grid item xs={12} md={7}>
            <Grid container spacing={2} justifyContent="flex-end">
              <Grid item xs={12} sm={6}>
                <KpiCard icon={<StarIcon />} label="Highest Exam Score" value={talentData?.highestExam || 'N/A'} color="warning" />
              </Grid>
              <Grid item xs={12} sm={6}>
                <KpiCard icon={<CheckCircleIcon />} label="Overall Progress" value={talentData?.progress || 'N/A'} color="success" />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Paper>
      
      <Paper elevation={1} sx={{ p: 3 }}>
        <CustomTabs value={tabIndex} onChange={handleTabChange} tabs={TABS_CONFIG} />
        
        {TABS_CONFIG.map((tab, index) => (
          <TabPanel key={index} value={tabIndex} index={index}>
            <Box>
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Typography variant="h6" fontWeight={600}>{tab.contentTitle}</Typography>
                  <Typography variant="body2" color="text.secondary">{tab.contentDescription}</Typography>
                </Box>
                <Chip label={`${totalData} items`} color="primary" variant="outlined" size="small" />
              </Stack>
              <Divider sx={{ my: 2 }} />

              {loading ? <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box> :
              error ? <Alert severity="error" sx={{ mb: 2 }}>{error}<Button onClick={fetchTabData} size="small" sx={{ ml: 2 }}>Retry</Button></Alert> :
              <TableComponent
                  rows={tabData.map((item, itemIndex) => ({ id: item.attemptId || item.id || itemIndex, ...item }))}
                  columns={getColumnsForTab()}
                  paginationModel={paginationModel}
                  onPaginationModelChange={setPaginationModel}
                  rowCount={totalData}
                  paginationEnabled
                  loading={loading}
                  getRowHeight={() => 'auto'}
                  sx={{
                    '& .MuiDataGrid-cell': {
                      py: 1.5,
                    },
                  }}
                />
              }
            </Box>
          </TabPanel>
        ))}
      </Paper>
    </Box>
  );
};

export default TalentDetailPage;