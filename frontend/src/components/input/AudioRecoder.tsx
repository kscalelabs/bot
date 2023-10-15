import AudioPlayback from "components/playback/AudioPlayback";
import { api, humanReadableError } from "constants/backend";
import { useEffect, useState } from "react";
import { Alert, Button, Card, Spinner } from "react-bootstrap";
import { useReactMediaRecorder } from "react-media-recorder";

const TIMEOUT_MS = 10000;

interface UploadAudioResponse {
  id: number;
}

const AudioRecorder = () => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<[string, Blob] | null>(null);
  const [showSpinner, setShowSpinner] = useState(false);
  const [lastId, setLastId] = useState<number | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [percentComplete, setPercentComplete] = useState<number | null>(null);
  const [intervalId, setIntervalId] = useState<number | null>(null);

  const { startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    onStop: (blobUrl, blob) => {
      setAudioBlob([blobUrl, blob]);
    },
  });

  useEffect(() => {
    (async () => {
      if (audioBlob === null) return;

      const blob = audioBlob[1];

      setErrorMessage(null);
      setShowSuccess(false);
      setShowSpinner(true);

      const formData = new FormData();
      formData.append("file", blob, "audio.webm");
      formData.append("source", "recorded");

      try {
        const response = await api.post<UploadAudioResponse>(
          "/audio/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        setShowSuccess(true);
        setLastId(response.data.id);
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
          <Button
            onClick={() => {
              const start = () => {
                setIsRecording(true);
                startRecording();

                // Show the progress bar.
                const interval = setInterval(() => {
                  setPercentComplete((prev) => {
                    if (prev === null) return 1;
                    const next = Math.min(prev + 1, 100);
                    if (next === 100) {
                      clearInterval(interval);
                      stop();
                    }
                    return next;
                  });
                }, TIMEOUT_MS / 100);
                setIntervalId(interval as unknown as number);
              };

              const stop = () => {
                setIsRecording(false);
                setPercentComplete(null);
                stopRecording();
                if (intervalId !== null) {
                  clearInterval(intervalId as unknown as number);
                }
              };

              if (isRecording) {
                stop();
              } else {
                start();
              }
              setErrorMessage(null);
            }}
            variant={isRecording ? "danger" : "primary"}
          >
            {isRecording
              ? percentComplete === null
                ? "Stop"
                : `Stop (${percentComplete}%)`
              : "Start"}
          </Button>
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
        <AudioPlayback className="mt-3" audioId={lastId} title="Last Upload" />
      )}
    </Card.Body>
  );
};

export default AudioRecorder;
