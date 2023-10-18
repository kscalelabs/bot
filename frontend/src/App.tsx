import "App.css";
import { ClipboardProvider } from "hooks/clipboard";
import { ThemeProvider } from "hooks/theme";
import Dashboard from "pages/Dashboard/Dashboard";

const App = () => {
  return (
    <ClipboardProvider>
      <ThemeProvider>
        <Dashboard />
      </ThemeProvider>
    </ClipboardProvider>
  );
};

export default App;
