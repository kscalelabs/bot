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

const AdminAudioComponent = () => {
  const [idString, setIdString] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [buttonEnabled, setButtonEnabled] = useState(true);

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleCheck = async () => {
    let id;
    try {
      id = parseInt(idString.trim());
    } catch (error) {
      addAlert("ID is not a number", "error");
      return;
    }

    setButtonEnabled(false);
    try {
      const response = await api.post<AdminResopnse>("/admin/act/content", {
        id,
      });
      setIsPublic(response.data.public);
      setButtonEnabled(true);
    } catch (error) {
      addAlert(humanReadableError(error), "error");
    } finally {
      setButtonEnabled(true);
    }
  };

  const handleAct = async () => {
    let id;
    try {
      id = parseInt(idString.trim());
    } catch (error) {
      addAlert("ID is not a number", "error");
      return;
    }

    setButtonEnabled(false);
    try {
      await api.post("/admin/act/content", {
        id,
        public: isPublic,
      });
      setIsPublic(false);
      setIdString("");
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
          placeholder="Audio ID"
          onChange={(e) => {
            setIdString(e.target.value);
          }}
          value={idString}
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
          onClick={handleCheck}
        >
          <FontAwesomeIcon icon={faCheck} /> Check ID
        </Button>
        <Button variant="danger" disabled={!buttonEnabled} onClick={handleAct}>
          <FontAwesomeIcon icon={faRunning} /> Take Action
        </Button>
      </ButtonGroup>
    </Col>
  );
};

export default AdminAudioComponent;
