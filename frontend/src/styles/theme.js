import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#5F0F40', // Tyrian purple
    },
    secondary: {
      main: '#9A031E', // Carmine
    },
    warning: {
      main: '#FB8B24', // UT orange
    },
    info: {
      main: '#E36414', // Spanish orange
    },
    success: {
      main: '#0F4C5C', // Midnight green
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
});

export default theme;
