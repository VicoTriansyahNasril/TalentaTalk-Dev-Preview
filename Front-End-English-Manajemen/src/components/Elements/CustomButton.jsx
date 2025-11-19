//src/components/Elements/CustomButton.jsx
import React from "react";
import { Button } from "@mui/material";
import { styled } from "@mui/system";

const StyledButton = styled(({ colorScheme, ...otherProps }) => (
  <Button {...otherProps} />
))(({ theme, colorScheme }) => {
  let backgroundColor;
  let colorFont;
  let hoverBackgroundColor;
  let border;

  switch (colorScheme) {
    case "bgBlue":
      backgroundColor = theme.palette.primary.main;
      colorFont = "#FFFFFF";
      hoverBackgroundColor = "#0062B3";
      border = "none";
      break;
    case "bgWhite":
      backgroundColor = "#FFFFFF";
      colorFont = "#16151C";
      hoverBackgroundColor = "#F5F5F5";
      border = "1px solid #E5E4E7";
      break;
    case "bgOrange":
      backgroundColor = "#FFBB34";
      colorFont = "#FFFFFF";
      hoverBackgroundColor = "#E69900";
      border = "none";
      break;
    default:
      backgroundColor = theme.palette.primary.main;
      colorFont = "#FFFFFF";
      hoverBackgroundColor = "#0062B3";
      border = "none";
      break;
  }

  return {
    backgroundColor: backgroundColor,
    color: colorFont,
    height: "50px",
    borderRadius: "10px",
    border: border,
    padding: "8px 16px",
    fontSize: "16px",
    fontWeight: theme.typography.fontWeightLight,
    textTransform: "none",
    boxShadow: "none",
    "&:hover": {
      backgroundColor: hoverBackgroundColor,
      boxShadow: "none",
    },
    display: "flex",
    alignItems: "center",
    gap: "8px",
    minWidth: "90px",
  };
});

const CustomButton = ({
  children,
  onClick,
  colorScheme,
  startIcon,
  type = "button",
  disabled,
}) => {
  return (
    <StyledButton
      variant="contained"
      onClick={onClick}
      colorScheme={colorScheme}
      type={type}
      disabled={disabled}
      startIcon={startIcon}
    >
      {children}
    </StyledButton>
  );
};

export default CustomButton;
