import {
  faCog,
  faMoon,
  faSignOut,
  faSun,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api } from "constants/backend";
import { deleteTokens } from "hooks/auth";
import { useTheme } from "hooks/theme";
import GenerationsPage from "pages/Dashboard/GenerationsPage/GenerationsPage";
import HomePage from "pages/Dashboard/HomePage/HomePage";
import LibraryPage from "pages/Dashboard/LibraryPage/LibraryPage";
import MakePage from "pages/Dashboard/MakePage/MakePage";
import SettingsPage from "pages/Dashboard/SettingsPage/SettingsPage";
import SingleAudioPage from "pages/Dashboard/SingleAudioPage/SingleAudioPage";
import SingleGenerationPage from "pages/Dashboard/SingleGenerationPage/SingleGenerationPage";
import Error404Page from "pages/Error/Error404Page";
import { useCallback, useEffect, useState } from "react";
import { Container, Nav, NavDropdown, Navbar } from "react-bootstrap";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";

interface UserInfoResponse {
  email: string;
}

const NavigationBar = () => {
  const { theme, setTheme } = useTheme();

  const [darkMode, setDarkMode] = useState<boolean>(theme === "dark");
  const navigate = useNavigate();
  const location = useLocation();

  const logout = useCallback(() => {
    deleteTokens();
    navigate("/login");
  }, [navigate]);

  const [email, setEmail] = useState<string | null>(null);

  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      setTheme(prev ? "light" : "dark");
      return !prev;
    });
  }, [setTheme]);

  const getActiveTab = useCallback(() => {
    switch (location.pathname) {
      case "/make":
        return "make";
      case "/library":
        return "library";
      case "/generations":
        return "generations";
      case "/":
        return "home";
      default:
        return "";
    }
  }, [location.pathname]);

  useEffect(() => {
    (async () => {
      if (email === null) {
        try {
          const response = await api.get<UserInfoResponse>("/users/me");
          setEmail(response.data.email);
        } catch (error) {
          logout();
        }
      }
    })();
  }, [email, logout]);

  return (
    <>
      <style>
        {`#basic-nav-dropdown::after {
          display: none;
        }`}
      </style>
      <Navbar>
        <Container>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav
              className="mr-auto"
              variant="underline"
              style={{ justifyContent: "center", flex: "1" }}
              activeKey={getActiveTab()}
            >
              <Nav.Item>
                <Nav.Link eventKey="home" onClick={() => navigate("/")}>
                  Home
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="make" onClick={() => navigate("/make")}>
                  Make
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link
                  eventKey="library"
                  onClick={() => navigate("/library")}
                >
                  Library
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link
                  eventKey="generations"
                  onClick={() => navigate("/generations")}
                >
                  Generations
                </Nav.Link>
              </Nav.Item>
            </Nav>

            {/* Navbar dropdown */}
            <Nav>
              <NavDropdown
                title={<i className="fa fa-lg fa-ellipsis-v" />}
                id="basic-nav-dropdown"
                align="end"
              >
                <NavDropdown.Header>{email}</NavDropdown.Header>
                <NavDropdown.Item onClick={() => navigate("/settings")}>
                  <FontAwesomeIcon icon={faCog} /> Settings
                </NavDropdown.Item>
                <NavDropdown.Item onClick={toggleDarkMode}>
                  {darkMode ? (
                    <span>
                      <FontAwesomeIcon icon={faSun} /> Light Mode
                    </span>
                  ) : (
                    <span>
                      <FontAwesomeIcon icon={faMoon} /> Dark Mode
                    </span>
                  )}
                </NavDropdown.Item>
                <NavDropdown.Item onClick={logout}>
                  <FontAwesomeIcon icon={faSignOut} /> Log Out
                </NavDropdown.Item>
              </NavDropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </>
  );
};

const Dashboard = () => {
  return (
    <Container fluid>
      <NavigationBar />
      <Container>
        <Routes>
          <Route index element={<HomePage />} />
          <Route path="make" element={<MakePage />} />
          <Route path="library" element={<LibraryPage />} />
          <Route path="generations" element={<GenerationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="audio/:id" element={<SingleAudioPage />} />
          <Route path="generation/:id" element={<SingleGenerationPage />} />
          <Route path="*" element={<Error404Page />} />
        </Routes>
      </Container>
    </Container>
  );
};

export default Dashboard;
