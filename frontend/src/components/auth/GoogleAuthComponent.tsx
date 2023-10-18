import { faGoogle } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { GoogleOAuthProvider, useGoogleLogin } from "@react-oauth/google";
import { humanReadableError } from "constants/backend";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import { Button } from "react-bootstrap";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";

interface Props {
  setMessage: (message: [string, string] | null) => void;
}

interface UserLoginResponse {
  token: string;
  token_type: string;
}

const GoogleAuthComponentInner = ({ setMessage }: Props) => {
  const [credential, setCredential] = useState<string | null>(null);
  const [disableButton, setDisableButton] = useState(false);

  const { setRefreshToken, api } = useAuthentication();

  useEffect(() => {
    (async () => {
      if (credential !== null) {
        try {
          const response = await api.post<UserLoginResponse>("/users/google", {
            token: credential,
          });
          setRefreshToken(response.data.token);
        } catch (error) {
          setMessage(["Error", humanReadableError(error)]);
        } finally {
          setCredential(null);
        }
      }
    })();
  }, [credential, setMessage, setRefreshToken, api]);

  const login = useGoogleLogin({
    onSuccess: (tokenResponse) => {
      const returnedCredential = tokenResponse.access_token;
      if (returnedCredential === undefined) {
        setMessage(["Error", "Failed to login using Google OAuth."]);
      } else {
        setCredential(returnedCredential);
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
      <span style={{ display: "flex", alignItems: "center" }}>
        Sign In with Google
        <FontAwesomeIcon icon={faGoogle} style={{ marginLeft: 15 }} />
      </span>
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
