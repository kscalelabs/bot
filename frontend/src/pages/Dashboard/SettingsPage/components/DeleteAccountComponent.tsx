import { faCancel } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useCallback, useState } from "react";
import { Button, Col, Form, Row, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const DeleteAccountComponent = () => {
  const [buttonEnabled, setButtonEnabled] = useState(false);
  const [useSpinner, setUseSpinner] = useState(false);

  const navigate = useNavigate();
  const { logout, api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleDeleteAccount = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setUseSpinner(true);
      try {
        await api.delete<boolean>("/users/me");
        logout();
        navigate("/login");
      } catch (error) {
        setButtonEnabled(false);
        addAlert(humanReadableError(error), "error");
      } finally {
        setUseSpinner(false);
      }
    },
    [navigate, logout, api, addAlert],
  );

  return (
    <Col>
      <Row className="mb-3">
        <Col className="text-center">
          <h2>Delete Account</h2>
        </Col>
      </Row>
      <Form.Group>
        <Form.Check
          type="switch"
          label="Confirm account deletion"
          onChange={(e) => {
            setButtonEnabled(e.target.checked);
          }}
          checked={buttonEnabled}
          className="mb-3"
        />
      </Form.Group>
      {useSpinner ? (
        <Spinner />
      ) : (
        <Button
          variant="danger"
          disabled={!buttonEnabled}
          onClick={handleDeleteAccount}
        >
          <FontAwesomeIcon icon={faCancel} /> Delete Account
        </Button>
      )}
    </Col>
  );
};

export default DeleteAccountComponent;
