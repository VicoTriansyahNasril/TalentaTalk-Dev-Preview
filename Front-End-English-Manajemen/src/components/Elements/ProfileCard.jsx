// src/components/Elements/ProfileCard.jsx
import React, { useState } from "react";
import {
  Box,
  Avatar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import LogoutIcon from "@mui/icons-material/Logout";
import PersonIcon from "@mui/icons-material/Person";

const ProfileCard = ({ userName = "Tim Manajemen", userRole = "Manajemen", onLogout, onProfile }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    onLogout?.();
  };

  const handleProfileClick = () => {
    handleMenuClose();
    onProfile?.();
  };

  return (
    <>
      <Box sx={styles.profileCard} onClick={handleMenuOpen}>
        <Avatar sx={styles.avatar}>
          <PersonIcon fontSize="small" />
        </Avatar>
        <Box sx={styles.userInfo}>
          <Typography sx={{ fontWeight: 500, fontSize: "14px", color: "#212121" }}>
            {userName}
          </Typography>
          <Typography
            sx={{ fontWeight: 400, fontSize: "12px" }}
            color="text.secondary"
          >
            {userRole}
          </Typography>
        </Box>
        <IconButton size="small">
          <ExpandMoreIcon />
        </IconButton>
      </Box>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        onClick={handleMenuClose}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: "visible",
            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.15))',
            mt: 1.5,
            width: 200,
            borderRadius: 2,
            '& .MuiAvatar-root': {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
            '&:before': {
              content: '""',
              display: 'block',
              position: 'absolute',
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: 'background.paper',
              transform: 'translateY(-50%) rotate(45deg)',
              zIndex: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem onClick={handleProfileClick}>
          <ListItemIcon>
            <PersonIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="My Profile" />
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" sx={{ color: "error.main" }} />
          </ListItemIcon>
          <ListItemText
            primary="Logout"
            primaryTypographyProps={{ sx: { color: "error.main" } }}
          />
        </MenuItem>
      </Menu>
    </>
  );
};

const styles = {
  profileCard: {
    border: "1px solid #E0E0E0",
    display: "flex",
    alignItems: "center",
    padding: "6px 8px",
    borderRadius: "12px",
    backgroundColor: "#FFFFFF",
    cursor: "pointer",
    transition: "box-shadow 0.2s",
    '&:hover': {
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
    }
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: "8px",
    bgcolor: "#E3F2FD",
    color: "#1976D2",
  },
  userInfo: {
    ml: 1.5,
    mr: 1,
  },
};

export default ProfileCard;