import React from "react";
import { Button, Stack } from "@mui/material";
import { User, CalendarCheck } from "lucide-react";

const ViewDetailTabSelector = ({ activeTab, onChange }) => {
  const tabs = [
    {
      label: "Top Active Learners",
      value: "topActive",
      icon: <User size={18} />,
    },
    {
      label: "Highest Scoring Learners",
      value: "highestScoring",
      icon: <CalendarCheck size={18} />,
    },
  ];

  return (
    <Stack direction="row" spacing={2} mb={2}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.value;
        return (
          <Button
            key={tab.value}
            variant="contained"
            onClick={() => onChange(tab.value)}
            startIcon={tab.icon}
            sx={{
              backgroundColor: isActive ? "#007BFF" : "#fff",
              color: isActive ? "#fff" : "#000",
              fontWeight: isActive ? "bold" : "normal",
              border: isActive ? "none" : "1px solid #ddd",
              borderRadius: "12px",
              textTransform: "none",
              boxShadow: "none",
              "&:hover": {
                backgroundColor: isActive ? "#0056b3" : "#f5f5f5",
              },
            }}
          >
            {tab.label}
          </Button>
        );
      })}
    </Stack>
  );
};

export default ViewDetailTabSelector;
