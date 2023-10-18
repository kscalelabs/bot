import "App.css";
import { ThemeProvider } from "hooks/theme";
import Dashboard from "pages/Dashboard/Dashboard";

const App = () => {
  return (
    <ThemeProvider>
      <Dashboard />
    </ThemeProvider>
  );
};

export default App;
