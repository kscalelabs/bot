import { GoogleLogin } from "@react-oauth/google";
import { useState } from "react";
import { Button, Col, Container, Image, Modal, Row } from "react-bootstrap";
import { Navigate } from "react-router-dom";
import logo from "../../assets/logo.png";
import { useToken } from "../../hooks/auth";

interface GoogleAuthProps {
  setErrorMessage: (message: string | null) => void;
}

const GoogleAuth = ({ setErrorMessage }: GoogleAuthProps) => {
  const [credential, setCredential] = useState<string | null>(null);

  return (
    <Row className="mb-3">
      <Col>
        {credential === null ? (
          <GoogleLogin
            onSuccess={(credentialResponse) => {
              const credential = credentialResponse.credential;
              if (credential === undefined) {
                setErrorMessage("Failed to login using Google OAuth.");
                return;
              }
              setCredential(credential);
            }}
            onError={() => {
              setErrorMessage("Failed to login using Google OAuth.");
            }}
            useOneTap={false}
          />
        ) : (
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        )}
      </Col>
    </Row>
  );
};

interface GoogleAuthProps {
  setErrorMessage: (message: string | null) => void;
}

const DummyAuth = ({ setErrorMessage }: GoogleAuthProps) => {
  const { setToken } = useToken();

  return (
    <Row>
      <Col>
        <Button
          variant="primary"
          onClick={() => {
            setToken("dummy-token");
          }}
        >
          Dummy Login
        </Button>
      </Col>
    </Row>
  );
};

const Login = () => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { token } = useToken();
  if (token !== null) {
    // Gets the ?redirect=... query parameter from the URL.
    const urlParams = new URLSearchParams(window.location.search);
    const redirect = urlParams.get("redirect");
    if (redirect !== null) {
      return <Navigate to={redirect} />;
    }
    return <Navigate to="/" />;
  }

  return (
    <Container
      fluid
      className="h-100 d-flex justify-content-center align-items-center"
      style={{ minHeight: "100vh" }}
    >
      <Row className="text-center">
        <Col>
          <Row className="aspect-ratio aspect-ratio-1x1">
            <Col>
              <Image src={logo} alt="Logo" />
            </Col>
          </Row>

          <Row className="mb-3">
            <Col>
              <h3 style={{ fontFamily: "monospace" }}>
                don't panic
                <br />
                stay human
              </h3>
            </Col>
          </Row>

          <GoogleAuth setErrorMessage={setErrorMessage} />

          <DummyAuth setErrorMessage={setErrorMessage} />

          <Modal
            show={errorMessage !== null}
            onHide={() => {
              setErrorMessage(null);
            }}
          >
            <Modal.Header closeButton>
              <Modal.Title>Error</Modal.Title>
            </Modal.Header>
            <Modal.Body>{errorMessage}</Modal.Body>
          </Modal>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;
