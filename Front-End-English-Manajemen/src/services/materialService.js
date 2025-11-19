// src/services/materialService.js
import apiClient from "./apiConfig";

const handleApiResponse = (response) => {
  if (response.status >= 200 && response.status < 300) {
    if (response.data && response.data.success === true) {
      return response.data;
    }
    if (response.data) {
      return {
        success: true,
        data: response.data,
        message: response.data.message || "Request completed successfully",
      };
    }
  }
  throw new Error(
    response.data?.message ||
      response.data?.detail ||
      `Request failed with status ${response.status}`
  );
};

const buildQueryParams = (params) => {
  const queryParams = new URLSearchParams({
    page: params.page || 1,
    limit: params.limit || 10,
  });
  if (params.search) {
    queryParams.append("search", params.search);
  }
  return queryParams;
};

export const materialService = {
  getPhonemeWordTemplate: async () => {
    try {
      const response = await apiClient.get(
        "/web/admin/phoneme-material/import-template",
        { responseType: 'blob' }
      );
      return response;
    } catch (error) {
      console.error("Get phoneme word template error:", error);
      throw error.response?.data || error;
    }
  },

  getAllValidPhonemes: async () => {
    try {
      const response = await apiClient.get("/web/admin/phonemes/all-valid");
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get all valid phonemes error:", error);
      throw error.response?.data || error;
    }
  },
  
  getExercisePhonemeTemplate: async () => {
    try {
      const response = await apiClient.get(
        "/web/admin/exercise-phoneme/import-template",
        { responseType: 'blob' }
      );
      return response;
    } catch (error) {
      console.error("Get exercise phoneme template error:", error);
      throw error.response?.data || error;
    }
  },

  getExamPhonemeTemplate: async () => {
    try {
      const response = await apiClient.get(
        "/web/admin/exam-phoneme/import-template",
        { responseType: 'blob' }
      );
      return response;
    } catch (error) {
      console.error("Get exam phoneme template error:", error);
      throw error.response?.data || error;
    }
  },

  getInterviewQuestionsTemplate: async () => {
    try {
      const response = await apiClient.get(
        "/web/admin/interview-questions/import-template",
        { responseType: 'blob' }
      );
      return response;
    } catch (error) {
      console.error("Get interview questions template error:", error);
      throw error.response?.data || error;
    }
  },

  importPhonemeWordMaterial: async (file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post(
        "/web/admin/phoneme-material/import",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Import phoneme word material error:", error);
      throw error.response?.data || error;
    }
  },

  importPhonemeSentenceMaterial: async (file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post(
        "/web/admin/exercise-phoneme/import",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Import phoneme sentence material error:", error);
      throw error.response?.data || error;
    }
  },

  importPhonemeExamMaterial: async (file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post(
        "/web/admin/exam-phoneme/import",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Import phoneme exam material error:", error);
      throw error.response?.data || error;
    }
  },

  importInterviewQuestionsMaterial: async (file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post(
        "/web/admin/interview-questions/import",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Import interview questions material error:", error);
      throw error.response?.data || error;
    }
  },

  validateExamCategory: async (category) => {
    try {
      const response = await apiClient.get(
        `/web/admin/exam-phoneme/${encodeURIComponent(category)}/validation`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Validate exam category error:", error);
      throw error.response?.data || error;
    }
  },

  getSuggestedExamCategories: async () => {
    try {
      const response = await apiClient.get(
        "/web/admin/exam-phoneme/categories/suggest"
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get suggested exam categories error:", error);
      throw error.response?.data || error;
    }
  },

  getPhonemeWordMaterials: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await apiClient.get(
        `/web/admin/phoneme-material?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get phoneme word materials error:", error);
      throw error.response?.data || error;
    }
  },

  addPhonemeWordMaterial: async (materialData) => {
    try {
      const payload = {
        phoneme_category: materialData.phoneme_category || materialData.phoneme,
        word: materialData.word,
        meaning: materialData.meaning,
        word_definition:
          materialData.word_definition || materialData.definition,
        phoneme: materialData.phoneme || materialData.phoneme_category,
      };
      const response = await apiClient.post(
        "/web/admin/phoneme-material",
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Add phoneme word material error:", error);
      throw error.response?.data || error;
    }
  },

  getPhonemeWordsByCategory: async (kategori, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await apiClient.get(
        `/web/admin/phoneme-material/${encodeURIComponent(
          kategori
        )}/detail?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get phoneme words by category error:", error);
      throw error.response?.data || error;
    }
  },

  updatePhonemeWord: async (phonemeCategory, wordId, updateData) => {
    try {
      const payload = {
        word: updateData.word,
        wordMeaning: updateData.meaning,
        wordDefinition: updateData.definition,
      };

      if (updateData.phoneme) {
        payload.phoneme = updateData.phoneme;
      }
      const response = await apiClient.put(
        `/web/admin/phoneme-material/${encodeURIComponent(
          phonemeCategory
        )}/words/${wordId}`,
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Update phoneme word error:", error);
      throw error.response?.data || error;
    }
  },

  deletePhonemeWord: async (wordId) => {
    try {
      const response = await apiClient.delete(
        `/web/admin/phoneme-material/words/${wordId}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Delete phoneme word error:", error);
      throw error.response?.data || error;
    }
  },

  getPhonemeSentenceMaterials: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await apiClient.get(
        `/web/admin/exercise-phoneme?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get phoneme sentence materials error:", error);
      throw error.response?.data || error;
    }
  },

  getPhonemeSentencesByCategory: async (category, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await apiClient.get(
        `/web/admin/exercise-phoneme/${encodeURIComponent(
          category
        )}/detail?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get phoneme sentences by category error:", error);
      throw error.response?.data || error;
    }
  },

  addPhonemeSentenceMaterial: async (sentenceData) => {
    try {
      const payload = {
        phoneme_category: sentenceData.phoneme_category,
        sentence: sentenceData.sentence,
        phoneme: sentenceData.phoneme,
      };
      const response = await apiClient.post(
        "/web/admin/exercise-phoneme/sentences",
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Add phoneme sentence material error:", error);
      throw error.response?.data || error;
    }
  },

  updatePhonemeSentence: async (sentenceId, updateData) => {
    try {
      const payload = {
        id_sentence: sentenceId,
        sentence: updateData.sentence,
        phoneme: updateData.phoneme,
      };
      const response = await apiClient.put(
        `/web/admin/exercise-phoneme/sentences/${sentenceId}`,
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Update phoneme sentence error:", error);
      throw error.response?.data || error;
    }
  },

  deletePhonemeSentence: async (sentenceId) => {
    try {
      const response = await apiClient.delete(
        `/web/admin/exercise-phoneme/sentences/${sentenceId}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Delete phoneme sentence error:", error);
      throw error.response?.data || error;
    }
  },

  getPhonemeExamMaterials: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await apiClient.get(
        `/web/admin/exam-phoneme?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get phoneme exam materials error:", error);
      throw error.response?.data || error;
    }
  },

  addPhonemeExamMaterial: async (examData) => {
    try {
      const response = await apiClient.post(
        "/web/admin/exam-phoneme/bulk-sentences",
        examData
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Add phoneme exam material error:", error);
      throw error.response?.data || error;
    }
  },

  getPhonemeExamsByCategory: async (category, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await apiClient.get(
        `/web/admin/exam-phoneme/${encodeURIComponent(
          category
        )}/detail?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get phoneme exams by category error:", error);
      throw error.response?.data || error;
    }
  },

  getExamSentenceDetail: async (category, testId) => {
    try {
      const response = await apiClient.get(
        `/web/admin/exam-phoneme/${encodeURIComponent(
          category
        )}/tests/${testId}/sentences`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get exam sentence detail error:", error);
      throw error.response?.data || error;
    }
  },

  updateExamSentence: async (sentenceId, updateData) => {
    try {
      const payload = {
        id_sentence: updateData.id_sentence,
        sentence: updateData.sentence,
        phoneme: updateData.phoneme,
      };
      const response = await apiClient.put(
        `/web/admin/exam-phoneme/sentences/${sentenceId}`,
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Update exam sentence error:", error);
      throw error.response?.data || error;
    }
  },

  deletePhonemeExam: async (category, testId) => {
    try {
      const response = await apiClient.delete(
        `/web/admin/exam-phoneme/${encodeURIComponent(
          category
        )}/tests/${testId}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Delete phoneme exam error:", error);
      throw error.response?.data || error;
    }
  },

  updatePhonemeExam: async (category, testId, examData) => {
    try {
      const payload = {
        sentences: examData.sentences.map((sentence, index) => ({
          id_sentence: typeof sentence.id_sentence === 'string' ?
            parseInt(sentence.id_sentence.replace("SEN", "")) :
            sentence.id_sentence || index + 1,
          sentence: sentence.sentence,
          phoneme: sentence.phoneme,
        })),
      };
      const response = await apiClient.put(
        `/web/admin/exam-phoneme/${encodeURIComponent(
          category
        )}/tests/${testId}`,
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Update phoneme exam error:", error);
      throw error.response?.data || error;
    }
  },

  getInterviewMaterials: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        size: params.pageSize || 10,
      });
      if (params.search) {
        queryParams.append("search", params.search);
      }
      const response = await apiClient.get(
        `/web/admin/interview-questions?${queryParams}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get interview materials error:", error);
      throw error.response?.data || error;
    }
  },

  addInterviewMaterial: async (questionData) => {
    try {
      const payload = {
        interview_question: questionData.interview_question,
      };
      const response = await apiClient.post(
        "/web/admin/interview-questions",
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Add interview material error:", error);
      throw error.response?.data || error;
    }
  },

  updateInterviewMaterial: async (id, questionData) => {
    try {
      const payload = {
        interview_question: questionData.interview_question,
      };
      const response = await apiClient.put(
        `/web/admin/interview-questions/${id}`,
        payload
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Update interview material error:", error);
      throw error.response?.data || error;
    }
  },

  deleteInterviewMaterial: async (id) => {
    try {
      const response = await apiClient.delete(
        `/web/admin/interview-questions/${id}`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Delete interview material error:", error);
      throw error.response?.data || error;
    }
  },

  swapQuestionOrder: async (questionId, direction) => {
    try {
      const response = await apiClient.post(
        `/web/admin/interview-questions/${questionId}/swap`,
        {
          direction: direction,
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Swap question order error:", error);
      throw error.response?.data || error;
    }
  },

  toggleInterviewQuestionStatus: async (questionId) => {
    try {
      const response = await apiClient.post(
        `/web/admin/interview-questions/${questionId}/toggle`
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Toggle status error:", error);
      throw error.response?.data || error;
    }
  },

  reorderAllQuestions: async (questionIdsOrder) => {
    try {
      const response = await apiClient.post(
        "/web/admin/interview-material/questions/reorder",
        {
          question_ids_order: questionIdsOrder,
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      console.error("Reorder questions error:", error);
      throw error.response?.data || error;
    }
  },

  
getQuestionsForMobile: async (limit = null) => {
    try {
      const queryParams = new URLSearchParams();
      if (limit) {
        queryParams.append("limit", limit);
      }
      let url = "/web/admin/interview-questions/mobile-order";
      const paramsString = queryParams.toString();
      if (paramsString) {
        url += `?${paramsString}`;
      }

      const response = await apiClient.get(url);
      return handleApiResponse(response);
    } catch (error) {
      console.error("Get questions for mobile error:", error);
      throw error.response?.data || error;
    }
  },

  downloadFile: async (url, fileName) => {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data]);
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
      
      return { success: true, message: 'File downloaded successfully' };
    } catch (error) {
      console.error('Download file error:', error);
      throw error.response?.data || error;
    }
  },

  validateFileBeforeUpload: (file, materialType) => {
    const errors = [];
    
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
      errors.push('Please select a valid Excel (.xlsx, .xls) or CSV file');
    }
    
    if (file.size > 10 * 1024 * 1024) {
      errors.push('File size must not exceed 10MB');
    }
    
    if (!file.name || file.name.trim() === '') {
      errors.push('File must have a valid name');
    }
    
    return {
      isValid: errors.length === 0,
      errors: errors
    };
  }
};

export default materialService;