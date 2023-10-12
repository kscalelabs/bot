import "App.css";
import { OneTimePasswordWrapper, RequiresLogin } from "hooks/auth";
import { ClipboardProvider } from "hooks/clipboard";
import { ThemeProvider } from "hooks/theme";
import AuthenticationPage from "pages/Authentication/AuthenticationPage";
import Dashboard from "pages/Dashboard/Dashboard";
import Error404Page from "pages/Error/Error404Page";
import { Route, HashRouter as Router, Routes } from "react-router-dom";

const App = () => {
  return (
    <Router>
      <OneTimePasswordWrapper>
        <ClipboardProvider>
          <ThemeProvider>
            <Routes>
              <Route
                path="/*"
                element={
                  <RequiresLogin>
                    <Dashboard />
                  </RequiresLogin>
                }
              />
              <Route path="/login" element={<AuthenticationPage />} />
              <Route path="*" element={<Error404Page />} />
            </Routes>
          </ThemeProvider>
        </ClipboardProvider>
      </OneTimePasswordWrapper>
    </Router>
  );
};

export default App;
