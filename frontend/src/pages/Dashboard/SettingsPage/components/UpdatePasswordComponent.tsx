import { humanReadableError, useApi } from "constants/backend";
import { PASSWORD_MESSAGE, isValidPassword } from "constants/inputs";
import { useState } from "react";
import {
  Button,
  ButtonGroup,
  FloatingLabel,
  Form,
  Spinner,
} from "react-bootstrap";

const UpdatePasswordComponent = () => {
  const [password, setPassword] = useState("");
  const [showSpinner, setShowSpinner] = useState(false);
  const [confirmedPassword, setConfirmedPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isDisabled, setIsDisabled] = useState(true);

  const api = useApi();

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmedPassword) {
      setMessage("Passwords do not match");
      return;
    }

    setShowSpinner(true);
    try {
      const login_url = window.location.href;
      await api.put<boolean>("/users/password/update", {
        new_password: password,
        login_url,
      });
      setIsDisabled(true);
    } catch (error) {
      setMessage(humanReadableError(error));
    } finally {
      setShowSpinner(false);
    }
  };

  const isInvalid =
    message !== null ||
    (password.length > 0 && !isValidPassword(password)) ||
    password !== confirmedPassword;

  return (
    <Form onSubmit={handleUpdatePassword} className="mb-3">
      <FloatingLabel label="Password" className="mb-3">
        <Form.Control
          type={showPassword ? "text" : "password"}
          isInvalid={isInvalid}
          onChange={(e) => {
            setPassword(e.target.value);
            setShowSpinner(false);
            setMessage(null);
            setIsDisabled(false);
          }}
          value={password}
          placeholder="Password"
        />
      </FloatingLabel>
      <FloatingLabel label="Confirm Password" className="mb-3">
        <Form.Control
          type={showPassword ? "text" : "password"}
          isInvalid={isInvalid}
          onChange={(e) => {
            setConfirmedPassword(e.target.value);
            setShowSpinner(false);
            setMessage(null);
            setIsDisabled(false);
          }}
          value={confirmedPassword}
          placeholder="Confirm Password"
        />
        <Form.Control.Feedback type="invalid">
          {message !== null
            ? message
            : !isValidPassword(password)
            ? PASSWORD_MESSAGE
            : "Passwords must match"}
        </Form.Control.Feedback>
      </FloatingLabel>

      <Form.Check
        className="mb-3"
        type="switch"
        label="Show password"
        onChange={(e) => setShowPassword(e.target.checked)}
      />
      <Form.Label>
        {showSpinner ? (
          <Spinner />
        ) : (
          <ButtonGroup>
            <Button
              variant="primary"
              type="submit"
              disabled={isDisabled || isInvalid || password.length === 0}
            >
              Update Password
            </Button>
          </ButtonGroup>
        )}
      </Form.Label>
    </Form>
  );
};

export default UpdatePasswordComponent;
