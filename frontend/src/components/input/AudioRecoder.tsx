import SingleAudioPlayback from "components/playback/SingleAudioPlayback";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import { Alert, Button, Card, Spinner } from "react-bootstrap";
import { useReactMediaRecorder } from "react-media-recorder";

const TIMEOUT_MS = 30000;
const MIN_MS = 5000;

interface UploadAudioResponse {
  id: number;
}

const AudioRecorder = () => {
  const [audioBlob, setAudioBlob] = useState<[string, Blob] | null>(null);
  const [showSpinner, setShowSpinner] = useState(false);
  const [lastId, setLastId] = useState<number | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [percentComplete, setPercentComplete] = useState<number | null>(null);
  const [intervalId, setIntervalId] = useState<number | null>(null);
  const [buttonDisabled, setButtonDisabled] = useState(false);

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const { startRecording, stopRecording } = useReactMediaRecorder({
    video: false,
    audio: true,
    onStop: (blobUrl, blob) => {
      setAudioBlob([blobUrl, blob]);
    },
    blobPropertyBag: {
      type: "audio/webm",
    },
    // mediaRecorderOptions: {
    //   mimeType: "audio/webm",
    // },
  });

  useEffect(() => {
    (async () => {
      if (audioBlob === null) return;

      const blob = audioBlob[1];

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
          },
        );
        setShowSuccess(true);
        setLastId(response.data.id);
      } catch (error) {
        addAlert(humanReadableError(error), "error");
      } finally {
        setShowSpinner(false);
        setAudioBlob(null);
      }
    })();
  }, [audioBlob, api, addAlert]);

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

                // Disable button if recording is less than 1 second.
                setButtonDisabled(true);
                setTimeout(() => {
                  setButtonDisabled(false);
                }, MIN_MS);

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
            }}
            variant={isRecording ? "danger" : "primary"}
            disabled={buttonDisabled}
          >
            {isRecording
              ? percentComplete === null
                ? "Stop"
                : `Stop (${percentComplete}%)`
              : "Start"}
          </Button>
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

export default AudioRecorder;
