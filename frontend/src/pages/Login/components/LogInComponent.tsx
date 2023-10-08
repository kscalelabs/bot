import axios from "axios";
import { useState } from "react";
import { Button, FloatingLabel, Form } from "react-bootstrap";

interface Props {
  setErrorMessage: (message: string | null) => void;
}

const LogInComponent = ({ setErrorMessage }: Props) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Username:", username);
    console.log("Password:", password);
    try {
      const response = await axios.post("http://localhost:8000/users/login", {
        username,
        password,
      });
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
      <FloatingLabel controlId="floatingPassword" label="Password">
        <Form.Control
          type="password"
          placeholder="Password"
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
      </FloatingLabel>

      <Button variant="primary" type="submit" className="mt-3">
        Login
      </Button>
    </Form>
  );
};

export default LogInComponent;
