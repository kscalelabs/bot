import { useState } from "react";
import { Button, FloatingLabel, Form } from "react-bootstrap";
import { api } from "../../../constants/backend";
import { useToken } from "../../../hooks/auth";

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

  const { setToken } = useToken();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post<LogInResponse>("/users/login", {
        email,
        password,
      });
      setToken([response.data.token, response.data.token_type]);
    } catch (error) {
      setMessage(["Error", `Authentication failed: ${error}`]);
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
