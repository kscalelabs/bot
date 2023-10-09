import { humanReadableError, useApi } from "constants/backend";
import {
  EMAIL_MESSAGE,
  PASSWORD_MESSAGE,
  isValidEmail,
  isValidPassword,
} from "constants/inputs";
import { useToken } from "hooks/auth";
import { useState } from "react";
import { Button, FloatingLabel, Form, Spinner } from "react-bootstrap";

interface Peops {
  setMessage: (message: [string, string] | null) => void;
}

interface SignUpResponse {
  token: string;
  token_type: string;
}

const SignUpComponent = ({ setMessage }: Peops) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showSpinner, setShowSpinner] = useState(false);

  const { setToken } = useToken();
  const api = useApi();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (confirmPassword !== password) {
      setMessage(["Error", "Passwords do not match."]);
      return;
    }

    setShowSpinner(true);

    try {
      const login_url = window.location.origin;
      const response = await api.post<SignUpResponse>("/users/signup", {
        email,
        password,
        login_url,
      });
      setToken([response.data.token, response.data.token_type]);
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
          isInvalid={!isValidEmail(email)}
          placeholder="name@example.com"
          onChange={(e) => {
            setEmail(e.target.value);
          }}
        />
        <Form.Control.Feedback type="invalid">
          {EMAIL_MESSAGE}
        </Form.Control.Feedback>
      </FloatingLabel>

      <FloatingLabel
        controlId="floatingPassword"
        label="Password"
        className="mb-3"
      >
        <Form.Control
          type="password"
          isInvalid={!isValidPassword(password)}
          placeholder="Password"
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
        <Form.Control.Feedback type="invalid">
          {PASSWORD_MESSAGE}
        </Form.Control.Feedback>
      </FloatingLabel>
      <FloatingLabel
        controlId="floatingPassword"
        label="Confirm Password"
        className="mb-3"
      >
        <Form.Control
          type="password"
          isInvalid={password !== confirmPassword}
          placeholder="Confirm Password"
          onChange={(e) => {
            setConfirmPassword(e.target.value);
          }}
        />
        <Form.Control.Feedback type="invalid">
          Passwords should match.
        </Form.Control.Feedback>
      </FloatingLabel>

      {showSpinner ? (
        <Spinner />
      ) : (
        <Button variant="primary" type="submit">
          Sign Up
        </Button>
      )}
    </Form>
  );
};

export default SignUpComponent;
