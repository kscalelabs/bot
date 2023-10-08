import { useState } from "react";
import { Button, FloatingLabel, Form } from "react-bootstrap";
import { api } from "../../../constants/backend";

interface Peops {
  setErrorMessage: (message: string | null) => void;
}

const SignUpComponent = ({ setErrorMessage }: Peops) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (confirmPassword !== password) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    try {
      const data = { username, password, login_url: window.location.href };
      const response = await api.post("/users/signup", data);
      console.log("Authentication successful", response.data);
    } catch (error) {
      setErrorMessage(`Authentication failed: ${error}`);
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
            setUsername(e.target.value);
          }}
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
        />
      </FloatingLabel>
      <FloatingLabel controlId="floatingPassword" label="Confirm Password">
        <Form.Control
          type="password"
          placeholder="Confirm Password"
          onChange={(e) => {
            setConfirmPassword(e.target.value);
          }}
        />
      </FloatingLabel>

      <Button variant="primary" type="submit" className="mt-3">
        Sign Up
      </Button>
    </Form>
  );
};

export default SignUpComponent;
