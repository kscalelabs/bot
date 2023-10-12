import { api, humanReadableError } from "constants/backend";
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

const LogInComponent = ({ setMessage }: Props) => {
  const [email, setEmail] = useState("");
  const [showSpinner, setShowSpinner] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setShowSpinner(true);
    const login_url = window.location.origin + "#/login";

    try {
      await api.post<boolean>("/users/login", {
        email,
        login_url,
      });
      setMessage(["Success!", "Check your email for a login link."]);
    } catch (error) {
      setMessage(["Error", humanReadableError(error)]);
    } finally {
      setShowSpinner(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="mb-3">
      {showSpinner ? (
        <Spinner />
      ) : (
        <>
          <FloatingLabel
            controlId="floatingInput"
            label="Email"
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
          <ButtonGroup>
            <Button variant="primary" type="submit">
              Login
            </Button>
          </ButtonGroup>
        </>
      )}
    </Form>
  );
};

export default LogInComponent;
