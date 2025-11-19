// src/pages/TalentPages/AddOrEditTalentForm.jsx
import React, { useEffect, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Stack,
  IconButton,
  Alert,
  Tabs,
  Tab,
  Box,
  DialogActions,
  CircularProgress,
  InputAdornment,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import PersonIcon from "@mui/icons-material/Person";
import LockResetIcon from "@mui/icons-material/LockReset";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { useFormik } from "formik";
import * as Yup from "yup";
import Swal from "sweetalert2";

import CustomInput from "../../components/Elements/CustomInput";
import CustomButton from "../../components/Elements/CustomButton";

const AddOrEditTalentForm = ({
  open,
  onClose,
  onSubmit,
  defaultValues = null,
  isEdit = false,
  onEditProfile,
  onChangePassword,
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [passwordForm, setPasswordForm] = useState({ newPassword: "", confirmPassword: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const formik = useFormik({
    initialValues: {
      name: "",
      email: "",
      role: "",
      password: "",
    },
    validationSchema: Yup.object({
      name: Yup.string().min(2, "Name must be at least 2 characters").required("Name is required"),
      email: Yup.string().email("Invalid email format").required("Email is required"),
      role: Yup.string().required("Role is required"),
      password: isEdit
        ? Yup.string()
        : Yup.string().min(6, "Password must be at least 6 characters").required("Password is required"),
    }),
    onSubmit: async (values) => {
      setIsSubmitting(true);
      await onSubmit(values);
      setIsSubmitting(false);
    },
    enableReinitialize: true,
  });

  useEffect(() => {
    if (open) {
      if (isEdit && defaultValues) {
        formik.setValues({
          name: defaultValues.talentName || "",
          email: defaultValues.email || "",
          role: defaultValues.role || "",
          password: "",
        });
      } else {
        formik.resetForm();
      }
      setActiveTab(0);
      setPasswordForm({ newPassword: "", confirmPassword: "" });
    }
  }, [open, isEdit, defaultValues]);

  const handleClose = () => {
    formik.resetForm();
    onClose();
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handlePasswordFormChange = (e) => {
    setPasswordForm({ ...passwordForm, [e.target.name]: e.target.value });
  };

  const handleProfileUpdate = async () => {
    setIsSubmitting(true);
    try {
      await onEditProfile({
        name: formik.values.name,
        email: formik.values.email,
        role: formik.values.role,
      });
    } catch (error) {
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePasswordUpdate = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      Swal.fire("Error", "Passwords do not match.", "error");
      return;
    }
    if (passwordForm.newPassword.length < 6) {
      Swal.fire("Error", "Password must be at least 6 characters.", "error");
      return;
    }
    setIsSubmitting(true);
    try {
      await onChangePassword({ new_password: passwordForm.newPassword });
      setPasswordForm({ newPassword: "", confirmPassword: "" });
    } catch (error) {
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const isProfileChanged = isEdit && defaultValues ? 
    formik.values.name !== defaultValues.talentName ||
    formik.values.email !== defaultValues.email ||
    formik.values.role !== defaultValues.role
    : false;

  const isPasswordFormValid = passwordForm.newPassword.length >= 6 && passwordForm.newPassword === passwordForm.confirmPassword;

  if (!isEdit) {
    return (
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          Add New Talent
          <IconButton onClick={handleClose}><CloseIcon /></IconButton>
        </DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <Stack spacing={2} pt={1}>
              <Alert severity="info">Create a new talent account. All fields are required.</Alert>
              <CustomInput label="Full Name" name="name" value={formik.values.name} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.name && Boolean(formik.errors.name)} helperText={formik.touched.name && formik.errors.name} fullWidth required />
              <CustomInput label="Email Address" name="email" type="email" value={formik.values.email} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.email && Boolean(formik.errors.email)} helperText={formik.touched.email && formik.errors.email} fullWidth required />
              <CustomInput label="Role" name="role" value={formik.values.role} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.role && Boolean(formik.errors.role)} helperText={formik.touched.role && formik.errors.role} fullWidth required />
              <CustomInput label="Password" name="password" type="password" value={formik.values.password} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.password && Boolean(formik.errors.password)} helperText={formik.touched.password ? formik.errors.password : "Minimum 6 characters"} fullWidth required />
            </Stack>
          </DialogContent>
          <DialogActions sx={{ p: 2, gap: 1 }}>
            <CustomButton colorScheme="bgWhite" onClick={handleClose} disabled={isSubmitting}>Cancel</CustomButton>
            <CustomButton type="submit" colorScheme="bgBlue" disabled={isSubmitting || !formik.isValid}>
              {isSubmitting ? "Saving..." : "Add Talent"}
            </CustomButton>
          </DialogActions>
        </form>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        Edit Talent
        <IconButton onClick={handleClose}><CloseIcon /></IconButton>
      </DialogTitle>
      <DialogContent sx={{ p: 0 }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<PersonIcon />} iconPosition="start" label="Personal Information" />
          <Tab icon={<LockResetIcon />} iconPosition="start" label="Change Password" />
        </Tabs>
        <Box p={3}>
          {activeTab === 0 && (
            <Stack spacing={2}>
              <CustomInput label="Name" name="name" value={formik.values.name} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.name && Boolean(formik.errors.name)} helperText={formik.touched.name && formik.errors.name} fullWidth required />
              <CustomInput label="Email Address" name="email" type="email" value={formik.values.email} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.email && Boolean(formik.errors.email)} helperText={formik.touched.email && formik.errors.email} fullWidth required />
              <CustomInput label="Role" name="role" value={formik.values.role} onChange={formik.handleChange} onBlur={formik.handleBlur} error={formik.touched.role && Boolean(formik.errors.role)} helperText={formik.touched.role && formik.errors.role} fullWidth required />
            </Stack>
          )}
          {activeTab === 1 && (
            <Stack spacing={2}>
              <CustomInput label="Enter New Password" name="newPassword" type={showPassword ? "text" : "password"} value={passwordForm.newPassword} onChange={handlePasswordFormChange} fullWidth required InputProps={{ endAdornment: ( <InputAdornment position="end"> <IconButton onClick={() => setShowPassword(!showPassword)}>{showPassword ? <VisibilityOff /> : <Visibility />}</IconButton> </InputAdornment> ), }} />
              <CustomInput label="Re-type New Password" name="confirmPassword" type={showConfirmPassword ? "text" : "password"} value={passwordForm.confirmPassword} onChange={handlePasswordFormChange} fullWidth required error={passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword} helperText={passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword ? "Passwords do not match" : ""} InputProps={{ endAdornment: ( <InputAdornment position="end"> <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)}>{showConfirmPassword ? <VisibilityOff /> : <Visibility />}</IconButton> </InputAdornment> ), }} />
            </Stack>
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <CustomButton colorScheme="bgWhite" onClick={handleClose} disabled={isSubmitting}>Cancel</CustomButton>
        {activeTab === 0 && (
          <CustomButton colorScheme="bgBlue" onClick={handleProfileUpdate} disabled={isSubmitting || !formik.isValid || !isProfileChanged}>
            {isSubmitting ? <CircularProgress size={24} color="inherit" /> : "Save"}
          </CustomButton>
        )}
        {activeTab === 1 && (
          <CustomButton colorScheme="bgBlue" onClick={handlePasswordUpdate} disabled={isSubmitting || !isPasswordFormValid}>
            {isSubmitting ? <CircularProgress size={24} color="inherit" /> : "Save"}
          </CustomButton>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default AddOrEditTalentForm;