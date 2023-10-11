import logo from "assets/logo.png";
import { getToken } from "hooks/auth";
import LogInComponent from "pages/Authentication/components/LogInComponent";
import { useCallback, useState } from "react";
import { Col, Container, Image, Modal, Row } from "react-bootstrap";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import GoogleAuthComponent from "./components/GoogleAuthComponent";

const AuthenticationPage = () => {
  const [message, setMessage] = useState<[string, string] | null>(null);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const getRedirect = useCallback(() => {
    const redirect = searchParams.get("redirect");
    return redirect !== null ? redirect : "/";
  }, [searchParams]);

  const redirectOnLogin = useCallback(() => {
    navigate(getRedirect());
  }, [navigate, getRedirect]);

  if (getToken("refresh") !== null) {
    return <Navigate to={getRedirect()} />;
  }

  return (
    <Container
      fluid
      className="h-100 d-flex justify-content-center align-items-center"
      style={{ minHeight: "100vh" }}
    >
      <Row className="text-center" style={{ width: "20em" }}>
        <Col>
          <Row className="aspect-ratio aspect-ratio-1x1">
            <Col>
              <Image src={logo} alt="Logo" />
            </Col>
          </Row>

          <Row className="mb-5">
            <Col>
              <h3 style={{ fontFamily: "monospace" }}>
                don't panic
                <br />
                stay human
              </h3>
            </Col>
          </Row>

          <GoogleAuthComponent
            setMessage={setMessage}
            redirectOnLogin={redirectOnLogin}
          />

          <LogInComponent setMessage={setMessage} />

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
        </Col>
      </Row>
    </Container>
  );
};

export default AuthenticationPage;
