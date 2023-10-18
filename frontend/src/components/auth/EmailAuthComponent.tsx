import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useState } from "react";
import { Button, ButtonGroup, FloatingLabel, Form } from "react-bootstrap";

const EmailAuthComponent = () => {
  const [email, setEmail] = useState("");
  const [isDisabled, setIsDisabled] = useState(false);
  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsDisabled(true);
    const login_url = window.location.origin + "#/login";

    try {
      await api.post<boolean>("/users/login", {
        email,
        login_url,
      });
      addAlert("Check your email for a login link.", "success");
    } catch (error) {
      addAlert(humanReadableError(error), "error");
    } finally {
      setIsDisabled(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="mb-3">
      <FloatingLabel controlId="floatingInput" label="Email" className="mb-3">
        <Form.Control
          type="email"
          placeholder="name@example.com"
          onChange={(e) => {
            setEmail(e.target.value);
          }}
          value={email}
          disabled={isDisabled}
        />
      </FloatingLabel>
      <ButtonGroup>
        <Button variant="primary" type="submit" disabled={isDisabled}>
          Sign In with Email
          <FontAwesomeIcon icon={faEnvelope} style={{ marginLeft: 15 }} />
        </Button>
      </ButtonGroup>
    </Form>
  );
};

export default EmailAuthComponent;
