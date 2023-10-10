import { api, humanReadableError } from "constants/backend";
import { useCallback, useRef, useState } from "react";
import { Button } from "react-bootstrap";

interface UploadAudioResponse {
  uuid: string;
}

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [audioData, setAudioData] = useState<Blob | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const mediaRecorder = useRef<MediaRecorder | null>(null);

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    mediaRecorder.current.start();
    setRecording(true);
    mediaRecorder.current.addEventListener("dataavailable", (e) => {
      setAudioData(e.data);
    });
  }, []);

  const stopRecording = useCallback(() => {
    mediaRecorder.current?.stop();
    mediaRecorder.current?.stream.getTracks().forEach((track) => track.stop());
    mediaRecorder.current = null;
    setRecording(false);
  }, []);

  const uploadAudio = async () => {
    if (!audioData) return;
    const formData = new FormData();
    formData.append("audio", audioData, "audio.wav");
    try {
      const response = await api.post<UploadAudioResponse>(
        "/make/upload",
        formData
      );
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    }
  };

  return (
    <div>
      {recording ? (
        <Button variant="danger" onClick={stopRecording}>
          Stop Recording
        </Button>
      ) : (
        <Button variant="primary" onClick={startRecording}>
          Start Recording
        </Button>
      )}
      {audioData && (
        <Button variant="success" onClick={uploadAudio}>
          Upload
        </Button>
      )}
      {errorMessage && <p>{errorMessage}</p>}
    </div>
  );
};

export default AudioRecorder;
