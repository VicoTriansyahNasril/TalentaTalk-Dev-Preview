// src/App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";

// Auth Context
import { useAuth } from "./context/AuthContext";

// Layout Components
import DashboardLayout from "./components/Layout/DashboardLayout";

// Page Components
import LoginPage from "./pages/LoginPage";
import DashboardHomePage from "./pages/Home/DashboardHomePage";
import ViewDetailPage from "./pages/Home/ViewDetail/ViewDetailPage";
import ProfilePage from "./pages/ProfilePage";

// Talent Pages
import TalentListPage from "./pages/TalentPages/TalentListPage";
import TalentDetailPage from "./pages/TalentPages/TalentDetailPage";
import TalentPronunciationCategoryDetail from "./pages/TalentPages/TalentPronunciationCategoryDetail";
import TalentPhonemeMaterialExerciseDetail from "./pages/TalentPages/TalentPhonemeMaterialExerciseDetail";
import TalentPhonemeExamCategoryDetail from "./pages/TalentPages/TalentPhonemeExamCategoryDetail";
import TalentInterviewDetail from "./pages/TalentPages/TalentInterviewDetail";
import TalentPhonemeExamAttemptDetail from "./pages/TalentPages/TalentPhonemeExamAttemptDetail"; // ✅ TAMBAH IMPORT INI

// Material Pages
import MaterialPronunciationPage from "./pages/MaterialPages/MaterialPronunciationPage";
import MaterialConversationPage from "./pages/MaterialPages/MaterialInterviewPage";
import PhonemeDetailPage from "./pages/MaterialPages/PhonemeDetailPage";
import ExercisePhonemeDetailPage from "./pages/MaterialPages/ExercisePhonemeDetailPage";
import ExamCategoryDetailPage from "./pages/MaterialPages/ExamCategoryDetailPage";

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="#f5f5f5"
      >
        <CircularProgress size={40} />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="#f5f5f5"
      >
        <CircularProgress size={40} />
      </Box>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

const App = () => {
  return (
    <Router>
      <Routes>

        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          
          <Route path="dashboard" element={<DashboardHomePage />} />
          <Route path="view-detail" element={<ViewDetailPage />} />

          <Route path="profile" element={<ProfilePage />} />

          <Route path="talents" element={<TalentListPage />} />
          <Route path="talent/:id" element={<TalentDetailPage />} />
          <Route
            path="talent/:id/pronunciation/:kategori"
            element={<TalentPronunciationCategoryDetail />}
          />
          <Route
            path="talent/:id/phoneme-material/:phoneme"
            element={<TalentPhonemeMaterialExerciseDetail />}
          />
          <Route
            path="talent/:id/phoneme-exam/:category"
            element={<TalentPhonemeExamCategoryDetail />}
          />
          <Route path="talent/:id/interview/:attemptId/detail" element={<TalentInterviewDetail />} />
          <Route
            path="talent/:id/phoneme-exam/attempt/:attemptId/detail"
            element={<TalentPhonemeExamAttemptDetail />}
          />
          
          <Route
            path="pronunciation-material"
            element={<MaterialPronunciationPage />}
          />
          <Route
            path="conversation-material"
            element={<MaterialConversationPage />}
          />
          <Route
            path="material/pronunciation"
            element={<MaterialPronunciationPage />}
          />
          <Route
            path="material/pronunciation/:phoneme"
            element={<PhonemeDetailPage />}
          />
          <Route
            path="material/exercise/:category"
            element={<ExercisePhonemeDetailPage />}
          />
          <Route
            path="exam-phoneme/:category"
            element={<ExamCategoryDetailPage />}
          />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};

export default App;