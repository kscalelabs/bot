import NavigationBar from "components/navigation/NavigationBar";
import { AuthenticationProvider, OneTimePasswordWrapper } from "hooks/auth";
import HomePage from "pages/Dashboard/HomePage/HomePage";
import MakePage from "pages/Dashboard/MakePage/MakePage";
import SettingsPage from "pages/Dashboard/SettingsPage/SettingsPage";
import SingleAudioPage from "pages/Dashboard/SingleAudioPage/SingleAudioPage";
import SingleGenerationPage from "pages/Dashboard/SingleGenerationPage/SingleGenerationPage";
import Error404Page from "pages/Error/Error404Page";
import { Container } from "react-bootstrap";
import { Route, HashRouter as Router, Routes } from "react-router-dom";

const Dashboard = () => {
  return (
    <Router>
      <AuthenticationProvider>
        <NavigationBar />
        <Container>
          <OneTimePasswordWrapper>
            <Routes>
              <Route index element={<HomePage />} />
              <Route path="make" element={<MakePage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="audio/:id" element={<SingleAudioPage />} />
              <Route path="generation/:id" element={<SingleGenerationPage />} />
              <Route path="*" element={<Error404Page />} />
            </Routes>
          </OneTimePasswordWrapper>
        </Container>
      </AuthenticationProvider>
    </Router>
  );
};

export default Dashboard;
