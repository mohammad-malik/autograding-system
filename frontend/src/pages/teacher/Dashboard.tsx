import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Container,
  Grid,
  Typography,
  Divider,
  CircularProgress,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SlideshowIcon from '@mui/icons-material/Slideshow';
import QuizIcon from '@mui/icons-material/Quiz';
import AssessmentIcon from '@mui/icons-material/Assessment';
import api from '../../services/api';
import { useAuth } from '../../services/AuthContext';

interface Textbook {
  id: string;
  title: string;
  author?: string;
  description?: string;
  created_at: string;
}

interface Quiz {
  id: string;
  title: string;
  description?: string;
  created_at: string;
  difficulty: string;
  submission_count: number;
  graded_count: number;
}

const TeacherDashboard: React.FC = () => {
  const { user } = useAuth();
  const [textbooks, setTextbooks] = useState<Textbook[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch textbooks
        const textbooksResponse = await api.get('/api/v1/content/textbooks');
        setTextbooks(textbooksResponse.data);

        // Fetch quizzes
        const quizzesResponse = await api.get('/api/v1/quiz/quizzes');
        setQuizzes(quizzesResponse.data);
      } catch (err: any) {
        setError('Failed to load data. Please try again later.');
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="lg" className="page-container">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" className="page-container">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome, {user?.fullName || user?.username}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your educational content and view analytics.
        </Typography>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 3 }}>
          {error}
        </Typography>
      )}

      {/* Quick Action Cards */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <UploadFileIcon color="primary" fontSize="large" />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Upload Textbook
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Upload a textbook PDF for content generation.
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  component={RouterLink}
                  to="/teacher/upload-textbook"
                  size="small"
                  color="primary"
                >
                  Upload Now
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <SlideshowIcon color="primary" fontSize="large" />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Generate Slides
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create slide presentations from textbook content.
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  component={RouterLink}
                  to="/teacher/generate-slides"
                  size="small"
                  color="primary"
                >
                  Create Slides
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <QuizIcon color="primary" fontSize="large" />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Generate Quiz
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create quizzes from textbook content.
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  component={RouterLink}
                  to="/teacher/generate-quiz"
                  size="small"
                  color="primary"
                >
                  Create Quiz
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <AssessmentIcon color="primary" fontSize="large" />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  View Analytics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View class performance analytics.
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  View Reports
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Textbooks Section */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" gutterBottom>
          Your Textbooks
        </Typography>
        {textbooks.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            You haven't uploaded any textbooks yet.
          </Typography>
        ) : (
          <Grid container spacing={3}>
            {textbooks.map((textbook) => (
              <Grid item xs={12} sm={6} md={4} key={textbook.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{textbook.title}</Typography>
                    {textbook.author && (
                      <Typography variant="body2" color="text.secondary">
                        Author: {textbook.author}
                      </Typography>
                    )}
                    {textbook.description && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {textbook.description}
                      </Typography>
                    )}
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      Uploaded on{' '}
                      {new Date(textbook.created_at).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button
                      component={RouterLink}
                      to={`/teacher/generate-slides?bookId=${textbook.id}`}
                      size="small"
                    >
                      Generate Slides
                    </Button>
                    <Button
                      component={RouterLink}
                      to={`/teacher/generate-quiz?bookId=${textbook.id}`}
                      size="small"
                    >
                      Generate Quiz
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Quizzes Section */}
      <Box>
        <Typography variant="h5" gutterBottom>
          Your Quizzes
        </Typography>
        {quizzes.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            You haven't created any quizzes yet.
          </Typography>
        ) : (
          <Grid container spacing={3}>
            {quizzes.map((quiz) => (
              <Grid item xs={12} sm={6} md={4} key={quiz.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{quiz.title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Difficulty: {quiz.difficulty}
                    </Typography>
                    {quiz.description && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {quiz.description}
                      </Typography>
                    )}
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="body2">
                      Submissions: {quiz.submission_count}
                    </Typography>
                    <Typography variant="body2">
                      Graded: {quiz.graded_count}
                    </Typography>
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      Created on {new Date(quiz.created_at).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button
                      component={RouterLink}
                      to={`/reports/class-summary/${quiz.id}`}
                      size="small"
                    >
                      View Analytics
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default TeacherDashboard; 