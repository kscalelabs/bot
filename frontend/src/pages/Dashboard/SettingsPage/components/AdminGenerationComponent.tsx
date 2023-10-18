import { faCheck, faRunning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { useAuthentication } from "hooks/auth";
import { useState } from "react";
import { Button, ButtonGroup, Col, Form } from "react-bootstrap";

interface AdminResopnse {
  public: boolean;
}

const AdminGenerationComponent = () => {
  const [uuid, setUuid] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [buttonEnabled, setButtonEnabled] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { api } = useAuthentication();

  const handleCheckEmail = async () => {
    setButtonEnabled(false);
    try {
      const response = await api.post<AdminResopnse>("/admin/act/generation", {
        output_id: uuid,
      });
      setIsPublic(response.data.public);
      setButtonEnabled(true);
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    } finally {
      setButtonEnabled(true);
    }
  };

  const handleAdminAction = async () => {
    setButtonEnabled(false);
    try {
      await api.post("/admin/act/generation", {
        output_id: uuid,
        public: isPublic,
      });
      setIsPublic(false);
      setUuid("");
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    } finally {
      setButtonEnabled(true);
    }
  };

  return (
    <Col>
      <Form.Group className="mb-3">
        <Form.Control
          type="text"
          placeholder="Generation ID"
          onChange={(e) => {
            setErrorMessage(null);
            setUuid(e.target.value);
          }}
          value={uuid}
          isInvalid={errorMessage !== null}
        />
        <Form.Control.Feedback type="invalid">
          {errorMessage}
        </Form.Control.Feedback>
      </Form.Group>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Public"
          onChange={(e) => {
            setErrorMessage(null);
            setIsPublic(e.target.checked);
          }}
          checked={isPublic}
          className="mb-3"
          isInvalid={errorMessage !== null}
        />
      </Form.Group>
      <ButtonGroup>
        <Button
          variant="primary"
          disabled={!buttonEnabled}
          onClick={handleCheckEmail}
        >
          <FontAwesomeIcon icon={faCheck} /> Check ID
        </Button>
        <Button
          variant="danger"
          disabled={!buttonEnabled}
          onClick={handleAdminAction}
        >
          <FontAwesomeIcon icon={faRunning} /> Take Action
        </Button>
      </ButtonGroup>
    </Col>
  );
};

export default AdminGenerationComponent;
