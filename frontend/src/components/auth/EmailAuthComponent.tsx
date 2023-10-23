import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useState } from "react";
import {
  Button,
  ButtonGroup,
  Col,
  FloatingLabel,
  Form,
  Row,
} from "react-bootstrap";

const EmailAuthComponent = () => {
  const [email, setEmail] = useState("");
  const [isDisabled, setIsDisabled] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsDisabled(true);
    const login_url = window.location.href;

    try {
      await api.post<boolean>("/users/login", {
        email,
        login_url,
      });
      setIsSuccess(true);
    } catch (error) {
      addAlert(humanReadableError(error), "error");
    } finally {
      setIsDisabled(false);
    }
  };

  return isSuccess ? (
    <Row>
      <Col>
        <Row>
          <Col>
            <h3>Success!</h3>
          </Col>
        </Row>
        <Row>
          <Col>Check your email for a login link.</Col>
        </Row>
      </Col>
    </Row>
  ) : (
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
        <Button
          variant="primary"
          type="submit"
          disabled={isDisabled || email.length === 0}
        >
          Sign In with Email
          <FontAwesomeIcon icon={faEnvelope} style={{ marginLeft: 15 }} />
        </Button>
      </ButtonGroup>
    </Form>
  );
};

export default EmailAuthComponent;
