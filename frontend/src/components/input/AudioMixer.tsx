import AudioSelection from "components/input/AudioSelection";
import SingleAudioPlayback from "components/playback/SingleAudioPlayback";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import { useState } from "react";
import { Alert, Button, Card, Col, Row, Spinner } from "react-bootstrap";

interface RunResponse {
  id: number;
}

const AudioMixer = () => {
  const [showSpinner, setShowSpinner] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [lastId, setLastId] = useState<number | null>(null);

  const { sourceId, referenceId } = useClipboard();
  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const handleSubmit = async () => {
    if (sourceId === null && referenceId === null) {
      addAlert("Please select a source and reference audio file.", "error");
      return;
    }
    if (sourceId === null) {
      addAlert("Please select a source audio file.", "error");
      return;
    }
    if (referenceId === null) {
      addAlert("Please select a reference audio file.", "error");
      return;
    }

    setShowSuccess(false);
    setShowSpinner(true);

    try {
      const response = await api.post<RunResponse>("/infer/run", {
        source_id: sourceId,
        reference_id: referenceId,
      });
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
      {lastId !== null && (
        <SingleAudioPlayback
          className="mt-3"
          audioId={lastId}
          title="Last Upload"
          showDeleteButton={false}
          showMixerButtons={false}
        />
      )}
    </Card.Body>
  );
};

export default AudioMixer;
