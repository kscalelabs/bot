import { faCancel, faCheck } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api, humanReadableError } from "constants/backend";
import { useState } from "react";
import { Button, ButtonGroup, Col, Form, Row } from "react-bootstrap";

interface AdminResopnse {
  banned: boolean;
  deleted: boolean;
}

const AdminComponent = () => {
  const [email, setEmail] = useState("");
  const [banned, setBanned] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const [buttonEnabled, setButtonEnabled] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleCheckEmail = async () => {
    setButtonEnabled(false);
    try {
      const response = await api.post<AdminResopnse>("/users/admin/act/user", {
        email,
      });
      setBanned(response.data.banned);
      setDeleted(response.data.deleted);
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
      await api.post("/users/admin/act/user", {
        email,
        banned,
        deleted,
      });
      setBanned(false);
      setDeleted(false);
      setEmail("");
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    } finally {
      setButtonEnabled(true);
    }
  };

  return (
    <Col>
      <Row className="mb-3">
        <Col className="text-center">
          <h2>Admin</h2>
        </Col>
      </Row>

      <Form.Group className="mb-3">
        <Form.Control
          type="email"
          placeholder="name@example.com"
          onChange={(e) => {
            setErrorMessage(null);
            setEmail(e.target.value);
          }}
          value={email}
          isInvalid={errorMessage !== null}
        />
        <Form.Control.Feedback type="invalid">
          {errorMessage}
        </Form.Control.Feedback>
      </Form.Group>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Banned"
          onChange={(e) => {
            setErrorMessage(null);
            setBanned(e.target.checked);
          }}
          checked={banned}
          className="mb-3"
          isInvalid={errorMessage !== null}
        />
      </Form.Group>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Deleted"
          onChange={(e) => {
            setErrorMessage(null);
            setDeleted(e.target.checked);
          }}
          checked={deleted}
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
          <FontAwesomeIcon icon={faCheck} /> Check Email
        </Button>
        <Button
          variant="danger"
          disabled={!buttonEnabled}
          onClick={handleAdminAction}
        >
          <FontAwesomeIcon icon={faCancel} /> Take Action
        </Button>
      </ButtonGroup>
    </Col>
  );
};

export default AdminComponent;
