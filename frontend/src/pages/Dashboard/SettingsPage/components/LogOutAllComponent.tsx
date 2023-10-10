import { faSignOutAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api, humanReadableError } from "constants/backend";
import { deleteToken } from "hooks/auth";
import { useState } from "react";
import { Button, Form, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

interface Props {
  setMessage: (message: [string, string] | null) => void;
}

const LogOutAllComponent = ({ setMessage }: Props) => {
  const [useSpinner, setUseSpinner] = useState(false);
  const navigate = useNavigate();

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setUseSpinner(true);
    try {
      await api.delete<boolean>("/users/logout/all");
      deleteToken();
      navigate("/login");
    } catch (error) {
      setMessage(["Error", humanReadableError(error)]);
    } finally {
      setUseSpinner(false);
    }
  };

  return (
    <Form.Group>
      {useSpinner ? (
        <Spinner />
      ) : (
        <Button
          variant="warning"
          id="button-addon2"
          onClick={handleDeleteAccount}
        >
          <FontAwesomeIcon icon={faSignOutAlt} /> Log Out Everywhere
        </Button>
      )}
    </Form.Group>
  );
};

export default LogOutAllComponent;
