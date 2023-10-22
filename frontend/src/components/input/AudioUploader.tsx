import SingleAudioPlayback from "components/playback/SingleAudioPlayback";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import React, { useState } from "react";
import { Alert, Card, Form, Spinner } from "react-bootstrap";

interface UploadAudioResponse {
  id: number;
}

const AudioUploader = () => {
  const [showSpinner, setShowSpinner] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [lastId, setLastId] = useState<number | null>(null);

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
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
        "/audio/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );
      setShowSuccess(true);
      setLastId(response.data.id);
    } catch (error) {
      addAlert(humanReadableError(error), "error");
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
            <Form.Control type="file" onChange={handleFileChange} />
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
      {lastId !== null && (
        <SingleAudioPlayback
          className="mt-3"
          audioId={lastId}
          title="Last Upload"
        />
      )}
    </Card.Body>
  );
};

export default AudioUploader;
