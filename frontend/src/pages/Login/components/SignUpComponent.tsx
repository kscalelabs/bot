import axios, { AxiosError } from "axios";
import { api } from "constants/backend";
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (confirmPassword !== password) {
      setMessage(["Error", "Passwords do not match."]);
      return;
    }

    setShowSpinner(true);

    try {
      const login_url = window.location.href.replace("signup", "login");
      const response = await api.post<SignUpResponse>("/users/signup", {
        email,
        password,
        login_url,
      });
      setToken([response.data.token, response.data.token_type]);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        console.log(axiosError);
        const request = axiosError.request,
          response = axiosError.response;
        if (response) {
          if (response.status === 400) {
            setMessage(["Error", "Invalid email or password."]);
          } else if (response.status === 500) {
            setMessage(["Error", "An internal server error occurred."]);
          } else {
            setMessage(["Error", "An unknown error occurred."]);
          }
        } else if (request) {
          setMessage(["Error", "An unknown error occurred."]);
        }
      } else {
        setMessage(["Error", "An unknown error occurred."]);
      }
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
      <FloatingLabel
        controlId="floatingPassword"
        label="Confirm Password"
        className="mb-3"
      >
        <Form.Control
          type="password"
          placeholder="Confirm Password"
          onChange={(e) => {
            setConfirmPassword(e.target.value);
          }}
        />
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
