//src/components/Elements/CustomSearchbar.jsx
import React from "react";
import { Box, TextField, InputAdornment } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

const CustomSearchBar = ({ searchValue, onSearchChange }) => {
  return (
    <Box sx={styles.boxSearch}>
      <TextField
        fullWidth
        size="small"
        placeholder="Search"
        value={searchValue}
        onChange={onSearchChange}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        sx={styles.input}
      />
    </Box>
  );
};

const styles = {
  input: {
    "& .MuiOutlinedInput-root": {
      borderRadius: "12px",
    },
  },
  boxSearch: {
    height: "50px",
  },
};

export default CustomSearchBar;
