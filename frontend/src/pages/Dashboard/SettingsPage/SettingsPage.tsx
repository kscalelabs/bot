import { Col, Container, Row } from "react-bootstrap";
import DeleteAccountComponent from "./components/DeleteAccountComponent";
import UpdateEmailComponent from "./components/UpdateEmailComponent";
import UpdatePasswordComponent from "./components/UpdatePasswordComponent";

const SettingsPage = () => {
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={4}>
          <Row md={4} className="mb-4">
            <h1>Settings</h1>
          </Row>
          <UpdateEmailComponent />
          <UpdatePasswordComponent />
          <DeleteAccountComponent />
        </Col>
      </Row>
    </Container>
  );
};

export default SettingsPage;
