// src/components/Layout/Sidebar.jsx
import React from "react";
import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  useTheme,
  Box,
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import PeopleIcon from "@mui/icons-material/People";
import { Link, useLocation } from "react-router-dom";

const drawerWidth = 240;

const Sidebar = ({ open, onClose, variant }) => {
  const location = useLocation();
  const theme = useTheme();

  const menuItems = [
    {
      text: "Home",
      icon: <DashboardIcon />,
      path: "/dashboard",
      matchPaths: ["/dashboard", "/view-detail"],
    },
    {
      text: "Talent List",
      icon: <PeopleIcon />,
      path: "/talents",
      matchPaths: ["/talents", "/talent/"],
    },
    {
      text: "Pronunciation Material",
      icon: <MenuBookIcon />,
      path: "/pronunciation-material",
      matchPaths: [
        "/pronunciation-material",
        "/material/pronunciation",
        "/material/exercise",
        "/exam-phoneme",
      ],
    },
    {
      text: "Interview Material",
      icon: <MenuBookIcon />,
      path: "/conversation-material",
      matchPaths: ["/conversation-material"],
    },
  ];

  const drawerContent = (
    <Box>
      <Toolbar />
      <Box sx={{ p: 2, pt: 1 }}>
        <List>
          {menuItems.map((item) => {
            const isActive = item.matchPaths.some((path) =>
              location.pathname.startsWith(path)
            );

            return (
              <ListItemButton
                key={item.text}
                component={Link}
                to={item.path}
                onClick={variant === "temporary" ? onClose : undefined}
                selected={isActive}
                sx={{
                  borderRadius: 2,
                  py: 1.2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.primary.main,
                    color: theme.palette.primary.contrastText,
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.contrastText,
                    },
                    '&:hover': {
                      backgroundColor: theme.palette.primary.dark,
                    }
                  },
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{ fontWeight: isActive ? 600 : 500 }}
                />
              </ListItemButton>
            );
          })}
        </List>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
          backgroundColor: "#FFFFFF",
          borderRight: "1px solid #E0E0E0",
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;