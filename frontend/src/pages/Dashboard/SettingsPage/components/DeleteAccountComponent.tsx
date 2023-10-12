import { faCancel } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api, humanReadableError } from "constants/backend";
import { deleteTokens } from "hooks/auth";
import { useCallback, useState } from "react";
import { Button, Form, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const DeleteAccountComponent = () => {
  const [buttonEnabled, setButtonEnabled] = useState(false);
  const [useSpinner, setUseSpinner] = useState(false);
  const navigate = useNavigate();

  const handleDeleteAccount = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setUseSpinner(true);
      try {
        await api.delete<boolean>("/users/me");
        deleteTokens();
        navigate("/login");
      } catch (error) {
        console.log(humanReadableError(error));
        setButtonEnabled(false);
      } finally {
        setUseSpinner(false);
      }
    },
    [navigate]
  );

  return (
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

      {useSpinner ? (
        <Spinner />
      ) : (
        <Button
          variant="danger"
          id="button-addon2"
          disabled={!buttonEnabled}
          onClick={handleDeleteAccount}
        >
          <FontAwesomeIcon icon={faCancel} /> Delete Account
        </Button>
      )}
    </Form.Group>
  );
};

export default DeleteAccountComponent;
