import logo from "assets/logo_nb.webp";
import { getToken } from "hooks/auth";
import { useTheme } from "hooks/theme";
import GoogleAuthComponent from "pages/Authentication/components/GoogleAuthComponent";
import LogInComponent from "pages/Authentication/components/LogInComponent";
import { useCallback, useState } from "react";
import { Col, Container, Image, Modal, Row } from "react-bootstrap";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

const AuthenticationPage = () => {
  const [message, setMessage] = useState<[string, string] | null>(null);
  const [searchParams] = useSearchParams();
  const { colors } = useTheme();
  const { backgroundColor, color } = colors;
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
      style={{
        backgroundColor,
        color,
        minHeight: "100vh",
      }}
    >
      <Row>
        <Col>
          <Row>
            <Col>
              <Image
                src={logo}
                alt="Logo"
                style={{
                  maxHeight: "20vh",
                }}
              />
            </Col>
          </Row>

          <Row className="mb-5 text-center">
            <Col>
              <h3>
                don't panic
                <br />
                stay human
              </h3>
            </Col>
          </Row>

          <Row className="mb-3 text-center">
            <Col>
              <LogInComponent setMessage={setMessage} />
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
              <GoogleAuthComponent
                setMessage={setMessage}
                redirectOnLogin={redirectOnLogin}
              />
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
        </Col>
      </Row>
    </Container>
  );
};

export default AuthenticationPage;
