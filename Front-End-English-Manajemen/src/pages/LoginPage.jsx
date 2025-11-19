// src/pages/LoginPage.jsx
import React, { useState, useEffect } from "react";
import { Box, Grid, Paper, CircularProgress, Alert } from "@mui/material";
import { useFormik } from "formik";
import * as Yup from "yup";
import { useNavigate, useLocation } from "react-router-dom";

import CustomTypography from "../components/Elements/CustomTypography";
import CustomInput from "../components/Elements/CustomInput";
import CustomButton from "../components/Elements/CustomButton";
import { useAuth } from "../context/AuthContext";
import { authService } from "../services/authService";

const LoginPage = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loginError, setLoginError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const formik = useFormik({
    initialValues: {
      email: localStorage.getItem('lastLoginEmail') || "",
      password: "",
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .email("Invalid email format")
        .required("Email is required"),
      password: Yup.string()
        .min(6, "Password must be at least 6 characters")
        .required("Password is required"),
    }),
    onSubmit: async (values, { setSubmitting }) => {
      setLoginError(null);
      setIsLoading(true);
      try {
        const response = await authService.loginAdmin(values);
        
        if (response && response.success) {
          const userData = {
            name: response.data.name,
            email: response.data.email,
            role: response.data.role,
          };
          login(response.data.token, userData); 
          localStorage.setItem('lastLoginEmail', values.email);
          navigate(from, { replace: true });
        } else {
          throw new Error(response.message || "Login failed due to an unknown error.");
        }
      } catch (err) {
        setLoginError(err.message || "An unexpected error occurred. Please try again.");
        formik.setFieldValue('password', '');
      } finally {
        setIsLoading(false);
        setSubmitting(false);
      }
    },
  });

  const handleInputChange = (e) => {
    formik.handleChange(e);
    if (loginError) {
      setLoginError(null);
    }
  };

  return (
    <Grid
      container
      component="main"
      sx={{ height: "100vh", backgroundColor: "#f5f5f5" }}
    >
      <Grid
        item
        xs={false}
        sm={5}
        md={6}
        sx={{
          backgroundImage: "url('/images/login.png')",
          backgroundRepeat: "no-repeat",
          backgroundSize: "cover",
          backgroundPosition: "center",
          display: { xs: "none", sm: "block" },
        }}
      />
      <Grid
        item
        xs={12}
        sm={7}
        md={6}
        component={Paper}
        elevation={6}
        square
        sx={{ 
          display: "flex", 
          alignItems: "center", 
          justifyContent: "center",
        }}
      >
        <Box
          sx={{
            mx: 4,
            width: "100%",
            maxWidth: 400,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Box textAlign="center" mb={4}>
            <CustomTypography variant="h4" fontWeight="bold" gutterBottom>
              TalentaTalk Admin
            </CustomTypography>
            <CustomTypography
              variant="subtitle1"
              color="text.secondary"
              gutterBottom
            >
              Sign in to manage the TalentaTalk system
            </CustomTypography>
          </Box>
          <Box 
            component="form" 
            onSubmit={formik.handleSubmit} 
            noValidate 
            sx={{ mt: 1 }}
          >
            <CustomInput
              label="Email Address"
              type="email"
              name="email"
              value={formik.values.email}
              onChange={handleInputChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
              fullWidth
              disabled={isLoading}
              autoComplete="email"
              autoFocus
            />
            <CustomInput
              label="Password"
              type="password"
              name="password"
              value={formik.values.password}
              onChange={handleInputChange}
              onBlur={formik.handleBlur}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
              fullWidth
              disabled={isLoading}
              autoComplete="current-password"
            />
            {loginError && (
              <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
                {loginError}
              </Alert>
            )}
            <CustomButton
              type="submit"
              colorScheme="bgBlue"
              fullWidth
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading || !formik.isValid}
            >
              {isLoading ? (
                <Box display="flex" alignItems="center" gap={1}>
                  <CircularProgress size={20} color="inherit" />
                  Signing in...
                </Box>
              ) : (
                "Sign In"
              )}
            </CustomButton>
          </Box>
          <Box textAlign="center" mt={4}>
            <CustomTypography variant="caption" color="text.secondary">
              TalentaTalk Admin Panel v1.0
            </CustomTypography>
          </Box>
        </Box>
      </Grid>
    </Grid>
  );
};

export default LoginPage;