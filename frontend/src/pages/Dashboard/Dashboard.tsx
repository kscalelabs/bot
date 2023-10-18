import NavigationBar from "components/navigation/NavigationBar";
import { AlertQueue, AlertQueueProvider } from "hooks/alerts";
import { AuthenticationProvider, OneTimePasswordWrapper } from "hooks/auth";
import { ClipboardProvider } from "hooks/clipboard";
import { ThemeProvider } from "hooks/theme";
import HomePage from "pages/Dashboard/HomePage/HomePage";
import SettingsPage from "pages/Dashboard/SettingsPage/SettingsPage";
import SingleAudioPage from "pages/Dashboard/SingleAudioPage/SingleAudioPage";
import SingleGenerationPage from "pages/Dashboard/SingleGenerationPage/SingleGenerationPage";
import UploadPage from "pages/Dashboard/UploadPage/UploadPage";
import Error404Page from "pages/Error/Error404Page";
import { Container } from "react-bootstrap";
import { Route, HashRouter as Router, Routes } from "react-router-dom";
import MixPage from "./MixPage/MixPage";

const Dashboard = () => {
  return (
    <Router>
      <ThemeProvider>
        <AuthenticationProvider>
          <AlertQueueProvider>
            <ClipboardProvider>
              <AlertQueue>
                <NavigationBar />
                <Container>
                  <OneTimePasswordWrapper>
                    <Routes>
                      <Route index element={<HomePage />} />
                      <Route path="upload" element={<UploadPage />} />
                      <Route path="mix" element={<MixPage />} />
                      <Route path="settings" element={<SettingsPage />} />
                      <Route path="audio/:id" element={<SingleAudioPage />} />
                      <Route
                        path="generation/:id"
                        element={<SingleGenerationPage />}
                      />
                      <Route path="*" element={<Error404Page />} />
                    </Routes>
                  </OneTimePasswordWrapper>
                </Container>
              </AlertQueue>
            </ClipboardProvider>
          </AlertQueueProvider>
        </AuthenticationProvider>
      </ThemeProvider>
    </Router>
  );
};

export default Dashboard;
