import { GoogleOAuthProvider } from "@react-oauth/google";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "./App.css";
import { RequiresLogin, TokenProvider } from "./hooks/auth";
import Dashboard from "./pages/Dashboard/Dashboard";
import Error404 from "./pages/Error/Error404";
import Login from "./pages/Login/Login";

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
            <Route path="/login" element={<Login />} />
            <Route path="*" element={<Error404 />} />
          </Routes>
        </Router>
      </TokenProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
