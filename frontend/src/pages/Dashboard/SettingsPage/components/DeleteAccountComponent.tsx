import { humanReadableError, useApi } from "constants/backend";
import { useToken } from "hooks/auth";
import { useState } from "react";
import { Button, Form } from "react-bootstrap";

const DeleteAccountComponent = () => {
  const [buttonEnabled, setButtonEnabled] = useState(false);

  const api = useApi();
  const { setToken } = useToken();

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.delete<boolean>("/users/myself");
      setToken(null);
    } catch (error) {
      console.log(humanReadableError(error));
      setButtonEnabled(false);
    }
  };

  return (
    <Form.Group className="mt-3">
      <Form.Check
        type="switch"
        label="Confirm account deletion"
        onChange={(e) => {
          setButtonEnabled(e.target.checked);
        }}
        checked={buttonEnabled}
      />

      <Button
        variant="danger"
        id="button-addon2"
        className="mt-3"
        disabled={!buttonEnabled}
        onClick={handleDeleteAccount}
      >
        <i className="fa fa-cross"></i> Delete Account
      </Button>
    </Form.Group>
  );
};

export default DeleteAccountComponent;
