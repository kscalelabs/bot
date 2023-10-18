import { faCog } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { Button, Container, Nav, Navbar } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import SidebarComponent from "./SidebarComponent";

const NavigationBar = () => {
  const navigate = useNavigate();
  const [showSidebar, setShowSidebar] = useState(false);

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

      {/* Toggle sidebar */}
      <Button
        variant="link"
        onClick={() => setShowSidebar(!showSidebar)}
        style={{
          position: "absolute",
          top: 5,
          right: 5,
          zIndex: 1000,
        }}
      >
        <FontAwesomeIcon icon={faCog} />
      </Button>

      <SidebarComponent show={showSidebar} setShow={setShowSidebar} />
    </>
  );
};

export default NavigationBar;
