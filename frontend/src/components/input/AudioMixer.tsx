import AudioSelection from "components/input/AudioSelection";
import AudioPlayback from "components/playback/AudioPlayback";
import { api, humanReadableError } from "constants/backend";
import { useClipboard } from "hooks/clipboard";
import { useState } from "react";
import { Alert, Button, Card, Col, Row, Spinner } from "react-bootstrap";

interface RunResponse {
  uuid: string;
}

const AudioMixer = () => {
  const [preErrorMessage, setPreErrorMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showSpinner, setShowSpinner] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [lastUuid, setLastUuid] = useState<string | null>(null);

  const { sourceUuid, referenceUuid } = useClipboard();

  const handleSubmit = async () => {
    if (sourceUuid === null && referenceUuid === null) {
      setPreErrorMessage("Please select a source and reference audio file.");
      return;
    }
    if (sourceUuid === null) {
      setPreErrorMessage("Please select a source audio file.");
      return;
    }
    if (referenceUuid === null) {
      setPreErrorMessage("Please select a reference audio file.");
      return;
    }

    setPreErrorMessage(null);
    setErrorMessage(null);
    setShowSuccess(false);
    setShowSpinner(true);

    try {
      const response = await api.post<RunResponse>("/infer/run", {
        orig_uuid: sourceUuid,
        ref_uuid: referenceUuid,
      });
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
      <Card.Title>Mix</Card.Title>
      <Card.Text>Mix two audio samples together.</Card.Text>
      <Row>
        <Col xs={12} md={6} className="mt-3">
          <AudioSelection isSource={true} />
        </Col>
        <Col xs={12} md={6} className="mt-3">
          <AudioSelection isSource={false} />
        </Col>
      </Row>
      <div className="d-flex justify-content-center mt-3">
        {showSpinner ? (
          <Spinner />
        ) : (
          <Button onClick={handleSubmit}>Mix</Button>
        )}
      </div>
      {(errorMessage || preErrorMessage) && (
        <Alert
          variant="warning"
          className="mt-3"
          onClose={() => {
            setErrorMessage(null);
            setPreErrorMessage(null);
          }}
          dismissible
        >
          <Alert.Heading>Oh snap!</Alert.Heading>
          {preErrorMessage === null ? (
            <div>
              An error occurred while mixing your audio samples:
              <br />
              <code>{errorMessage}</code>
            </div>
          ) : (
            <div>{preErrorMessage}</div>
          )}
        </Alert>
      )}
      {showSuccess && (
        <Alert
          variant="success"
          className="mt-3"
          onClose={() => setShowSuccess(false)}
          dismissible
        >
          <Alert.Heading>Success!</Alert.Heading>
          <div>Your audio files have started mixing!</div>
        </Alert>
      )}
      {lastUuid !== null && (
        <AudioPlayback
          className="mt-3"
          uuid={lastUuid}
          title="Last Upload"
          showDeleteButton={false}
          showSelectionButtons={false}
        />
      )}
    </Card.Body>
  );
};

export default AudioMixer;
