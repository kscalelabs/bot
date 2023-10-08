import { useState } from "react";
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
import logo from "../../assets/logo.png";
import { useToken } from "../../hooks/auth";
import GoogleAuthComponent from "./components/GoogleAuthComponent";
import LogInComponent from "./components/LogInComponent";
import SignUpComponent from "./components/SignUpComponent";

const Login = () => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [searchParams] = useSearchParams();
  const [signUp, setSignUp] = useState(false);

  const { token } = useToken();
  if (token !== null) {
    // Gets the ?redirect=... query parameter from the URL.
    const redirect = searchParams.get("redirect");
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

          <GoogleAuthComponent setErrorMessage={setErrorMessage} />

          {signUp ? (
            <SignUpComponent setErrorMessage={setErrorMessage} />
          ) : (
            <LogInComponent setErrorMessage={setErrorMessage} />
          )}

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
