import React, { ChangeEvent } from "react";

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files![0];
    onFileUpload(file);
  };

  return <input type="file" onChange={handleFileChange} />;
};

export default FileUpload;
