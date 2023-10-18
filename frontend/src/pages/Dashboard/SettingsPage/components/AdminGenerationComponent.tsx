import { faCheck, faRunning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
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

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleCheckEmail = async () => {
    setButtonEnabled(false);
    try {
      const response = await api.post<AdminResopnse>("/admin/act/generation", {
        output_id: uuid,
      });
      setIsPublic(response.data.public);
      setButtonEnabled(true);
    } catch (error) {
      addAlert(humanReadableError(error), "error");
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
      addAlert(humanReadableError(error), "error");
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
            setUuid(e.target.value);
          }}
          value={uuid}
        />
      </Form.Group>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Public"
          onChange={(e) => {
            setIsPublic(e.target.checked);
          }}
          checked={isPublic}
          className="mb-3"
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
