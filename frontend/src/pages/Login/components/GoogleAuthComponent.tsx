import { GoogleLogin } from "@react-oauth/google";
import { useState } from "react";
import { Col, Row } from "react-bootstrap";

interface Props {
  setErrorMessage: (message: string | null) => void;
}

const GoogleAuthComponent = ({ setErrorMessage }: Props) => {
  const [credential, setCredential] = useState<string | null>(null);

  return (
    <Row className="mb-3">
      <Col>
        {credential === null ? (
          <GoogleLogin
            onSuccess={(credentialResponse) => {
              const credential = credentialResponse.credential;
              if (credential === undefined) {
                setErrorMessage("Failed to login using Google OAuth.");
                return;
              }
              setCredential(credential);
            }}
            onError={() => {
              setErrorMessage("Failed to login using Google OAuth.");
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
  );
};

export default GoogleAuthComponent;
