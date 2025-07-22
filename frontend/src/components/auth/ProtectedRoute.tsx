import React, { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth, UserRole } from '../../services/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
  role: UserRole | 'any';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, role }) => {
  const { isAuthenticated, userRole } = useAuth();

  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // If role is 'any', allow access to any authenticated user
  if (role === 'any') {
    return <>{children}</>;
  }

  // Check if user has required role
  if (userRole !== role) {
    // Redirect based on user's role
    if (userRole === 'teacher') {
      return <Navigate to="/teacher" />;
    } else if (userRole === 'ta') {
      return <Navigate to="/ta" />;
    } else {
      return <Navigate to="/student" />;
    }
  }

  // If all checks pass, render the children
  return <>{children}</>;
};

export default ProtectedRoute; 