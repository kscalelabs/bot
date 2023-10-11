import AudioPlayback from "components/playback/AudioPlayback";
import { api, humanReadableError } from "constants/backend";
import React, { useState } from "react";
import { Alert, Card, Form, Spinner } from "react-bootstrap";

interface UploadAudioResponse {
  uuid: string;
}

const AudioUploader = () => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showSpinner, setShowSpinner] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [lastUuid, setLastUuid] = useState<string | null>(null);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setErrorMessage(null);
    setShowSuccess(false);
    setShowSpinner(true);

    const files = event.target.files;
    if (files === null) return;
    const file = files[0];

    const formData = new FormData();
    formData.append("file", file);
    formData.append("source", "uploaded");

    try {
      const response = await api.post<UploadAudioResponse>(
        "/make/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setShowSuccess(true);
      setLastUuid(response.data.uuid);
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    } finally {
      setShowSpinner(false);
    }
  };

  return (
    <Card.Body>
      <Card.Title>Upload</Card.Title>
      <Form.Group>
        {showSpinner ? (
          <div className="mt-3 d-flex justify-content-center">
            <Spinner />
          </div>
        ) : (
          <>
            <Form.Label>Upload an audio recording.</Form.Label>
            <Form.Control
              type="file"
              onChange={handleFileChange}
              isInvalid={errorMessage !== null}
            />
            <Form.Control.Feedback type="invalid">
              {errorMessage}
            </Form.Control.Feedback>
          </>
        )}
      </Form.Group>
      {showSuccess && (
        <Alert
          variant="success"
          className="mt-3"
          onClose={() => setShowSuccess(false)}
          dismissible
        >
          <Alert.Heading>Success!</Alert.Heading>
          <div>Your audio file was successfully uploaded!</div>
        </Alert>
      )}
      {lastUuid !== null && (
        <AudioPlayback className="mt-3" uuid={lastUuid} title="Last Upload" />
      )}
    </Card.Body>
  );
};

export default AudioUploader;
