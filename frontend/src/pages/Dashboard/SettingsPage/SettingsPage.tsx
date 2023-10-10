import { useState } from "react";
import { Col, Container, Modal, Row } from "react-bootstrap";
import DeleteAccountComponent from "./components/DeleteAccountComponent";
import LogOutAllComponent from "./components/LogOutAllComponent";

const SettingsPage = () => {
  const [message, setMessage] = useState<[string, string] | null>(null);

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={4}>
          <Row className="mb-4">
            <h1>Settings</h1>
          </Row>
          <Row className="mb-4">
            <LogOutAllComponent setMessage={setMessage} />
          </Row>
          <Row>
            <DeleteAccountComponent />
          </Row>
        </Col>
      </Row>
      <Modal
        show={message !== null}
        onHide={() => {
          setMessage(null);
        }}
      >
        <Modal.Header closeButton>
          <Modal.Title>{message ? message[0] : ""}</Modal.Title>
        </Modal.Header>
        <Modal.Body>{message ? message[1] : ""}</Modal.Body>
        <Modal.Footer>
          Seeing issues? Send an email to <code>ben@dpsh.dev</code>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default SettingsPage;
