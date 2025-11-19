// src/services/talentService.js
import apiClient from "./apiConfig";

const handleApiResponse = (response) => {
  if (response.data && response.data.success && response.data.data !== undefined) {
    return response.data.data;
  }
  if (response.data && response.data.success) {
    return response.data;
  }
  throw new Error(response.data?.message || "Invalid response format from server");
};

export const talentService = {
  getTalentList: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        limit: params.limit || 10,
      });
      if (params.search) {
        queryParams.append("searchQuery", params.search);
      }
      const response = await apiClient.get(`/web/admin/talents?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getTalentById: async (talentId) => {
    try {
      const response = await apiClient.get(`/web/admin/talents/${talentId}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getTalentProgress: async (talentId, category, params = {}) => {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        limit: params.limit || 10,
      });
      const response = await apiClient.get(`/web/admin/talents/${talentId}/${category}?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  getTalentDetailProgress: async (talentId, category, subCategory, params = {}) => {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        limit: params.limit || 10,
      });
      const endpoint = `/web/admin/talents/${talentId}/${category}/${encodeURIComponent(subCategory)}/detail`;
      const response = await apiClient.get(`${endpoint}?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getTalentInterviewDetail: async (talentId, attemptId) => {
    try {
        const response = await apiClient.get(`/web/admin/talents/${talentId}/interview/${attemptId}/detail`);
        return handleApiResponse(response);
    } catch (error) {
        throw error.response?.data || error;
    }
  },

  getTalentExamAttemptDetail: async (talentId, attemptId) => {
    try {
      const response = await apiClient.get(`/web/admin/talents/${talentId}/phoneme-exam/attempt/${attemptId}/detail`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  addTalent: async (talentData) => {
    try {
      const response = await apiClient.post("/web/admin/talents", {
        nama: talentData.name,
        email: talentData.email,
        role: talentData.role,
        password: talentData.password
      });
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  editTalent: async (talentId, talentData) => {
    try {
      const response = await apiClient.put(`/web/admin/talents/${talentId}`, {
        nama: talentData.name,
        email: talentData.email,
        role: talentData.role
      });
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  deleteTalent: async (talentId) => {
    try {
      const response = await apiClient.delete(`/web/admin/talents/${talentId}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  changeTalentPassword: async (talentId, passwordData) => {
    try {
      const response = await apiClient.put(`/web/admin/talents/${talentId}/change-password`, {
        new_password: passwordData.new_password
      });
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getTalentTemplate: async () => {
    try {
      const response = await apiClient.get("/web/admin/talents/import-template", {
        responseType: 'blob',
      });
      return response;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  importTalents: async (file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post(
        "/web/admin/talents/import",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000,
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};