// src/components/Layout/Topbar.jsx
import React from "react";
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useNavigate } from "react-router-dom";
import ProfileCard from "../Elements/ProfileCard"; 

const Topbar = ({ onToggleSidebar, isMobile, userName, userRole, onLogout }) => {
  const navigate = useNavigate();

  const handleProfile = () => {
    navigate("/profile");
  };

  return (
    <AppBar
      position="fixed"
      elevation={1}
      sx={{
        bgcolor: "primary.main",
        color: "#FFFFFF",
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between", px: { xs: 2, md: 3 } }}>
        <Box display="flex" alignItems="center">
          {isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={onToggleSidebar}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" noWrap fontWeight={600}>
            TalentaTalk Admin
          </Typography>
        </Box>

        <ProfileCard
          userName={userName}
          userRole={userRole}
          onLogout={onLogout}
          onProfile={handleProfile}
        />
      </Toolbar>
    </AppBar>
  );
};

export default Topbar;