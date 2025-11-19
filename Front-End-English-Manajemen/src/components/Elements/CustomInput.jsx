//src/components/Elements/CustomInput.jsx
import React, { useState, useRef } from "react";
import {
  TextField,
  MenuItem,
  IconButton,
  InputAdornment,
  Box,
  Typography,
  Modal,
} from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CloseIcon from "@mui/icons-material/Close";
import { TimePicker } from "@mui/x-date-pickers/TimePicker";
import { DateCalendar } from "@mui/x-date-pickers/DateCalendar";
import dayjs from "dayjs";

const CustomInput = ({
  label,
  type,
  options = [],
  value,
  name,
  onChange,
  fileType,
  hideLabel = false,
  ...rest
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [isSelectOpen, setIsSelectOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isDatePickerOpen, setIsDatePickerOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(value ? dayjs(value) : null);
  const fileInputRef = useRef(null);

  const handleTogglePasswordVisibility = () => setShowPassword(!showPassword);
  const handleSelectOpen = () => setIsSelectOpen(true);
  const handleSelectClose = () => setIsSelectOpen(false);

  const handleFileChange = (file) => {
    const maxFileSize = 2 * 1024 * 1024;
    const validFormats =
      fileType === "image"
        ? ["image/png", "image/jpeg", "image/jpg"]
        : ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/csv"];

    if (!file) {
      setSelectedFile(null);
      setError("File is required.");
      onChange?.({ target: { name: "fileField", files: [] } });
      return;
    }

    if (!validFormats.includes(file.type)) {
      setSelectedFile(null);
      setError(
        fileType === "image"
          ? "Please upload a valid image file (.jpg, .jpeg, .png)."
          : "Please upload a valid .xlsx or .csv file."
      );
    } else if (file.size > maxFileSize) {
      setSelectedFile(null);
      setError("File size must be less than 2MB.");
    } else {
      setSelectedFile(file);
      setError("");
      onChange?.({ target: { name: "fileField", files: [file] } });
    }
  };

  const handleDateChange = (newValue) => {
    if (newValue) {
      const formatted = dayjs(newValue);
      setSelectedDate(formatted);
      onChange?.({ target: { name, value: formatted.format("YYYY-MM-DD") } });
      setTimeout(() => setIsDatePickerOpen(false), 100);
    }
  };

  const handleFileClick = () => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      const link = document.createElement("a");
      link.href = url;
      link.download = selectedFile.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  const handleRemoveFile = (e) => {
    e.stopPropagation();
    setSelectedFile(null);
    setError("");
    onChange?.({ target: { name: "fileField", files: [] } });
  };

  const renderTextField = () => (
    <TextField
      label={hideLabel ? "" : label}
      type={type === "password" ? (showPassword ? "text" : "password") : type}
      variant="outlined"
      margin="normal"
      name={name}
      sx={styles.common}
      value={value}
      onChange={onChange}
      InputProps={{
        ...styles.input,
        ...(type === "password" && {
          endAdornment: (
            <InputAdornment position="end">
              <IconButton onClick={handleTogglePasswordVisibility} edge="end">
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }),
      }}
      {...rest}
    />
  );

  const renderDate = () => (
    <>
      <TextField
        label={hideLabel ? "" : label}
        type="text"
        variant="outlined"
        margin="normal"
        name={name}
        sx={styles.common}
        value={selectedDate ? selectedDate.format("MMMM DD, YYYY") : ""}
        InputProps={{
          ...styles.input,
          readOnly: true,
          endAdornment: (
            <InputAdornment position="end">
              <IconButton onClick={() => setIsDatePickerOpen(true)}>
                <CalendarTodayIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        {...rest}
      />
      <Modal open={isDatePickerOpen} onClose={() => setIsDatePickerOpen(false)}>
        <Box sx={styles.modal}>
          <DateCalendar
            value={selectedDate ? selectedDate.toDate() : null}
            onChange={handleDateChange}
          />
        </Box>
      </Modal>
    </>
  );

  const renderSelect = () => (
    <TextField
      select
      label={hideLabel ? "" : label}
      variant="outlined"
      margin="normal"
      name={name}
      sx={styles.common}
      value={value}
      onChange={onChange}
      SelectProps={{
        open: isSelectOpen,
        onOpen: handleSelectOpen,
        onClose: handleSelectClose,
        IconComponent: () => null,
      }}
      InputProps={{
        ...styles.input,
        endAdornment: (
          <InputAdornment position="end">
            <IconButton onClick={handleSelectOpen} edge="end">
              {isSelectOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
            </IconButton>
          </InputAdornment>
        ),
      }}
      {...rest}
    >
      {options.map((option, index) => (
        <MenuItem key={index} value={option.value}>
          {option.label}
        </MenuItem>
      ))}
    </TextField>
  );

  const renderTimePicker = () => (
    <TimePicker
      label={hideLabel ? "" : label}
      value={value}
      onChange={onChange}
      renderInput={(params) => (
        <TextField
          {...params}
          variant="outlined"
          name={name}
          sx={styles.common}
          InputProps={{ ...styles.input, ...params.InputProps }}
          {...rest}
        />
      )}
    />
  );

  const renderFileUpload = () => (
    <Box
      sx={{
        ...styles.fileUpload.box,
        borderColor: error ? "error.main" : "#CFD0DA",
        backgroundColor: isDragging ? "#F0F0F0" : "#FFF",
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFileChange(e.dataTransfer.files[0]);
      }}
      onClick={() => fileInputRef.current?.click()}
    >
      <Typography sx={styles.fileUpload.text}>
        Drag & drop file here, or click to select
      </Typography>
      <Box mt={2}>
        <CloudUploadIcon fontSize="large" />
      </Box>
      <input
        ref={fileInputRef}
        type="file"
        hidden
        accept={fileType === "image" ? ".jpg,.png" : ".xlsx,.csv"}
        onChange={(e) => handleFileChange(e.target.files[0])}
      />
      {selectedFile && (
        <Box sx={styles.fileUpload.info} onClick={handleFileClick}>
          <InsertDriveFileIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>{selectedFile.name}</Typography>
          <IconButton onClick={handleRemoveFile}>
            <CloseIcon />
          </IconButton>
        </Box>
      )}
      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
    </Box>
  );

  switch (type) {
    case "select":
      return renderSelect();
    case "time":
      return renderTimePicker();
    case "file":
      return renderFileUpload();
    case "date":
      return renderDate();
    default:
      return renderTextField();
  }
};

const styles = {
  modal: {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 370,
    bgcolor: "background.paper",
    boxShadow: 24,
    py: 2,
    borderRadius: "10px",
  },
  fileUpload: {
    box: {
      border: "2px dashed",
      borderRadius: "10px",
      padding: 2,
      display: "flex",
      width: "100%",
      height: "200px",
      cursor: "pointer",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
    },
    info: {
      mt: 2,
      borderRadius: "20px",
      bgcolor: "#CFD0DA",
      p: 1,
      display: "flex",
      alignItems: "center",
      position: "relative",
      cursor: "pointer",
    },
    text: {
      textAlign: "center",
      color: "secondary.main",
    },
  },
  common: {
    "& .MuiInputLabel-shrink": {
      color: "primary.main",
      fontWeight: "light",
      transform: "translate(14px, 10px) scale(0.7)",
    },
  },
  input: {
    sx: {
      borderRadius: "10px",
      "& input, & .MuiSelect-select": {
        paddingTop: "27px",
        paddingBottom: "7px",
      },
    },
  },
};

export default CustomInput;
