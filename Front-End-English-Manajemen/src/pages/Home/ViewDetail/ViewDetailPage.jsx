// src/pages/Home/ViewDetail/ViewDetailPage.jsx
import React, { useState } from "react";
import { Box, Card, CardContent, IconButton } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useNavigate } from "react-router-dom";

import TopActiveLearnersTab from "./TopActiveLearnersTab";
import HighestScoringLearnersTab from "./HighestScoringLearnersTab";
import ViewDetailTabSelector from "../../../components/Elements/ViewDetailTabSelector";
import CustomTypography from "../../../components/Elements/CustomTypography";

const ViewDetailPage = () => {
  const [activeTab, setActiveTab] = useState("topActive");
  const navigate = useNavigate();

  const handleBackToDashboard = () => {
    navigate("/dashboard");
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case "topActive":
        return <TopActiveLearnersTab />;
      case "highestScoring":
        return <HighestScoringLearnersTab />;
      default:
        return <TopActiveLearnersTab />;
    }
  };

  const getTabTitle = () => {
    switch (activeTab) {
      case "topActive":
        return "Top Active Learners";
      case "highestScoring":
        return "Highest Scoring Learners";
      default:
        return "Learner Analytics";
    }
  };

  const getTabDescription = () => {
    switch (activeTab) {
      case "topActive":
        return "Talents with the highest activity streaks and consistent practice";
      case "highestScoring":
        return "Performance analysis across different exercise categories";
      default:
        return "Detailed analytics for talent performance";
    }
  };

  return (
    <Box p={4}>
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={handleBackToDashboard} sx={{ mr: 2 }} title="Back to Dashboard">
          <ArrowBackIcon />
        </IconButton>
        <Box>
          <CustomTypography variant="h5" fontWeight={600}>{getTabTitle()}</CustomTypography>
          <CustomTypography variant="body2" color="text.secondary">{getTabDescription()}</CustomTypography>
        </Box>
      </Box>
      <Card sx={{ borderRadius: 3, boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}>
        <CardContent sx={{ p: 3 }}>
          <ViewDetailTabSelector activeTab={activeTab} onChange={setActiveTab} />
          <Box mt={3}>{renderActiveTab()}</Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ViewDetailPage;