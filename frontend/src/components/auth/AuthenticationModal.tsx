import GoogleAuthComponent from "components/auth/GoogleAuthComponent";
import { Col, Modal, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import EmailAuthComponent from "./EmailAuthComponent";

const LogInModal = () => {
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
                <EmailAuthComponent />
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
                <GoogleAuthComponent />
              </Col>
            </Row>
          </Col>
        </Row>
      </Modal.Body>
      <Modal.Footer>
        <small>
          <i>Issues logging in? Send an email to </i>
          <code>ben@dpsh.dev</code>
        </small>
      </Modal.Footer>
    </Modal>
  );
};

export default LogInModal;
