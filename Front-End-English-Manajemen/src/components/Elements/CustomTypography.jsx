// src/components/Elements/CustomTypography.jsx
import React from "react";
import { Typography } from "@mui/material";

const CustomTypography = ({
  variant = "body1",
  fontWeight = 400,
  fontSize,
  color = "inherit",
  sx = {},
  children,
  ...props
}) => {
  return (
    <Typography
      variant={variant}
      color={color}
      sx={{
        fontWeight,
        fontSize,
        textTransform: "none",
        ...sx,
      }}
      {...props}
    >
      {children}
    </Typography>
  );
};

export default CustomTypography;
