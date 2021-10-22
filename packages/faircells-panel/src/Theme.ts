import { createMuiTheme } from '@material-ui/core/styles';

declare module '@material-ui/core/styles/createMuiTheme' {
  interface Theme {
    kale: {
      headers: {
        main: string;
      };
    };
  }

  interface ThemeOptions {
    kale?: {
      headers?: {
        main?: string;
      };
    };
  }
}

export const theme = createMuiTheme({
  palette: {
    secondary: {
      main: '#ea5b2d',
      dark: '#b12800',
      light: '#ff8c5a',
    },
    primary: {
      main: '#0f4e8a',
      dark: '#00275c',
      light: '#4e79ba',
    },
  },
});
