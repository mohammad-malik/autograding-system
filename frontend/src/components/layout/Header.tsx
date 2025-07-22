import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  Button,
  Container,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useAuth } from '../../services/AuthContext';

const Header: React.FC = () => {
  const { isAuthenticated, userRole, user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/login');
  };

  // Define navigation links based on user role
  const getNavLinks = () => {
    if (!isAuthenticated) {
      return [
        { text: 'Login', path: '/login' },
        { text: 'Register', path: '/register' },
      ];
    }

    switch (userRole) {
      case 'teacher':
        return [
          { text: 'Dashboard', path: '/teacher' },
          { text: 'Upload Textbook', path: '/teacher/upload-textbook' },
          { text: 'Generate Slides', path: '/teacher/generate-slides' },
          { text: 'Generate Quiz', path: '/teacher/generate-quiz' },
        ];
      case 'ta':
        return [
          { text: 'Dashboard', path: '/ta' },
          { text: 'Submit Answer Key', path: '/ta/submit-answer-key' },
          { text: 'Grade Submissions', path: '/ta/grade-submissions' },
        ];
      case 'student':
        return [
          { text: 'Dashboard', path: '/student' },
          { text: 'Submit Quiz', path: '/student/quiz-submission' },
        ];
      default:
        return [];
    }
  };

  const navLinks = getNavLinks();

  // Drawer content
  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ my: 2 }}>
        AI-Powered Educational System
      </Typography>
      <Divider />
      <List>
        {navLinks.map((link) => (
          <ListItem key={link.path} disablePadding>
            <ListItemButton
              component={RouterLink}
              to={link.path}
              sx={{ textAlign: 'center' }}
            >
              <ListItemText primary={link.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar position="static">
        <Container maxWidth="xl">
          <Toolbar disableGutters>
            <Typography
              variant="h6"
              noWrap
              component={RouterLink}
              to="/"
              sx={{
                mr: 2,
                display: { xs: 'none', md: 'flex' },
                fontWeight: 700,
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              AI-Powered Educational System
            </Typography>

            <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
              <IconButton
                size="large"
                aria-label="menu"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleDrawerToggle}
                color="inherit"
              >
                <MenuIcon />
              </IconButton>
            </Box>

            <Typography
              variant="h6"
              noWrap
              component={RouterLink}
              to="/"
              sx={{
                mr: 2,
                display: { xs: 'flex', md: 'none' },
                flexGrow: 1,
                fontWeight: 700,
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              AI-Edu System
            </Typography>

            <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
              {navLinks.map((link) => (
                <Button
                  key={link.path}
                  component={RouterLink}
                  to={link.path}
                  sx={{ my: 2, color: 'white', display: 'block' }}
                >
                  {link.text}
                </Button>
              ))}
            </Box>

            {isAuthenticated && (
              <Box sx={{ flexGrow: 0 }}>
                <IconButton
                  onClick={handleMenuOpen}
                  sx={{ p: 0, color: 'white' }}
                  aria-controls="user-menu"
                  aria-haspopup="true"
                >
                  <AccountCircleIcon />
                  <Typography sx={{ ml: 1, display: { xs: 'none', sm: 'block' } }}>
                    {user?.username || 'User'}
                  </Typography>
                </IconButton>
                <Menu
                  id="user-menu"
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                  }}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
                  <MenuItem onClick={handleLogout}>Logout</MenuItem>
                </Menu>
              </Box>
            )}
          </Toolbar>
        </Container>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Header; 