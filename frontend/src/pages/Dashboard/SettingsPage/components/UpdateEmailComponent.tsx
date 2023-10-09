import { humanReadableError, useApi } from "constants/backend";
import { EMAIL_MESSAGE, isValidEmail } from "constants/inputs";
import { useEffect, useState } from "react";
import {
  Button,
  ButtonGroup,
  FloatingLabel,
  Form,
  Spinner,
} from "react-bootstrap";

interface UserInfoResponse {
  email: string;
  email_verified: string;
}

const UpdateEmailComponent = () => {
  const [email, setEmail] = useState<string | null>(null);
  const [showSpinner, setShowSpinner] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isDisabled, setIsDisabled] = useState(true);

  const api = useApi();

  useEffect(() => {
    (async () => {
      if (email === null) {
        try {
          const response = await api.get<UserInfoResponse>("/users/me");
          setEmail(response.data.email);
        } catch (error) {
          setMessage(humanReadableError(error));
        }
      }
    })();
  }, [api, email]);

  const handleUpdateEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setShowSpinner(true);
    try {
      const login_url = window.location.href;
      await api.put<boolean>("/users/email/update", {
        new_email: email,
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
    (email !== null && email.length > 0 && !isValidEmail(email));

  return (
    <Form onSubmit={handleUpdateEmail} className="mb-3">
      <FloatingLabel label="Email address" className="mb-3">
        <Form.Control
          type="email"
          isInvalid={isInvalid}
          onChange={(e) => {
            setEmail(e.target.value);
            setShowSpinner(false);
            setMessage(null);
            setIsDisabled(false);
          }}
          value={email || ""}
          placeholder="Email"
          disabled={email === null}
        />
        <Form.Control.Feedback type="invalid">
          {message || EMAIL_MESSAGE}
        </Form.Control.Feedback>
      </FloatingLabel>
      <Form.Label>
        {showSpinner ? (
          <Spinner />
        ) : (
          <ButtonGroup>
            <Button
              variant="primary"
              type="submit"
              disabled={
                isDisabled ||
                isInvalid ||
                (email !== null && email.length === 0)
              }
            >
              Update Email
            </Button>
          </ButtonGroup>
        )}
      </Form.Label>
    </Form>
  );
};

export default UpdateEmailComponent;
