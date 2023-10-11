import React, { createContext, useContext, useState } from "react";

interface ClipboardContextProps {
  uuid: string | null;
  setUuid: (uuid: string | null) => void;
}

const ClipboardContext = createContext<ClipboardContextProps | undefined>(
  undefined
);

interface ClipboardProviderProps {
  children: React.ReactNode;
}

export const ClipboardProvider = (props: ClipboardProviderProps) => {
  const { children } = props;
  const [uuid, setUuid] = useState<string | null>(null);

  return (
    <ClipboardContext.Provider value={{ uuid, setUuid }}>
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
