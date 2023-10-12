import React, { createContext, useContext, useState } from "react";

interface ClipboardContextProps {
  sourceUuid: string | null;
  referenceUuid: string | null;
  setSourceUuid: (uuid: string | null) => void;
  setReferenceUuid: (uuid: string | null) => void;
}

const ClipboardContext = createContext<ClipboardContextProps | undefined>(
  undefined,
);

interface ClipboardProviderProps {
  children: React.ReactNode;
}

export const ClipboardProvider = (props: ClipboardProviderProps) => {
  const { children } = props;
  const [sourceUuid, setSourceUuid] = useState<string | null>(null);
  const [referenceUuid, setReferenceUuid] = useState<string | null>(null);

  return (
    <ClipboardContext.Provider
      value={{ sourceUuid, referenceUuid, setSourceUuid, setReferenceUuid }}
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
