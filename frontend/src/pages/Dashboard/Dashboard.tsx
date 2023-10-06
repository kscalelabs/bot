import React from "react";
import { Col, Container, ListGroup, Nav, Row } from "react-bootstrap";
import { Link, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import DashboardContent from "./DashboardContent/DashboardContent";
import PaymentInfoEditor from "./PaymentInfoEditor/PaymentInfoEditor";
import ProfileEditor from "./ProfileEditor/ProfileEditor";

const Dashboard: React.FC = () => {
  return (
    <Router>
      <div className="container-fluid">
        <div className="row">
          <Nav className="col-md-2 d-none d-md-block bg-light sidebar">
            <div className="sidebar-sticky">
              <ListGroup variant="flush">
                <ListGroup.Item>
                  <Nav.Link as={Link} to="/" active>
                    Dashboard
                  </Nav.Link>
                </ListGroup.Item>
                <ListGroup.Item>
                  <Nav.Link as={Link} to="/profile">
                    Profile
                  </Nav.Link>
                </ListGroup.Item>
                <ListGroup.Item>
                  <Nav.Link as={Link} to="/payment">
                    Payment Info
                  </Nav.Link>
                </ListGroup.Item>
                {/* ... other navigation items */}
              </ListGroup>
            </div>
          </Nav>

          <main role="main" className="col-md-9 ml-sm-auto col-lg-10 px-md-4">
            <Container fluid>
              <Row>
                <Col>
                  <Routes>
                    <Route path="/" element={<DashboardContent />} />
                    <Route path="profile" element={<ProfileEditor />} />
                    <Route path="payment" element={<PaymentInfoEditor />} />
                    {/* ... other routes */}
                  </Routes>
                </Col>
              </Row>
            </Container>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default Dashboard;
