import apiClient from "./apiConfig";

export const authService = {
  loginAdmin: async (credentials) => {
    return await apiClient.post("/web/admin/login", {
      email: credentials.email,
      password: credentials.password
    });
  },

  getAdminProfile: async () => {
    return await apiClient.get("/web/admin/profile");
  },

  updateAdminProfile: async (profileData) => {
    return await apiClient.put("/web/admin/profile", {
      nama: profileData.name,
      email: profileData.email
    });
  },

  changeAdminPassword: async (passwordData) => {
    return await apiClient.put("/web/admin/profile/change-password", {
      new_password: passwordData.new_password
    });
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
        localStorage.removeItem('token');
        localStorage.removeItem('lastLoginEmail');
        return false;
      }
      return true;
    } catch {
      localStorage.removeItem('token');
      return false;
    }
  },
};