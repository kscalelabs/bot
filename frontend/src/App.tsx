import "App.css";
import { AuthenticationProvider } from "hooks/auth";
import { ClipboardProvider } from "hooks/clipboard";
import { ThemeProvider } from "hooks/theme";
import Dashboard from "pages/Dashboard/Dashboard";

const App = () => {
  return (
    <ClipboardProvider>
      <AuthenticationProvider>
        <ThemeProvider>
          <Dashboard />
        </ThemeProvider>
      </AuthenticationProvider>
    </ClipboardProvider>
  );
};

export default App;
