import {
  faCog,
  faMoon,
  faSignOut,
  faSun,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuthentication } from "hooks/auth";
import { useTheme } from "hooks/theme";
import { useCallback, useEffect, useState } from "react";
import { Container, Nav, NavDropdown, Navbar } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

interface UserInfoResponse {
  email: string;
}

const NavigationBar = () => {
  const { isAuthenticated, logout, api } = useAuthentication();
  const { theme, setTheme } = useTheme();

  const [darkMode, setDarkMode] = useState<boolean>(theme === "dark");
  const navigate = useNavigate();

  const [email, setEmail] = useState<string | null>(null);

  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      setTheme(prev ? "light" : "dark");
      return !prev;
    });
  }, [setTheme]);

  useEffect(() => {
    (async () => {
      if (isAuthenticated) {
        if (email === null) {
          try {
            const response = await api.get<UserInfoResponse>("/users/me");
            setEmail(response.data.email);
          } catch (error) {}
        }
      } else {
        setEmail(null);
      }
    })();
  }, [email, isAuthenticated, api]);

  return (
    <>
      <Navbar expand="lg">
        <Container fluid>
          <Navbar.Toggle />
          <Navbar.Collapse className="justify-content-between">
            {/* Navigation */}
            <Nav className="justify-content-center mx-auto">
              <Nav.Item>
                <Nav.Link eventKey="home" onClick={() => navigate("/")}>
                  home
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="upload" onClick={() => navigate("/upload")}>
                  upload
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="mix" onClick={() => navigate("/mix")}>
                  mix
                </Nav.Link>
              </Nav.Item>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Drop-down menu */}
      <Nav style={{ position: "absolute", right: 5, top: 5 }}>
        <style>{`#nav-dropdown::after { display: none; }`}</style>
        <NavDropdown
          title={<FontAwesomeIcon icon={faCog} />}
          id="nav-dropdown"
          align="end"
        >
          {email !== null && <NavDropdown.Header>{email}</NavDropdown.Header>}
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
          {isAuthenticated && (
            <NavDropdown.Item onClick={logout}>
              <FontAwesomeIcon icon={faSignOut} /> Log Out
            </NavDropdown.Item>
          )}
        </NavDropdown>
      </Nav>
    </>
  );
};

export default NavigationBar;
