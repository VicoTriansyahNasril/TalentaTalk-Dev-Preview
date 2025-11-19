// src/pages/Home/ViewDetail/TopActiveLearnersTab.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Box, CircularProgress, Alert, Chip, IconButton, Typography, Paper } from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import InfoIcon from "@mui/icons-material/Info";
import CustomSearchbar from "../../../components/Elements/CustomSearchbar";
import TableComponent from "../../../components/Elements/TableComponent";
import CustomTypography from "../../../components/Elements/CustomTypography";
import { dashboardService } from "../../../services/dashboardService";

const TopActiveLearnersTab = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [data, setData] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await dashboardService.getTopActiveLearners({
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
  }, [searchTerm, paginationModel]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getStreakColor = (streakText) => {
    const streakValue = parseInt(streakText?.replace(' Days', '') || '0');
    if (streakValue >= 30) return "success";
    if (streakValue >= 7) return "warning";
    if (streakValue >= 1) return "info";
    return "default";
  };

  const getCurrentStreakColor = (streakText) => {
    const streakValue = parseInt(streakText?.replace(' Days', '') || '0');
    if (streakValue >= 7) return "success";
    if (streakValue >= 3) return "warning";
    if (streakValue >= 1) return "info";
    return "default";
  };
  
  const columns = [
    { field: "no", headerName: "Rank", width: 80 },
    { field: "talentName", headerName: "Talent Name", flex: 1.5 },
    { field: "email", headerName: "Email", flex: 2 },
    { 
      field: "currentStreak", 
      headerName: "Current Streak", 
      flex: 1.2, 
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          size="small" 
          color={getCurrentStreakColor(params.value)}
          sx={{ fontWeight: 'bold' }}
        />
      )
    },
    { 
      field: "highestStreak", 
      headerName: "Highest Streak", 
      flex: 1.2, 
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          size="small" 
          color={getStreakColor(params.value)} 
          variant="outlined"
        />
      )
    },
  ];

  return (
    <Box>
      {/* Sorting Info Banner */}
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
          <Box>
            <Typography variant="subtitle2" fontWeight={600} color="primary" gutterBottom>
              Sorting Logic - Top Active Learners
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
              <strong>1. Primary Sort:</strong> Current Streak (highest to lowest) - ongoing consecutive days of activity
              <br />
              <strong>2. Tie-breaker:</strong> Highest Streak (highest to lowest) - all-time record of consecutive days
              <br />
              <strong>3. Final Sort:</strong> Name (A-Z) for consistency when both streaks are equal
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Search and Controls */}
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

      {/* Content Area */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" p={6}>
          <CircularProgress size={40} />
          <Typography variant="body2" sx={{ ml: 2 }}>Loading top active learners...</Typography>
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
          {/* Results Summary */}
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary">
              {totalItems > 0 
                ? `Showing ${Math.min(data.length, totalItems)} of ${totalItems} active learners (sorted by current streak)`
                : "No active learners found"
              }
            </Typography>
          </Box>

          {/* Table */}
          <TableComponent
            rows={data.map((item, index) => ({ 
              id: item.id || index, 
              ...item,
              no: (paginationModel.page * paginationModel.pageSize) + index + 1
            }))}
            columns={columns}
            paginationEnabled
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            rowCount={totalItems}
            loading={loading}
          />

          <Box mt={3} p={2} sx={{ backgroundColor: '#fafafa', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" fontWeight={600} gutterBottom>
              Streak Color Legend:
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap" mt={1}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <Chip label="30+ Days" size="small" color="success" sx={{ minWidth: 80 }} />
                <Typography variant="caption">Excellent</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <Chip label="7-29 Days" size="small" color="warning" sx={{ minWidth: 80 }} />
                <Typography variant="caption">Good</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <Chip label="1-6 Days" size="small" color="info" sx={{ minWidth: 80 }} />
                <Typography variant="caption">Active</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <Chip label="0 Days" size="small" color="default" sx={{ minWidth: 80 }} />
                <Typography variant="caption">Inactive</Typography>
              </Box>
            </Box>
          </Box>
        </>
      )}
    </Box>
  );
};

export default TopActiveLearnersTab;