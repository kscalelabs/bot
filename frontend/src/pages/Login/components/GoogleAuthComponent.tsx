import { GoogleLogin } from "@react-oauth/google";
import { useState } from "react";
import { Col, Row } from "react-bootstrap";

interface Props {
  setMessage: (message: [string, string] | null) => void;
}

const GoogleAuthComponent = ({ setMessage }: Props) => {
  const [credential, setCredential] = useState<string | null>(null);

  return (
    <Row className="mb-3">
      <Col>
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
  );
};

export default GoogleAuthComponent;
