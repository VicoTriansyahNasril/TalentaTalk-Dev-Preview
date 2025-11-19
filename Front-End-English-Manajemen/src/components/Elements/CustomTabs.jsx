//src/components/Elements/CustomTabs.jsx
import React from "react";
import { Tabs, Tab, Box, Typography } from "@mui/material";
import PropTypes from "prop-types";

const CustomTabs = ({ value, onChange, tabs }) => {
  return (
    <Tabs
      value={value}
      onChange={onChange}
      indicatorColor="primary"
      textColor="primary"
      sx={styles.tabs}
    >
      {tabs.map((tab, index) => (
        <Tab
          key={index}
          icon={tab.icon}
          iconPosition="start"
          label={
            <Typography
              sx={{
                textTransform: "none",
                fontSize: "14px",
                fontWeight: value === index ? 600 : 400,
              }}
            >
              {tab.label}
            </Typography>
          }
          sx={{
            py: 1.5,
            minHeight: "60px",
            gap: 1,
          }}
        />
      ))}
    </Tabs>
  );
};

CustomTabs.propTypes = {
  value: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.node.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
};

const styles = {
  tabs: {
    borderBottom: "1px solid #ddd",
    height: "60px",
    display: "flex",
  },
};

export default CustomTabs;
