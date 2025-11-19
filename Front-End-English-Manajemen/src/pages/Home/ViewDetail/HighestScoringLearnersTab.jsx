// src/pages/Home/ViewDetail/HighestScoringLearnersTab.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Box, Tabs, Tab, CircularProgress, Alert, Chip, IconButton, Typography, Paper } from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import InfoIcon from "@mui/icons-material/Info";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import { useNavigate } from "react-router-dom";
import CustomSearchbar from "../../../components/Elements/CustomSearchbar";
import TableComponent from "../../../components/Elements/TableComponent";
import dashboardService from "../../../services/dashboardService";

const TABS_CONFIG = [
  { 
    label: "PHONEME MATERIAL", 
    category: "phoneme_material_exercise",
    description: "Word pronunciation exercises - sorted by average accuracy",
    sortingInfo: "Average Score → Attempted Words → Name"
  },
  { 
    label: "PHONEME EXERCISE", 
    category: "phoneme_exercise",
    description: "Sentence pronunciation exercises - sorted by average accuracy", 
    sortingInfo: "Average Score → Attempted Sentences → Name"
  },
  { 
    label: "PHONEME EXAM", 
    category: "phoneme_exam",
    description: "Phoneme examination results - sorted by average score",
    sortingInfo: "Average Score → Categories Attempted → Name"
  },
  { 
    label: "CONVERSATION", 
    category: "conversation",
    description: "Conversation practice sessions - sorted by speaking fluency",
    sortingInfo: "Average WPM → Total Attempts → Name"
  },
  { 
    label: "INTERVIEW", 
    category: "interview",
    description: "Interview practice sessions - sorted by speaking performance",
    sortingInfo: "Average WPM → Total Attempts → Name"
  },
];

const HighestScoringLearnersTab = () => {
  const [tabIndex, setTabIndex] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [data, setData] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await dashboardService.getHighestScoringLearners({
        category: TABS_CONFIG[tabIndex].category,
        searchQuery: searchTerm,
        page: paginationModel.page + 1,
        limit: paginationModel.pageSize,
      });
      
      setData(response.learners || []);
      setTotalItems(response.pagination?.totalRecords || 0);
    } catch (err) {
      setError(err.message || "Failed to load data");
      setData([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [tabIndex, searchTerm, paginationModel]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleTabChange = (_, newValue) => {
    setTabIndex(newValue);
    setSearchTerm("");
    setPaginationModel({ page: 0, pageSize: 10 });
  };

  const handleRowClick = (params) => {
    if (params.row.id) {
      navigate(`/talent/${params.row.id}`);
    }
  };

  const getScoreColor = (score) => {
    const value = parseFloat(score?.replace('%', '') || 0);
    if (value >= 80) return "success";
    if (value >= 70) return "warning";
    return "error";
  };

  const getWPMColor = (wpmValue) => {
    const value = parseFloat(wpmValue?.toString().replace(' WPM', '') || 0);
    if (value >= 150) return "success";
    if (value >= 100) return "warning";
    if (value >= 50) return "info";
    return "default";
  };
  
  const getColumns = () => {
    const baseColumns = [
      { field: "no", headerName: "Rank", width: 80 },
      { 
        field: "talentName", 
        headerName: "Talent Name", 
        flex: 2,
        renderCell: (params) => (
          <Box>
            <Typography variant="body2" fontWeight={500} sx={{ cursor: 'pointer', color: 'primary.main' }}>
              {params.value}
            </Typography>
          </Box>
        )
      },
    ];

    if (tabIndex <= 2) {
      return [
        ...baseColumns,
        { 
          field: "overallCompletion", 
          headerName: tabIndex === 0 ? "Words Attempted" : tabIndex === 1 ? "Sentences Attempted" : "Categories Attempted", 
          flex: 1.5,
          renderCell: (params) => (
            <Box>
              <Typography variant="body2">{params.value}</Typography>
            </Box>
          )
        },
        { 
          field: "overallPercentage", 
          headerName: "Avg Score", 
          flex: 1, 
          renderCell: (params) => (
            <Box>
              <Chip 
                label={params.value} 
                size="small" 
                color={getScoreColor(params.value)}
                icon={<TrendingUpIcon sx={{ fontSize: 16 }} />}
              />
              {params.row.totalAttempts && (
                <Typography variant="caption" display="block" color="text.secondary">
                  {params.row.totalAttempts} attempts
                </Typography>
              )}
            </Box>
          ) 
        }
      ];
    }
    
    if (tabIndex === 3) {
      return [
        ...baseColumns,
        { 
          field: "wpm", 
          headerName: "Avg WPM", 
          flex: 1,
          renderCell: (params) => (
            <Chip 
              label={params.value || "0 WPM"} 
              size="small" 
              color={getWPMColor(params.value)}
            />
          )
        },
        { 
          field: "grammer", 
          headerName: "Grammar Status", 
          flex: 1.5,
          renderCell: (params) => (
            <Typography variant="body2" noWrap>
              {params.value || "No data"}
            </Typography>
          )
        },
        { 
          field: "date", 
          headerName: "Latest Session", 
          flex: 1,
          renderCell: (params) => (
            <Typography variant="body2">
              {params.value || "N/A"}
            </Typography>
          )
        },
        {
          field: "totalAttempts",
          headerName: "Total Sessions",
          flex: 1,
          renderCell: (params) => (
            <Typography variant="body2">
              {params.value || 0}
            </Typography>
          )
        }
      ];
    }
    
    return [
      ...baseColumns,
      { 
        field: "wpm", 
        headerName: "Avg WPM", 
        flex: 1,
        renderCell: (params) => (
          <Chip 
            label={params.value || "0 WPM"} 
            size="small" 
            color={getWPMColor(params.value)}
          />
        )
      },
      { 
        field: "feedback", 
        headerName: "Latest Feedback", 
        flex: 2,
        renderCell: (params) => (
          <Typography variant="body2" noWrap title={params.value}>
            {params.value || "No feedback"}
          </Typography>
        )
      },
      { 
        field: "date", 
        headerName: "Latest Session", 
        flex: 1,
        renderCell: (params) => (
          <Typography variant="body2">
            {params.value || "N/A"}
          </Typography>
        )
      },
      {
        field: "totalAttempts",
        headerName: "Total Sessions",
        flex: 1,
        renderCell: (params) => (
          <Typography variant="body2">
            {params.value || 0}
          </Typography>
        )
      }
    ];
  };

  const currentTab = TABS_CONFIG[tabIndex];

  return (
    <Box>
      <Tabs 
        value={tabIndex} 
        onChange={handleTabChange} 
        sx={{ mb: 3 }} 
        variant="scrollable" 
        scrollButtons="auto"
      >
        {TABS_CONFIG.map((tab, i) => (
          <Tab key={i} label={tab.label} />
        ))}
      </Tabs>

      <Paper 
        elevation={0} 
        sx={{ 
          p: 2, 
          mb: 3, 
          backgroundColor: '#f8f9fa', 
          border: '1px solid #e3f2fd',
          borderRadius: 2
        }}
      >
        <Box display="flex" alignItems="flex-start" gap={1}>
          <InfoIcon color="primary" sx={{ mt: 0.5, fontSize: 20 }} />
          <Box flex={1}>
            <Typography variant="subtitle2" fontWeight={600} color="primary" gutterBottom>
              {currentTab.label} - Highest Scoring Learners
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {currentTab.description}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              <strong>Sorting Logic:</strong> {currentTab.sortingInfo}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <CustomSearchbar 
          searchValue={searchTerm} 
          onSearchChange={(e) => setSearchTerm(e.target.value)} 
          placeholder="Search by talent name..." 
        />
        <IconButton 
          onClick={fetchData} 
          disabled={loading} 
          title="Refresh Data"
          sx={{ 
            backgroundColor: loading ? 'transparent' : 'action.hover',
            '&:hover': { backgroundColor: 'action.selected' }
          }}
        >
          <RefreshIcon />
        </IconButton>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" p={6}>
          <CircularProgress size={40} />
          <Typography variant="body2" sx={{ ml: 2 }}>Loading highest scoring learners...</Typography>
        </Box>
      ) : error ? (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          action={
            <IconButton size="small" onClick={fetchData}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          }
        >
          {error}
        </Alert>
      ) : (
        <>
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary">
              {totalItems > 0 
                ? `Showing ${Math.min(data.length, totalItems)} of ${totalItems} learners (sorted by ${currentTab.sortingInfo.toLowerCase()})`
                : "No learners found for this category"
              }
            </Typography>
          </Box>

          <TableComponent
            rows={data.map((item, index) => ({ 
              id: item.id || index, 
              ...item,
              no: (paginationModel.page * paginationModel.pageSize) + index + 1
            }))}
            columns={getColumns()}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalItems}
            loading={loading}
            onRowClick={handleRowClick}
            sx={{
              '& .MuiDataGrid-row': {
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover',
                }
              }
            }}
          />

          <Box mt={3} p={2} sx={{ backgroundColor: '#fafafa', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" fontWeight={600} gutterBottom>
              Performance Indicators:
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap" mt={1}>
              {tabIndex <= 2 ? (
                <>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="80%+" size="small" color="success" sx={{ minWidth: 60 }} />
                    <Typography variant="caption">Excellent</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="70-79%" size="small" color="warning" sx={{ minWidth: 60 }} />
                    <Typography variant="caption">Good</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="<70%" size="small" color="error" sx={{ minWidth: 60 }} />
                    <Typography variant="caption">Needs Improvement</Typography>
                  </Box>
                </>
              ) : (
                <>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="150+ WPM" size="small" color="success" sx={{ minWidth: 80 }} />
                    <Typography variant="caption">Excellent</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="100-149 WPM" size="small" color="warning" sx={{ minWidth: 80 }} />
                    <Typography variant="caption">Good</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="50-99 WPM" size="small" color="info" sx={{ minWidth: 80 }} />
                    <Typography variant="caption">Average</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Chip label="<50 WPM" size="small" color="default" sx={{ minWidth: 80 }} />
                    <Typography variant="caption">Beginner</Typography>
                  </Box>
                </>
              )}
            </Box>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
              💡 <strong>Tip:</strong> Click on any row to view detailed talent profile and progress
            </Typography>
          </Box>
        </>
      )}
    </Box>
  );
};

export default HighestScoringLearnersTab;