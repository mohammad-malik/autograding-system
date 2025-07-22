import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Button, Container, Typography } from '@mui/material';
import { useAuth } from '../services/AuthContext';

const NotFound: React.FC = () => {
  const { isAuthenticated, userRole } = useAuth();
  
  // Determine home path based on user role
  const getHomePath = () => {
    if (!isAuthenticated) {
      return '/login';
    }
    
    switch (userRole) {
      case 'teacher':
        return '/teacher';
      case 'ta':
        return '/ta';
      case 'student':
        return '/student';
      default:
        return '/login';
    }
  };
  
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '80vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          The page you are looking for does not exist or has been moved.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          component={RouterLink}
          to={getHomePath()}
          sx={{ mt: 3 }}
        >
          Go to Home
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound; 