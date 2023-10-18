import { humanReadableError } from "constants/backend";
import React, { createContext, useContext, useState } from "react";
import { useAlertQueue } from "./alerts";
import { useAuthentication } from "./auth";

const MAX_SUBMISSION_IDS = 10;

interface ClipboardContextProps {
  sourceId: number | null;
  referenceId: number | null;
  setSourceId: (id: number | null) => void;
  setReferenceId: (id: number | null) => void;
  submissionIds: number[];
  submitting: boolean;
  submit: () => void;
}

const ClipboardContext = createContext<ClipboardContextProps | undefined>(
  undefined,
);

interface ClipboardProviderProps {
  children: React.ReactNode;
}

interface RunResponse {
  id: number;
}

export const ClipboardProvider = (props: ClipboardProviderProps) => {
  const { children } = props;
  const [sourceId, setSourceId] = useState<number | null>(null);
  const [referenceId, setReferenceId] = useState<number | null>(null);
  const [submissionIds, setSubmissionIds] = useState<number[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  const submit = async () => {
    setSubmitting(true);
    try {
      const response = await api.post<RunResponse>("/infer/run", {
        source_id: sourceId,
        reference_id: referenceId,
      });
      setSubmissionIds((prev) => {
        if (prev.length === MAX_SUBMISSION_IDS) {
          return [...prev.slice(1), response.data.id];
        } else {
          return [...prev, response.data.id];
        }
      });
    } catch (error) {
      addAlert(humanReadableError(error), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ClipboardContext.Provider
      value={{
        sourceId,
        referenceId,
        setSourceId,
        setReferenceId,
        submissionIds,
        submitting,
        submit,
      }}
    >
      {children}
    </ClipboardContext.Provider>
  );
};

export const useClipboard = (): ClipboardContextProps => {
  const context = useContext(ClipboardContext);
  if (!context) {
    throw new Error("useClipboard must be used within a ClipboardProvider");
  }
  return context;
};
