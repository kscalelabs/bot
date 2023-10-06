import { Col, Container, Nav, Navbar, Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useToken } from "../../hooks/auth";

const LogoutLink = () => {
  const { setToken } = useToken();

  return (
    <Nav.Link
      as={Link}
      to="/login"
      onClick={() => {
        setToken(null);
      }}
    >
      Logout
    </Nav.Link>
  );
};

const Dashboard = () => {
  const { token } = useToken();

  return (
    <Container fluid>
      <Row>
        <Col xs={3} id="sidebar" className="bg-light">
          <Navbar bg="light" expand="lg" className="flex-column">
            <Navbar.Brand as={Link} to="/">
              dpsh
            </Navbar.Brand>
            <Nav className="flex-column">
              <Nav.Link as={Link} to="/profile">
                Profile
              </Nav.Link>
              <Nav.Link as={Link} to="/payment-info">
                Payment Info
              </Nav.Link>
              <Nav.Link as={Link} to="/upload">
                Upload
              </Nav.Link>
              {token && <LogoutLink />}
            </Nav>
          </Navbar>
        </Col>

        <Col xs={9} id="page-content-wrapper">
          Dashboard
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
