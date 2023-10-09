import "App.css";
import {
  OneTimePasswordWrapper,
  RequiresLogin,
  TokenProvider,
} from "hooks/auth";
import AuthenticationPage from "pages/Authentication/AuthenticationPage";
import Dashboard from "pages/Dashboard/Dashboard";
import Error404Page from "pages/Error/Error404Page";
import { Route, HashRouter as Router, Routes } from "react-router-dom";

const App = () => {
  return (
    <TokenProvider>
      <Router>
        <OneTimePasswordWrapper>
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
        </OneTimePasswordWrapper>
      </Router>
    </TokenProvider>
  );
};

export default App;
