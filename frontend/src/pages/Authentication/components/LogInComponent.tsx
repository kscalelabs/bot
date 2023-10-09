import { humanReadableError, useApi } from "constants/backend";
import { useToken } from "hooks/auth";
import { useState } from "react";
import {
  Button,
  ButtonGroup,
  FloatingLabel,
  Form,
  Spinner,
} from "react-bootstrap";

interface Props {
  setMessage: (message: [string, string] | null) => void;
}

interface LogInResponse {
  token: string;
  token_type: string;
}

const LogInComponent = ({ setMessage }: Props) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showSpinner, setShowSpinner] = useState(false);

  const { setToken } = useToken();
  const api = useApi();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setShowSpinner(true);

    try {
      const response = await api.post<LogInResponse>("/users/login", {
        email,
        password,
      });
      setToken([response.data.token, response.data.token_type]);
    } catch (error) {
      setMessage(["Error", humanReadableError(error)]);
    } finally {
      setShowSpinner(false);
    }
  };

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();

    setShowSpinner(true);

    // Construct the login URL from the current URL, using hash routing.
    const login_url = window.location.origin + "#/login";

    try {
      await api.post<boolean>("/users/password/forgot", {
        email,
        login_url,
      });
      setMessage([
        "Sent!",
        "If a corresponding email exists, then a temporary login link has been sent.",
      ]);
    } catch (error) {
      setMessage(["Error", humanReadableError(error)]);
    } finally {
      setShowSpinner(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="mb-3">
      <FloatingLabel
        controlId="floatingInput"
        label="Email address"
        className="mb-3"
      >
        <Form.Control
          type="email"
          placeholder="name@example.com"
          onChange={(e) => {
            setEmail(e.target.value);
          }}
          value={email}
        />
      </FloatingLabel>
      <FloatingLabel
        controlId="floatingPassword"
        label="Password"
        className="mb-3"
      >
        <Form.Control
          type="password"
          placeholder="Password"
          onChange={(e) => {
            setPassword(e.target.value);
          }}
          value={password}
        />
      </FloatingLabel>

      {showSpinner ? (
        <Spinner />
      ) : (
        <ButtonGroup>
          <Button variant="primary" type="submit">
            Login
          </Button>
          {email.length > 0 && password.length === 0 && (
            <Button
              variant="secondary"
              type="button"
              onClick={handlePasswordReset}
            >
              Log In with OTP
            </Button>
          )}
        </ButtonGroup>
      )}
    </Form>
  );
};

export default LogInComponent;
