import apiClient from "./apiConfig";
import DashboardEnhancements from "../utils/dashboardEnhancements";

const buildQueryParams = (params) => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page);
  if (params.activityLimit) query.append("activityLimit", DashboardEnhancements.validateActivityLimit(params.activityLimit));
  if (params.limit) query.append("limit", DashboardEnhancements.validateActivityLimit(params.limit));
  if (params.daysBack) query.append("daysBack", DashboardEnhancements.validateDaysBack(params.daysBack));
  if (params.startDate) query.append("startDate", params.startDate);
  if (params.endDate) query.append("endDate", params.endDate);
  if (params.searchQuery) query.append("searchQuery", params.searchQuery);
  if (params.category) query.append("category", params.category);
  return query.toString();
};

export const dashboardService = {
  getDashboardData: async (params = {}) => {
    const queryString = buildQueryParams(params);
    const response = await apiClient.get(`/web/admin/dashboard?${queryString}`);
    return response.data;
  },

  getPronunciationActivities: async (params = {}) => {
    const queryString = buildQueryParams(params);
    const response = await apiClient.get(`/web/admin/dashboard/pronunciation-activities?${queryString}`);
    return response.data;
  },

  getSpeakingActivities: async (params = {}) => {
    const queryString = buildQueryParams(params);
    const response = await apiClient.get(`/web/admin/dashboard/speaking-activities?${queryString}`);
    return response.data;
  },

  getTopActiveLearners: async (params = {}) => {
    const queryString = buildQueryParams(params);
    const response = await apiClient.get(`/web/admin/learners/top-active?${queryString}`);
    return response.data;
  },

  getHighestScoringLearners: async (params = {}) => {
    if (!params.category) params.category = "phoneme_material_exercise";
    const queryString = buildQueryParams(params);
    const response = await apiClient.get(`/web/admin/learners/highest-scoring?${queryString}`);
    return response.data;
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