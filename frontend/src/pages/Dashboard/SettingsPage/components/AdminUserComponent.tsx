import { faCheck, faRunning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useState } from "react";
import { Button, ButtonGroup, Col, Form } from "react-bootstrap";

interface AdminResopnse {
  banned: boolean;
  deleted: boolean;
}

const AdminUserComponent = () => {
  const [email, setEmail] = useState("");
  const [banned, setBanned] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const [buttonEnabled, setButtonEnabled] = useState(true);

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleCheckEmail = async () => {
    setButtonEnabled(false);
    try {
      const response = await api.post<AdminResopnse>("/admin/act/user", {
        email,
      });
      setBanned(response.data.banned);
      setDeleted(response.data.deleted);
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
      await api.post("/admin/act/user", {
        email,
        banned,
        deleted,
      });
      setBanned(false);
      setDeleted(false);
      setEmail("");
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
          type="email"
          placeholder="name@example.com"
          onChange={(e) => {
            setEmail(e.target.value);
          }}
          value={email}
        />
      </Form.Group>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Banned"
          onChange={(e) => {
            setBanned(e.target.checked);
          }}
          checked={banned}
          className="mb-3"
        />
      </Form.Group>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Deleted"
          onChange={(e) => {
            setDeleted(e.target.checked);
          }}
          checked={deleted}
          className="mb-3"
        />
      </Form.Group>
      <ButtonGroup>
        <Button
          variant="primary"
          disabled={!buttonEnabled}
          onClick={handleCheckEmail}
        >
          <FontAwesomeIcon icon={faCheck} /> Check Email
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

export default AdminUserComponent;
