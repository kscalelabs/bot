import AudioPlayback from "components/playback/AudioPlayback";
import { api, humanReadableError } from "constants/backend";
import { useEffect, useState } from "react";
import { Alert, Button, ButtonGroup, Card, Spinner } from "react-bootstrap";
import { ReactMediaRecorder } from "react-media-recorder";

interface UploadAudioResponse {
  uuid: string;
}

const AudioRecorder = () => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<[string, Blob] | null>(null);
  const [showSpinner, setShowSpinner] = useState(false);
  const [lastUuid, setLastUuid] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    (async () => {
      if (audioBlob === null) return;

      const blob = audioBlob[1];

      setErrorMessage(null);
      setShowSuccess(false);
      setShowSpinner(true);

      const formData = new FormData();
      formData.append("file", blob, "audio.webm");
      formData.append("source", "recording");

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
    })();
  }, [audioBlob]);

  return (
    <Card.Body>
      <Card.Title>Record</Card.Title>
      <Card.Text>
        Record your own audio using your computer microphone.
      </Card.Text>
      <div className="d-flex justify-content-center">
        {showSpinner ? (
          <Spinner />
        ) : (
          <ReactMediaRecorder
            audio
            render={({ status, startRecording, stopRecording }) => (
              <ButtonGroup>
                <Button
                  onClick={() => {
                    setIsRecording(true);
                    setErrorMessage(null);
                    startRecording();
                  }}
                  disabled={isRecording}
                >
                  Start Recording
                </Button>
                <Button
                  onClick={() => {
                    stopRecording();
                    setIsRecording(false);
                  }}
                  disabled={!isRecording}
                >
                  Stop Recording
                </Button>
              </ButtonGroup>
            )}
            onStop={(blobUrl, blob) => {
              setAudioBlob([blobUrl, blob]);
            }}
          />
        )}
      </div>
      {errorMessage && (
        <Alert
          variant="warning"
          className="mt-3"
          onClose={() => setErrorMessage(null)}
          dismissible
        >
          <Alert.Heading>Oh snap!</Alert.Heading>
          <div>
            An error occurred while uploading your recorded audio:
            <br />
            <code>{errorMessage}</code>
          </div>
        </Alert>
      )}
      {showSuccess && (
        <Alert
          variant="primary"
          className="mt-3"
          onClose={() => setShowSuccess(false)}
          dismissible
        >
          <Alert.Heading>Success!</Alert.Heading>
          <div>Your audio file was successfully uploaded!</div>
        </Alert>
      )}
      {lastUuid !== null && (
        <AudioPlayback uuid={lastUuid} title="Last Upload" />
      )}
    </Card.Body>
  );
};

export default AudioRecorder;
