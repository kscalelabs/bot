import logo from "assets/logo.svg";
import { api } from "constants/backend";
import { deleteTokens } from "hooks/auth";
import DashboardContent from "pages/Dashboard/DashboardContent/DashboardContent";
import GalleryPage from "pages/Dashboard/GalleryPage/GalleryPage";
import MakePage from "pages/Dashboard/MakePage/MakePage";
import SettingsPage from "pages/Dashboard/SettingsPage/SettingsPage";
import Error404Page from "pages/Error/Error404Page";
import { useCallback, useEffect, useState } from "react";
import { Container, Nav, NavDropdown, Navbar } from "react-bootstrap";
import { Route, Routes, useNavigate } from "react-router-dom";

interface UserInfoResponse {
  email: string;
}

const NavigationBar = () => {
  const navigate = useNavigate();

  const logout = useCallback(() => {
    deleteTokens();
    navigate("/login");
  }, [navigate]);

  const [email, setEmail] = useState<string | null>(null);

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
          {/* Site icon */}
          <Navbar.Brand href="#" onClick={() => navigate("/")}>
            <img src={logo} alt="logo" width="30" height="30" />
          </Navbar.Brand>

          {/* Navbar choices */}
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav
              className="mr-auto"
              variant="pills"
              style={{ justifyContent: "center", flex: "1" }}
            >
              <Nav.Link
                onClick={() => navigate("/make")}
                style={{ margin: "0 1em" }}
              >
                <i className="fa fa-star" /> Make
              </Nav.Link>
              <Nav.Link
                onClick={() => navigate("/gallery")}
                style={{ margin: "0 1em" }}
              >
                <i className="fa fa-picture-o" /> Gallery
              </Nav.Link>
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
                  <i className="fa fa-cog" /> Settings
                </NavDropdown.Item>
                <NavDropdown.Item onClick={logout}>
                  <i className="fa fa-sign-out" /> Logout
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
          <Route index element={<DashboardContent />} />
          <Route path="gallery" element={<GalleryPage />} />
          <Route path="make" element={<MakePage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Error404Page />} />
        </Routes>
      </Container>
    </Container>
  );
};

export default Dashboard;
