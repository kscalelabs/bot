import { Container, Nav, NavDropdown, Navbar } from "react-bootstrap";
import { Route, Routes, useNavigate } from "react-router-dom";
import { useToken } from "../../hooks/auth";
import DashboardContent from "./DashboardContent/DashboardContent";
import GalleryPage from "./GalleryPage/GalleryPage";
import HistoryPage from "./HistoryPage/HistoryPage";
import SettingsPage from "./SettingsPage/SettingsPage";

const NavigationBar = () => {
  const { setToken } = useToken();
  const navigate = useNavigate();

  const logout = () => {
    setToken(null);
    navigate("/login");
  };

  return (
    <>
      <style>
        {`#basic-nav-dropdown::after {
          display: none;
        }`}
      </style>
      <Navbar expand="lg" className="bg-body-tertiary mb-3">
        <Container>
          <Navbar.Brand href="#" onClick={() => navigate("/")}>
            dpsh
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link onClick={() => navigate("/history")}>
                <i className="fa fa-history" /> History
              </Nav.Link>
              <Nav.Link onClick={() => navigate("/gallery")}>
                <i className="fa fa-picture-o" /> Gallery
              </Nav.Link>
            </Nav>
            <Nav>
              <NavDropdown
                title={<i className="fa fa-lg fa-ellipsis-v" />}
                id="basic-nav-dropdown"
                align="end"
              >
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
          <Route path="history" element={<HistoryPage />} />
          <Route path="gallery" element={<GalleryPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Routes>
      </Container>
    </Container>
  );
};

export default Dashboard;
