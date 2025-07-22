import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// Components
import Header from './components/layout/Header';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import TeacherDashboard from './pages/teacher/Dashboard';
import TADashboard from './pages/ta/Dashboard';
import StudentDashboard from './pages/student/Dashboard';
import UploadTextbook from './pages/teacher/UploadTextbook';
import GenerateSlides from './pages/teacher/GenerateSlides';
import GenerateQuiz from './pages/teacher/GenerateQuiz';
import QuizSubmission from './pages/student/QuizSubmission';
import SubmitAnswerKey from './pages/ta/SubmitAnswerKey';
import GradeSubmissions from './pages/ta/GradeSubmissions';
import StudentReport from './pages/reports/StudentReport';
import ClassSummary from './pages/reports/ClassSummary';
import NotFound from './pages/NotFound';

// Auth
import { useAuth } from './services/AuthContext';

const App: React.FC = () => {
  const { isAuthenticated, userRole } = useAuth();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
          <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />
          
          {/* Redirect based on role */}
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                userRole === 'teacher' ? <Navigate to="/teacher" /> :
                userRole === 'ta' ? <Navigate to="/ta" /> :
                <Navigate to="/student" />
              ) : <Navigate to="/login" />
            } 
          />
          
          {/* Teacher routes */}
          <Route path="/teacher" element={<ProtectedRoute role="teacher"><TeacherDashboard /></ProtectedRoute>} />
          <Route path="/teacher/upload-textbook" element={<ProtectedRoute role="teacher"><UploadTextbook /></ProtectedRoute>} />
          <Route path="/teacher/generate-slides" element={<ProtectedRoute role="teacher"><GenerateSlides /></ProtectedRoute>} />
          <Route path="/teacher/generate-quiz" element={<ProtectedRoute role="teacher"><GenerateQuiz /></ProtectedRoute>} />
          
          {/* TA routes */}
          <Route path="/ta" element={<ProtectedRoute role="ta"><TADashboard /></ProtectedRoute>} />
          <Route path="/ta/submit-answer-key" element={<ProtectedRoute role="ta"><SubmitAnswerKey /></ProtectedRoute>} />
          <Route path="/ta/grade-submissions" element={<ProtectedRoute role="ta"><GradeSubmissions /></ProtectedRoute>} />
          
          {/* Student routes */}
          <Route path="/student" element={<ProtectedRoute role="student"><StudentDashboard /></ProtectedRoute>} />
          <Route path="/student/quiz-submission" element={<ProtectedRoute role="student"><QuizSubmission /></ProtectedRoute>} />
          
          {/* Report routes (accessible by multiple roles) */}
          <Route path="/reports/student/:submissionId" element={<ProtectedRoute role="any"><StudentReport /></ProtectedRoute>} />
          <Route path="/reports/class-summary/:quizId" element={<ProtectedRoute role="ta"><ClassSummary /></ProtectedRoute>} />
          
          {/* Catch-all */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Box>
    </Box>
  );
};

export default App; 