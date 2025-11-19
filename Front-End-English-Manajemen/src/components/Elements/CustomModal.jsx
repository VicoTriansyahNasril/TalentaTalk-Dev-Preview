//src/components/Elements/CustomModal.jsx
import React from "react";
import {
  Modal,
  Box,
  Typography,
  IconButton,
  Backdrop,
  Divider,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import CustomButton from "./CustomButton";

const CustomModal = ({ open, onClose, children }) => {
  return (
    <Modal
      open={open}
      onClose={onClose}
      closeAfterTransition
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
        sx: styles.backdrop,
      }}
    >
      <Box sx={styles.modal}>
        <Box sx={styles.content}>{children}</Box>
      </Box>
    </Modal>
  );
};

const HeaderModal = ({ children, onClose }) => (
  <>
    <Box sx={styles.header}>
      <Typography sx={styles.headerTitle}>{children}</Typography>
      <IconButton onClick={onClose}>
        <CloseIcon />
      </IconButton>
    </Box>
    <Divider sx={styles.divider} />
  </>
);

const FooterModal = ({ onClose, onSubmit, children, disableSubmit }) => (
  <Box sx={styles.footer}>
    <CustomButton variant="outlined" onClick={onClose} colorScheme="bgWhite">
      Cancel
    </CustomButton>
    <CustomButton
      variant="contained"
      onClick={onSubmit}
      colorScheme="bgBlue"
      disabled={disableSubmit}
    >
      {children}
    </CustomButton>
  </Box>
);

CustomModal.Header = HeaderModal;
CustomModal.Footer = FooterModal;

const styles = {
  divider: {
    width: "50%",
  },
  modal: {
    position: "absolute",
    top: "50%",
    left: "50%",
    width: "732px",
    maxHeight: "90vh",
    overflowY: "auto",
    transform: "translate(-50%, -50%)",
    backgroundColor: "background.paper",
    borderRadius: 4,
    boxShadow: 24,
    p: 4,
  },
  content: {
    maxHeight: "calc(90vh - 150px)",
    overflowY: "auto",
    paddingRight: "16px",
  },
  backdrop: {
    backdropFilter: "blur(10px)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    mb: 2,
  },
  headerTitle: {
    fontWeight: "bold",
    fontSize: "1.25rem",
  },
  footer: {
    display: "flex",
    justifyContent: "flex-end",
    mt: 2,
    gap: 2,
  },
};

export default CustomModal;
