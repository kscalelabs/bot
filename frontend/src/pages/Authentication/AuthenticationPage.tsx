import logo from "assets/logo.png";
import { useToken } from "hooks/auth";
import GoogleAuthComponent from "pages/Authentication/components/GoogleAuthComponent";
import LogInComponent from "pages/Authentication/components/LogInComponent";
import SignUpComponent from "pages/Authentication/components/SignUpComponent";
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
import { Navigate, useParams, useSearchParams } from "react-router-dom";

interface AuthenticationPageRouterParams {
  [urlToken: string]: string;
}

const AuthenticationPage = () => {
  const [message, setMessage] = useState<[string, string] | null>(null);
  const [searchParams] = useSearchParams();
  const [signUp, setSignUp] = useState(false);

  const { token, setToken } = useToken();
  const { urlToken } = useParams<AuthenticationPageRouterParams>();

  const tokenIsFound = () => {
    // Gets the ?redirect=... query parameter from the URL.
    const redirect = searchParams.get("redirect");
    if (redirect !== null) {
      return <Navigate to={redirect} />;
    }
    return <Navigate to="/" />;
  };

  if (token !== null) {
    return tokenIsFound();
  }

  if (urlToken !== undefined) {
    setToken([urlToken, "url"]);
    return tokenIsFound();
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

          <GoogleAuthComponent setMessage={setMessage} />

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
