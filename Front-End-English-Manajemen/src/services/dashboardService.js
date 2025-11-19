// src/services/dashboardService.js - Clean Version with Enhanced Utilities
import apiClient from "./apiConfig";
import DashboardEnhancements from "../utils/dashboardEnhancements";

const handleApiResponse = (response) => {
  if (response.data && response.data.success && response.data.data) {
    return response.data.data;
  }
  throw new Error(response.data?.message || "Invalid response format from server");
};

export const dashboardService = {

  getDashboardData: async (params = {}) => {
    try {

      const validatedLimit = DashboardEnhancements.validateActivityLimit(params.activityLimit || 10);
      const validatedDaysBack = DashboardEnhancements.validateDaysBack(params.daysBack || 30);
      
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        activityLimit: validatedLimit,
        daysBack: validatedDaysBack,
      });

      if (params.startDate) {
        queryParams.append("startDate", params.startDate);
      }
      if (params.endDate) {
        queryParams.append("endDate", params.endDate);
      }
      
      const response = await apiClient.get(`/web/admin/dashboard?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getPronunciationActivities: async (params = {}) => {
    try {
      const validatedLimit = DashboardEnhancements.validateActivityLimit(params.limit || 10);
      const validatedDaysBack = DashboardEnhancements.validateDaysBack(params.daysBack || 30);
      
      const queryParams = new URLSearchParams({
        limit: validatedLimit,
        daysBack: validatedDaysBack,
      });
      
      const response = await apiClient.get(`/web/admin/dashboard/pronunciation-activities?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getSpeakingActivities: async (params = {}) => {
    try {
      const validatedLimit = DashboardEnhancements.validateActivityLimit(params.limit || 10);
      const validatedDaysBack = DashboardEnhancements.validateDaysBack(params.daysBack || 30);
      
      const queryParams = new URLSearchParams({
        limit: validatedLimit,
        daysBack: validatedDaysBack,
      });
      
      const response = await apiClient.get(`/web/admin/dashboard/speaking-activities?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getTopActiveLearners: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        limit: params.limit || 10,
      });
      if (params.searchQuery) {
        queryParams.append("searchQuery", params.searchQuery);
      }
      const response = await apiClient.get(`/web/admin/learners/top-active?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getHighestScoringLearners: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams({
        category: params.category || "phoneme_material_exercise",
        page: params.page || 1,
        limit: params.limit || 10,
      });
      if (params.searchQuery) {
        queryParams.append("searchQuery", params.searchQuery);
      }
      const response = await apiClient.get(`/web/admin/learners/highest-scoring?${queryParams}`);
      return handleApiResponse(response);
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getActivityLimitOptions: () => DashboardEnhancements.limitOptions,
  validateActivityLimit: DashboardEnhancements.validateActivityLimit,
  validateDaysBack: DashboardEnhancements.validateDaysBack,
  getDefaultSettings: () => DashboardEnhancements.defaultSettings,

  saveSettings: DashboardEnhancements.saveSettings,
  loadSettings: DashboardEnhancements.loadSettings,

  generateInfoMessage: DashboardEnhancements.generateInfoMessage,
  generateActivityBadges: DashboardEnhancements.generateActivityBadges,
  generateEmptyStateMessage: DashboardEnhancements.generateEmptyStateMessage,
  generateActivitySummary: DashboardEnhancements.generateActivitySummary,
  generateTableFooterInfo: DashboardEnhancements.generateTableFooterInfo,

  getWPMColorAndMessage: DashboardEnhancements.getWPMColorAndMessage,
  getScoreColorAndMessage: DashboardEnhancements.getScoreColorAndMessage,

  trackSettingsChange: DashboardEnhancements.trackSettingsChange
};

export default dashboardService;