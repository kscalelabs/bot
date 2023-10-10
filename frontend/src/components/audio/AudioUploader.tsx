import { api, humanReadableError } from "constants/backend";
import React, { useState } from "react";
import { Form } from "react-bootstrap";

interface UploadAudioResponse {
  uuid: string;
}

const AudioUploader = () => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setErrorMessage(null);

    const files = event.target.files;
    if (files === null) return;
    const file = files[0];

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post<UploadAudioResponse>("/make/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    }
  };

  return (
    <Form.Group>
      <Form.Label>Upload an audio recording</Form.Label>
      <Form.Control
        type="file"
        onChange={handleFileChange}
        isInvalid={errorMessage !== null}
      />
      <Form.Control.Feedback type="invalid">
        {errorMessage}
      </Form.Control.Feedback>
    </Form.Group>
  );
};

export default AudioUploader;
