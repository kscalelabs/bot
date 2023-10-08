import { useState } from "react";
import { Button, Col, Container, Form, InputGroup } from "react-bootstrap";

const EmailInput = () => {
  const [email, setEmail] = useState<string | null>(null);

  return (
    <Col>
      <InputGroup>
        <Form.Control
          type="email"
          onChange={(e) => {
            setEmail(e.target.value);
          }}
          value={email || ""}
          placeholder="Email"
        />
        <Button variant="outline-secondary" id="button-addon2">
          <i className="fa fa-check"></i>
        </Button>
      </InputGroup>
    </Col>
  );
};

const PasswordInput = () => {
  const [password, setPassword] = useState("");
  const [confirmedPassword, setConfirmedPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const isValidPassword = (password: string) => {
    if (password.length === 0) {
      // Don't update password
      return true;
    }
    return (
      password.length >= 8 &&
      password.length <= 100 &&
      !password.match(/[^a-zA-Z0-9_]/)
    );
  };

  return (
    <Col className="mt-3">
      <InputGroup>
        <Form.Control
          type={showPassword ? "text" : "password"}
          isInvalid={!isValidPassword(password)}
          onChange={(e) => {
            setPassword(e.target.value);
          }}
          value={password || ""}
          placeholder="Password"
        />
        <Form.Control.Feedback type="invalid">
          Your password must be 8-100 characters long, contain letters, numbers,
          and underscores, and must not contain spaces, special characters, or
          emoji.
        </Form.Control.Feedback>
      </InputGroup>
      <InputGroup className="mt-3">
        <Form.Control
          type={showPassword ? "text" : "password"}
          isInvalid={password !== confirmedPassword}
          onChange={(e) => {
            setConfirmedPassword(e.target.value);
          }}
          value={confirmedPassword || ""}
          placeholder="Confirm Password"
        />
        <Button variant="outline-secondary" id="button-addon2">
          <i className="fa fa-check"></i>
        </Button>
        <Form.Control.Feedback type="invalid">
          Your passwords should match.
        </Form.Control.Feedback>
      </InputGroup>
      <Form.Group className="mt-3">
        <Form.Check
          type="switch"
          label={showPassword ? "Hide password" : "Show password"}
          onChange={(e) => {
            setShowPassword(e.target.checked);
          }}
        />
      </Form.Group>
    </Col>
  );
};

const NotificationSettings = () => {
  return (
    <Form.Group className="mt-3">
      <Form.Check
        type="switch"
        label="Receive periodic updates when new models come out"
      />
    </Form.Group>
  );
};

const SettingsPage = () => {
  return (
    <Container style={{ maxWidth: 800 }}>
      <h1>Settings</h1>
      <EmailInput />
      <PasswordInput />
      <NotificationSettings />
    </Container>
  );
};

export default SettingsPage;
