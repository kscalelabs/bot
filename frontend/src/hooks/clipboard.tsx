import React, { createContext, useContext, useState } from "react";

interface ClipboardContextProps {
  sourceId: number | null;
  referenceId: number | null;
  setSourceId: (id: number | null) => void;
  setReferenceId: (id: number | null) => void;
}

const ClipboardContext = createContext<ClipboardContextProps | undefined>(
  undefined
);

interface ClipboardProviderProps {
  children: React.ReactNode;
}

export const ClipboardProvider = (props: ClipboardProviderProps) => {
  const { children } = props;
  const [sourceId, setSourceId] = useState<number | null>(null);
  const [referenceId, setReferenceId] = useState<number | null>(null);

  return (
    <ClipboardContext.Provider
      value={{ sourceId, referenceId, setSourceId, setReferenceId }}
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
