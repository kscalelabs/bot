import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import { api, humanReadableError } from "constants/backend";
import { setToken } from "hooks/auth";
import { useEffect, useState } from "react";
import { Col, Row } from "react-bootstrap";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";

interface Props {
  setMessage: (message: [string, string] | null) => void;
  redirectOnLogin: () => void;
}

interface UserLoginResponse {
  token: string;
  token_type: string;
}

const GoogleAuthComponent = ({ setMessage, redirectOnLogin }: Props) => {
  const [credential, setCredential] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      if (credential !== null) {
        try {
          const response = await api.post<UserLoginResponse>("/users/google", {
            token: credential,
          });
          setToken([response.data.token, response.data.token_type]);
          redirectOnLogin();
        } catch (error) {
          setMessage(["Error", humanReadableError(error)]);
        } finally {
          setCredential(null);
        }
      }
    })();
  });

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
                } else {
                  setCredential(credential);
                }
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
