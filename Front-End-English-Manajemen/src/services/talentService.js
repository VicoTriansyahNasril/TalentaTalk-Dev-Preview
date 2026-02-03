import apiClient from "./apiConfig";

const buildParams = (params) => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page);
  if (params.limit) query.append("limit", params.limit);
  if (params.search) query.append("searchQuery", params.search);
  return query.toString();
};

export const talentService = {
  getTalentList: async (params = {}) => {
    const queryString = buildParams(params);
    const response = await apiClient.get(`/web/admin/talents?${queryString}`);
    return response.data;
  },

  getTalentById: async (talentId) => {
    const response = await apiClient.get(`/web/admin/talents/${talentId}`);
    return response.data;
  },

  getTalentProgress: async (talentId, category, params = {}) => {
    const queryString = buildParams(params);
    const response = await apiClient.get(`/web/admin/talents/${talentId}/${category}?${queryString}`);
    return response.data;
  },

  getTalentDetailProgress: async (talentId, category, subCategory, params = {}) => {
    const queryString = buildParams(params);
    const endpoint = `/web/admin/talents/${talentId}/${category}/${encodeURIComponent(subCategory)}/detail`;
    const response = await apiClient.get(`${endpoint}?${queryString}`);
    return response.data;
  },

  getTalentInterviewDetail: async (talentId, attemptId) => {
    const response = await apiClient.get(`/web/admin/talents/${talentId}/interview/${attemptId}/detail`);
    return response.data;
  },

  getTalentExamAttemptDetail: async (talentId, attemptId) => {
    const response = await apiClient.get(`/web/admin/talents/${talentId}/phoneme-exam/attempt/${attemptId}/detail`);
    return response.data;
  },

  addTalent: async (talentData) => {
    return await apiClient.post("/web/admin/talents", {
      nama: talentData.name,
      email: talentData.email,
      role: talentData.role,
      password: talentData.password
    });
  },

  editTalent: async (talentId, talentData) => {
    return await apiClient.put(`/web/admin/talents/${talentId}`, {
      nama: talentData.name,
      email: talentData.email,
      role: talentData.role
    });
  },

  deleteTalent: async (talentId) => {
    return await apiClient.delete(`/web/admin/talents/${talentId}`);
  },

  changeTalentPassword: async (talentId, passwordData) => {
    return await apiClient.put(`/web/admin/talents/${talentId}/change-password`, {
      new_password: passwordData.new_password
    });
  },

  getTalentTemplate: async () => {
    return await apiClient.get("/web/admin/talents/import-template", {
      responseType: 'blob',
    });
  },

  importTalents: async (file) => {
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
    return response.data;
  },
};