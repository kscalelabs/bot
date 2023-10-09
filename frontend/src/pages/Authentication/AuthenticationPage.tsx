import logo from "assets/logo.png";
import { useToken } from "hooks/auth";
import LogInComponent from "pages/Authentication/components/LogInComponent";
import SignUpComponent from "pages/Authentication/components/SignUpComponent";
import { useCallback, useState } from "react";
import {
  Col,
  Container,
  Image,
  Modal,
  Row,
  ToggleButton,
  ToggleButtonGroup,
} from "react-bootstrap";
import { Navigate, useSearchParams } from "react-router-dom";

const AuthenticationPage = () => {
  const [message, setMessage] = useState<[string, string] | null>(null);
  const [searchParams] = useSearchParams();
  const [signUp, setSignUp] = useState(false);

  const { token } = useToken();

  const getRedirect = useCallback(() => {
    const redirect = searchParams.get("redirect");
    return redirect !== null ? redirect : "/";
  }, [searchParams]);

  if (token !== null) {
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

          <Row className="mb-3">
            <Col>
              <h3 style={{ fontFamily: "monospace" }}>
                don't panic
                <br />
                stay human
              </h3>
            </Col>
          </Row>

          <ToggleButtonGroup
            type="radio"
            defaultValue={1}
            name="options"
            className="mb-3"
          >
            <ToggleButton
              id="loginButton"
              value={1}
              onChange={() => setSignUp(false)}
            >
              Login
            </ToggleButton>
            <ToggleButton
              id="signUpButton"
              value={2}
              onChange={() => setSignUp(true)}
            >
              Sign Up
            </ToggleButton>
          </ToggleButtonGroup>

          {/* <GoogleAuthComponent setMessage={setMessage} /> */}

          {signUp ? (
            <SignUpComponent setMessage={setMessage} />
          ) : (
            <LogInComponent setMessage={setMessage} />
          )}

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
