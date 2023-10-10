import { faDeleteLeft } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api, humanReadableError } from "constants/backend";
import { deleteTokens } from "hooks/auth";
import { useState } from "react";
import { Button, Form, Spinner } from "react-bootstrap";

const DeleteAccountComponent = () => {
  const [buttonEnabled, setButtonEnabled] = useState(false);
  const [useSpinner, setUseSpinner] = useState(false);

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setUseSpinner(true);
    try {
      await api.delete<boolean>("/users/myself");
      deleteTokens();
    } catch (error) {
      console.log(humanReadableError(error));
      setButtonEnabled(false);
    } finally {
      setUseSpinner(false);
    }
  };

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
          <FontAwesomeIcon icon={faDeleteLeft} /> Delete Account
        </Button>
      )}
    </Form.Group>
  );
};

export default DeleteAccountComponent;
