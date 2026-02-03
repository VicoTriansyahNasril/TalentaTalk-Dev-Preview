import apiClient from "./apiConfig";

const buildParams = (params) => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page);
  if (params.limit) query.append("limit", params.limit);
  if (params.pageSize) query.append("size", params.pageSize);
  if (params.search) query.append("search", params.search);
  return query.toString();
};

export const materialService = {
  // --- TEMPLATES ---
  getPhonemeWordTemplate: async () => apiClient.get("/web/admin/phoneme-material/import-template", { responseType: 'blob' }),
  getExercisePhonemeTemplate: async () => apiClient.get("/web/admin/exercise-phoneme/import-template", { responseType: 'blob' }),
  getExamPhonemeTemplate: async () => apiClient.get("/web/admin/exam-phoneme/import-template", { responseType: 'blob' }),
  getInterviewQuestionsTemplate: async () => apiClient.get("/web/admin/interview-questions/import-template", { responseType: 'blob' }),

  importPhonemeWordMaterial: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/web/admin/phoneme-material/import", formData, { headers: { "Content-Type": "multipart/form-data" }, timeout: 60000 });
    return response;
  },
  importPhonemeSentenceMaterial: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/web/admin/exercise-phoneme/import", formData, { headers: { "Content-Type": "multipart/form-data" }, timeout: 60000 });
    return response;
  },
  importPhonemeExamMaterial: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/web/admin/exam-phoneme/import", formData, { headers: { "Content-Type": "multipart/form-data" }, timeout: 60000 });
    return response;
  },
  importInterviewQuestionsMaterial: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/web/admin/interview-questions/import", formData, { headers: { "Content-Type": "multipart/form-data" }, timeout: 60000 });
    return response;
  },

  // --- PHONEME WORDS ---
  getPhonemeWordMaterials: async (params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/phoneme-material?${qs}`);
    return response; // FIXED
  },
  getPhonemeWordsByCategory: async (category, params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/phoneme-material/${encodeURIComponent(category)}/detail?${qs}`);
    return response; // FIXED
  },
  addPhonemeWordMaterial: async (data) => {
    const payload = {
      phoneme_category: data.phoneme_category || data.phoneme,
      word: data.word,
      meaning: data.meaning,
      word_definition: data.word_definition || data.definition,
      phoneme: data.phoneme || data.phoneme_category,
    };
    return await apiClient.post("/web/admin/phoneme-material", payload);
  },
  updatePhonemeWord: async (category, id, data) => {
    const payload = {
      word: data.word,
      wordMeaning: data.meaning,
      wordDefinition: data.definition,
      phoneme: data.phoneme
    };
    return await apiClient.put(`/web/admin/phoneme-material/${encodeURIComponent(category)}/words/${id}`, payload);
  },
  deletePhonemeWord: async (id) => {
    return await apiClient.delete(`/web/admin/phoneme-material/words/${id}`);
  },

  // --- EXERCISE SENTENCES ---
  getPhonemeSentenceMaterials: async (params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/exercise-phoneme?${qs}`);
    return response; // FIXED
  },
  getPhonemeSentencesByCategory: async (category, params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/exercise-phoneme/${encodeURIComponent(category)}/detail?${qs}`);
    return response; // FIXED
  },
  addPhonemeSentenceMaterial: async (data) => {
    const payload = { phoneme_category: data.category, sentence: data.sentence, phoneme: data.phoneme };
    return await apiClient.post("/web/admin/exercise-phoneme/sentences", payload);
  },
  updatePhonemeSentence: async (id, data) => {
    const payload = { sentence: data.sentence, phoneme: data.phoneme };
    return await apiClient.put(`/web/admin/exercise-phoneme/sentences/${id}`, payload);
  },
  deletePhonemeSentence: async (id) => {
    return await apiClient.delete(`/web/admin/exercise-phoneme/sentences/${id}`);
  },

  // --- EXAMS ---
  getPhonemeExamMaterials: async (params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/exam-phoneme?${qs}`);
    return response; // FIXED
  },
  getPhonemeExamsByCategory: async (category, params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/exam-phoneme/${encodeURIComponent(category)}/detail?${qs}`);
    return response; // FIXED
  },
  getExamSentenceDetail: async (category, testId) => {
    const response = await apiClient.get(`/web/admin/exam-phoneme/${encodeURIComponent(category)}/tests/${testId}/sentences`);
    return response; // FIXED
  },
  addPhonemeExamMaterial: async (data) => {
    return await apiClient.post("/web/admin/exam-phoneme/bulk-sentences", data);
  },
  updatePhonemeExam: async (category, testId, data) => {
    const payload = {
      sentences: data.sentences.map((s) => ({
        id_sentence: s.id_sentence || s.sentenceId,
        sentence: s.sentence,
        phoneme: s.phoneme
      }))
    };
    return await apiClient.put(`/web/admin/exam-phoneme/${encodeURIComponent(category)}/tests/${testId}`, payload);
  },
  deletePhonemeExam: async (category, testId) => {
    return await apiClient.delete(`/web/admin/exam-phoneme/${encodeURIComponent(category)}/tests/${testId}`);
  },

  // --- INTERVIEW ---
  getInterviewMaterials: async (params = {}) => {
    const qs = buildParams(params);
    const response = await apiClient.get(`/web/admin/interview-questions?${qs}`);
    return response;
  },
  addInterviewMaterial: async (data) => {
    return await apiClient.post("/web/admin/interview-questions", { interview_question: data.interview_question });
  },
  updateInterviewMaterial: async (id, data) => {
    return await apiClient.put(`/web/admin/interview-questions/${id}`, { interview_question: data.interview_question });
  },
  deleteInterviewMaterial: async (id) => {
    return await apiClient.delete(`/web/admin/interview-questions/${id}`);
  },
  toggleInterviewQuestionStatus: async (id) => {
    const response = await apiClient.post(`/web/admin/interview-questions/${id}/toggle`);
    return response;
  },
  swapQuestionOrder: async (id, direction) => {
    const response = await apiClient.post(`/web/admin/interview-questions/${id}/swap`, { direction });
    return response;
  },
  getQuestionsForMobile: async (limit = null) => {
    const qs = limit ? `?limit=${limit}` : '';
    const response = await apiClient.get(`/web/admin/interview-questions/mobile-order${qs}`);
    return response;
  },

  // --- HELPERS ---
  getAllValidPhonemes: async () => {
    const response = await apiClient.get("/web/admin/phonemes/all-valid");
    return response;
  },
  validateExamCategory: async (category) => {
    const response = await apiClient.get(`/web/admin/exam-phoneme/${encodeURIComponent(category)}/validation`);
    return response;
  },
  getSuggestedExamCategories: async () => {
    const response = await apiClient.get("/web/admin/exam-phoneme/categories/suggest");
    return response;
  }
};

export default materialService;