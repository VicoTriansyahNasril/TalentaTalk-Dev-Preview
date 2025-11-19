// src/pages/ProfilePage.jsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Avatar,
  Paper,
  Button,
  TextField,
  Stack,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  CircularProgress,
  Alert,
  Divider,
  Grid,
  Card,
  CardContent,
  CardHeader,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Person as PersonIcon,
  Save as SaveIcon,
  Lock as LockIcon,
  BadgeOutlined as AdminIdIcon,
  AlternateEmailOutlined as EmailIcon,
  SupervisorAccountOutlined as RoleIcon,
  CalendarTodayOutlined as DateIcon,
} from "@mui/icons-material";
import Swal from "sweetalert2";
import { authService } from "../services/authService";
import { useAuth } from "../context/AuthContext";

const InfoItem = ({ icon, label, value }) => (
  <Grid item xs={12} sm={6}>
    <Stack direction="row" spacing={2} alignItems="center">
      <Avatar sx={{ bgcolor: "grey.100", color: "text.secondary" }}>{icon}</Avatar>
      <Box>
        <Typography variant="caption" color="text.secondary" display="block">
          {label}
        </Typography>
        <Typography variant="body1" fontWeight={500}>
          {value}
        </Typography>
      </Box>
    </Stack>
  </Grid>
);

const ProfilePage = () => {
  const { updateUser } = useAuth();
  const [tabIndex, setTabIndex] = useState(0);
  const [profile, setProfile] = useState({ name: "", email: "", role: "N/A", adminId: "N/A", createdAt: "N/A" });
  const [form, setForm] = useState({ name: "", email: "" });
  const [passwordForm, setPasswordForm] = useState({ new_password: "", confirmPassword: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const formatDate = (dateString) => {
    if (!dateString || dateString === "N/A") return "N/A";
    try {
      return new Date(dateString).toLocaleDateString('id-ID', {
        day: '2-digit', month: 'long', year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await authService.getAdminProfile();
      
      const profileData = {
        name: response.data.fullName || response.data.name || "Admin",
        email: response.data.email || "N/A",
        role: response.data.role || "Administrator",
        adminId: response.data.adminId || "N/A",
        createdAt: formatDate(response.data.createdAt),
      };
      
      setProfile(profileData);
      setForm({ name: profileData.name, email: profileData.email });
    } catch (err) {
      setError(err.message || "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handlePasswordChange = (e) => {
    setPasswordForm({ ...passwordForm, [e.target.name]: e.target.value });
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      const updatedData = {
        name: form.name.trim(),
        email: form.email.trim(),
      };
      const response = await authService.updateAdminProfile(updatedData);

      updateUser(updatedData);

      setProfile(prev => ({ ...prev, name: form.name, email: form.email }));
      
      Swal.fire({
        icon: "success",
        title: "Profile Updated!",
        text: response.message || "Your profile has been updated successfully.",
        timer: 2000,
        showConfirmButton: false,
      });
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Update Failed!",
        text: error.message || "Failed to update profile",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleSavePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirmPassword) {
      Swal.fire({ icon: "error", title: "Password Mismatch!", text: "Passwords do not match." });
      return;
    }
    if (passwordForm.new_password.length < 6) {
      Swal.fire({ icon: "error", title: "Password Too Short!", text: "Password must be at least 6 characters." });
      return;
    }

    try {
      setSaving(true);
      const response = await authService.changeAdminPassword({ new_password: passwordForm.new_password });
      setPasswordForm({ new_password: "", confirmPassword: "" });
      Swal.fire({
        icon: "success",
        title: "Password Updated!",
        text: response.message || "Your password has been changed successfully.",
        timer: 2000,
        showConfirmButton: false,
      });
    } catch (error) {
      Swal.fire({ icon: "error", title: "Update Failed!", text: error.message || "Failed to update password" });
    } finally {
      setSaving(false);
    }
  };

  const isProfileChanged = form.name !== profile.name || form.email !== profile.email;
  const isPasswordFormValid = passwordForm.new_password && passwordForm.confirmPassword && passwordForm.new_password === passwordForm.confirmPassword && passwordForm.new_password.length >= 6;

  if (loading) {
    return (
      <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        <Button onClick={fetchProfile} variant="contained">Retry</Button>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Typography variant="h5" fontWeight={600} mb={3}>Admin Profile</Typography>
      <Card sx={{ maxWidth: 800, borderRadius: 3 }}>
        <CardHeader
          avatar={
            <Avatar sx={{ width: 64, height: 64, bgcolor: "primary.main" }}>
              <PersonIcon fontSize="large" />
            </Avatar>
          }
          title={<Typography variant="h6">{profile.name}</Typography>}
          subheader={<Typography variant="body2" color="text.secondary">{profile.email}</Typography>}
        />
        <Divider />
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabIndex} onChange={(e, newVal) => setTabIndex(newVal)} aria-label="profile tabs">
            <Tab label="Profile Information" id="profile-tab-0" aria-controls="profile-tabpanel-0" />
            <Tab label="Change Password" id="profile-tab-1" aria-controls="profile-tabpanel-1" />
          </Tabs>
        </Box>
        
        <Box role="tabpanel" hidden={tabIndex !== 0} id="profile-tabpanel-0" aria-labelledby="profile-tab-0">
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} mb={3}>Personal Details</Typography>
            <Grid container spacing={4} mb={4}>
              <InfoItem icon={<AdminIdIcon />} label="Admin ID" value={profile.adminId} />
              <InfoItem icon={<RoleIcon />} label="Role" value={profile.role} />
              <InfoItem icon={<DateIcon />} label="Account Created" value={profile.createdAt} />
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Typography variant="subtitle1" fontWeight={600} mb={2}>Edit Information</Typography>
            <Stack spacing={3}>
              <TextField label="Full Name" name="name" value={form.name} onChange={handleChange} fullWidth disabled={saving} required />
              <TextField label="Email Address" name="email" type="email" value={form.email} onChange={handleChange} fullWidth disabled={saving} required />
            </Stack>
          </CardContent>
          <Divider />
          <Box display="flex" justifyContent="flex-end" p={2}>
            <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSaveProfile} disabled={saving || !isProfileChanged}>
              {saving ? <CircularProgress size={20} color="inherit" /> : "Save Changes"}
            </Button>
          </Box>
        </Box>

        <Box role="tabpanel" hidden={tabIndex !== 1} id="profile-tabpanel-1" aria-labelledby="profile-tab-1">
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} mb={2}>Set New Password</Typography>
            <Stack spacing={3}>
              <TextField
                label="New Password"
                name="new_password"
                type={showPassword ? "text" : "password"}
                value={passwordForm.new_password}
                onChange={handlePasswordChange}
                fullWidth disabled={saving} required
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)}>{showPassword ? <VisibilityOff /> : <Visibility />}</IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <TextField
                label="Confirm New Password"
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={passwordForm.confirmPassword}
                onChange={handlePasswordChange}
                fullWidth disabled={saving} required
                error={passwordForm.confirmPassword && passwordForm.new_password !== passwordForm.confirmPassword}
                helperText={passwordForm.confirmPassword && passwordForm.new_password !== passwordForm.confirmPassword ? "Passwords do not match" : ""}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)}>{showConfirmPassword ? <VisibilityOff /> : <Visibility />}</IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Stack>
          </CardContent>
          <Divider />
          <Box display="flex" justifyContent="flex-end" p={2}>
            <Button variant="contained" startIcon={<LockIcon />} onClick={handleSavePassword} disabled={saving || !isPasswordFormValid}>
              {saving ? <CircularProgress size={20} color="inherit" /> : "Update Password"}
            </Button>
          </Box>
        </Box>
      </Card>
    </Box>
  );
};

export default ProfilePage;