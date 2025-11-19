// src/services/authService.js
import apiClient from "./apiConfig";

export const authService = {
  loginAdmin: async (credentials) => {
    try {
      const response = await apiClient.post("/web/admin/login", {
        email: credentials.email,
        password: credentials.password
      });
      
      if (response.data && response.data.success && response.data.data) {
        return response.data;
      }
      
      throw new Error("Invalid response format from server");

    } catch (error) {
      if (error.response && error.response.data && error.response.data.message) {
        throw new Error(error.response.data.message);
      }
      if (error.response && error.response.status === 401) {
        throw new Error("Invalid email or password.");
      }
      throw new Error(error.message || "Login failed. Please try again.");
    }
  },

  getAdminProfile: async () => {
    try {
      const response = await apiClient.get("/web/admin/profile");
      if (response.data && response.data.success) {
        return response.data;
      }
      throw new Error("Failed to get profile");
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  updateAdminProfile: async (profileData) => {
    try {
      const response = await apiClient.put("/web/admin/profile", {
        nama: profileData.name,
        email: profileData.email
      });
      if (response.data && response.data.success) {
        return response.data;
      }
      throw new Error("Update failed");
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  changeAdminPassword: async (passwordData) => {
    try {
      const response = await apiClient.put("/web/admin/profile/change-password", {
        new_password: passwordData.new_password
      });
      if (response.data && response.data.success) {
        return response.data;
      }
      throw new Error("Password change failed");
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('lastLoginEmail');
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      if (payload.exp < currentTime) {
        authService.logout();
        return false;
      }
      return true;
    } catch (error) {
      authService.logout();
      return false;
    }
  },
};