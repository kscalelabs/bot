import { Col, Container, Row } from "react-bootstrap";
import DeleteAccountComponent from "./components/DeleteAccountComponent";

const SettingsPage = () => {
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={4}>
          <Row md={4} className="mb-4">
            <h1>Settings</h1>
          </Row>
          <DeleteAccountComponent />
        </Col>
      </Row>
    </Container>
  );
};

export default SettingsPage;
