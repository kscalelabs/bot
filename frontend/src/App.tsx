import { GoogleOAuthProvider } from "@react-oauth/google";
import "App.css";
import { RequiresLogin, TokenProvider } from "hooks/auth";
import AuthenticationPage from "pages/Authentication/AuthenticationPage";
import Dashboard from "pages/Dashboard/Dashboard";
import Error404Page from "pages/Error/Error404Page";
import { Route, HashRouter as Router, Routes } from "react-router-dom";

const GOOGLE_CLIENT_ID =
  "685406162099-1u959q1m7v540vqillkc8ta5pq1nstp6.apps.googleusercontent.com";

const App = () => {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <TokenProvider>
        <Router>
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
        </Router>
      </TokenProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
