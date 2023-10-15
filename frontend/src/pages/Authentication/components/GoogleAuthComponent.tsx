import { faGoogle } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { GoogleOAuthProvider, useGoogleLogin } from "@react-oauth/google";
import { api, humanReadableError } from "constants/backend";
import { setToken } from "hooks/auth";
import { useEffect, useState } from "react";
import { Button } from "react-bootstrap";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";

interface Props {
  setMessage: (message: [string, string] | null) => void;
  redirectOnLogin: () => void;
}

interface UserLoginResponse {
  token: string;
  token_type: string;
}

const GoogleAuthComponentInner = ({ setMessage, redirectOnLogin }: Props) => {
  const [credential, setCredential] = useState<string | null>(null);
  const [disableButton, setDisableButton] = useState(false);

  useEffect(() => {
    (async () => {
      if (credential !== null) {
        try {
          const response = await api.post<UserLoginResponse>("/users/google", {
            token: credential,
          });
          setToken(response.data.token, "refresh");
          redirectOnLogin();
        } catch (error) {
          setMessage(["Error", humanReadableError(error)]);
        } finally {
          setCredential(null);
        }
      }
    })();
  });

  const login = useGoogleLogin({
    onSuccess: (tokenResponse) => {
      const credential = tokenResponse.access_token;
      if (credential === undefined) {
        setMessage(["Error", "Failed to login using Google OAuth."]);
      } else {
        setCredential(credential);
      }
    },
    onError: () => {
      setMessage(["Error", "Failed to login using Google OAuth."]);
      setDisableButton(false);
    },
  });

  return (
    <Button
      onClick={() => {
        setDisableButton(true);
        login();
      }}
      disabled={disableButton || credential !== null}
    >
      <FontAwesomeIcon icon={faGoogle} />
    </Button>
  );
};

const GoogleAuthComponent = (props: Props) => {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <GoogleAuthComponentInner {...props} />
    </GoogleOAuthProvider>
  );
};

export default GoogleAuthComponent;
