// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect, useCallback } from "react";
import { authService } from "../services/authService";
import apiClient from "../services/apiConfig";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const verifyAuth = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (token && authService.isAuthenticated()) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      try {
        const response = await authService.getAdminProfile();
        setUser(response.data);
      } catch (error) {
        console.error("Failed to fetch user profile on auth verify:", error);
        logout();
      }
    } else {
      setIsAuthenticated(false);
      setUser(null);
      localStorage.removeItem("token");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    verifyAuth();
  }, [verifyAuth]);

  const login = (token, userData) => {
    localStorage.setItem("token", token);
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    authService.logout();
    delete apiClient.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = '/login'; 
  };

  const updateUser = (newUserData) => {
    setUser(prevUser => ({
      ...prevUser,
      ...newUserData,
      fullName: newUserData.name, 
    }));
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};