import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import { humanReadableError, useApi } from "constants/backend";
import { useToken } from "hooks/auth";
import { useEffect, useState } from "react";
import { Col, Row } from "react-bootstrap";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";

interface Props {
  setMessage: (message: [string, string] | null) => void;
}

interface UserLoginResponse {
  token: string;
  token_type: string;
}

const GoogleAuthComponent = ({ setMessage }: Props) => {
  const [credential, setCredential] = useState<string | null>(null);

  const api = useApi();
  const { setToken } = useToken();

  useEffect(() => {
    (async () => {
      if (credential === null) {
        return;
      }

      try {
        const response = await api.post<UserLoginResponse>("/users/google", {
          token: credential,
        });
        setToken([response.data.token, response.data.token_type]);
      } catch (error) {
        setMessage(["Error", humanReadableError(error)]);
      }
    })();
  }, [api, credential, setMessage, setToken]);

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Row className="mb-3">
        <Col className="d-flex justify-content-center">
          {credential === null ? (
            <GoogleLogin
              onSuccess={(credentialResponse) => {
                const credential = credentialResponse.credential;
                if (credential === undefined) {
                  setMessage(["Error", "Failed to login using Google OAuth."]);
                  return;
                }
                setCredential(credential);
              }}
              onError={() => {
                setMessage(["Error", "Failed to login using Google OAuth."]);
              }}
              useOneTap={false}
            />
          ) : (
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          )}
        </Col>
      </Row>
    </GoogleOAuthProvider>
  );
};

export default GoogleAuthComponent;