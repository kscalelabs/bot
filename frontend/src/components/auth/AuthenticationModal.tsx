import GoogleAuthComponent from "components/auth/GoogleAuthComponent";
import { useState } from "react";
import { Alert, Col, Modal, Row } from "react-bootstrap";
import { Variant } from "react-bootstrap/esm/types";
import { useNavigate } from "react-router-dom";
import EmailAuthComponent from "./EmailAuthComponent";

const LogInModal = () => {
  const [message, setMessage] = useState<[string, string, Variant] | null>(
    null,
  );
  const navigate = useNavigate();

  const navigateToPreviousPage = () => {
    navigate(-1);
  };

  return (
    <Modal show={true} onHide={navigateToPreviousPage} centered>
      <Modal.Body>
        <Row>
          <Col>
            <Row className="mb-3 text-center">
              <Col>
                <h5>Sign in to see this page</h5>
              </Col>
            </Row>

            <Row className="mb-3 text-center">
              <Col>
                <EmailAuthComponent setMessage={setMessage} />
              </Col>
            </Row>

            <Row className="text-center">
              <Col>
                <hr />
              </Col>
              <Col xs="auto">
                <h6>or</h6>
              </Col>
              <Col>
                <hr />
              </Col>
            </Row>

            <Row className="mt-3 text-center">
              <Col>
                <GoogleAuthComponent setMessage={setMessage} />
              </Col>
            </Row>
          </Col>
        </Row>
        {message !== null && (
          <Alert
            variant={message[2]}
            onClose={() => setMessage(null)}
            dismissible
            className="mt-3"
          >
            <Alert.Heading>{message[0]}</Alert.Heading>
            {message[1]}
            <div className="mt-2">
              <small>
                <i>
                  Unexpected issues? Send an email to <code>ben@dpsh.dev</code>
                </i>
              </small>
            </div>
          </Alert>
        )}
      </Modal.Body>
    </Modal>
  );
};

export default LogInModal;
