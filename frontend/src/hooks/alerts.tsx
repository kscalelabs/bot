import { createContext, useCallback, useContext, useState } from "react";
import { Toast, ToastContainer } from "react-bootstrap";

const MAX_ERRORS = 10;

type AlertType = "error" | "success";

const alertTypeToBg = (kind: AlertType) => {
  switch (kind) {
    case "error":
      return "danger";
    case "success":
      return "success";
  }
};

interface AlertQueueContextProps {
  addAlert: (alert: string, kind: AlertType) => void;
}

const AlertQueueContext = createContext<AlertQueueContextProps | undefined>(
  undefined,
);

interface AlertQueueProviderProps {
  children: React.ReactNode;
}

export const AlertQueueProvider = (props: AlertQueueProviderProps) => {
  const { children } = props;

  const [alerts, setAlerts] = useState<Map<string, [string, AlertType]>>(
    new Map(),
  );

  const generateAlertId = useCallback(() => {
    return Math.random().toString(36).substring(2);
  }, []);

  const addAlert = (alert: string, kind: AlertType) => {
    setAlerts((prev) => {
      const newAlerts = new Map(prev);
      const alertId = generateAlertId();
      newAlerts.set(alertId, [alert, kind]);

      // Ensure the map doesn't exceed MAX_ERRORS
      while (newAlerts.size > MAX_ERRORS) {
        const firstKey = Array.from(newAlerts.keys())[0];
        newAlerts.delete(firstKey);
      }

      return newAlerts;
    });
  };

  const removeAlert = (alertId: string) => {
    setAlerts((prev) => {
      const newAlerts = new Map(prev);
      newAlerts.delete(alertId);
      return newAlerts;
    });
  };

  console.log(alerts);

  return (
    <AlertQueueContext.Provider
      value={{
        addAlert,
      }}
    >
      {children}
      <ToastContainer className="p-3" position="bottom-center">
        {Array.from(alerts).map(([alertId, [alert, kind]]) => {
          return (
            <Toast
              key={alertId}
              bg={alertTypeToBg(kind)}
              autohide
              delay={3000}
              onClose={() => removeAlert(alertId)}
              animation={true}
            >
              <Toast.Header>
                <strong className="me-auto">Error</strong>
              </Toast.Header>
              <Toast.Body>{alert}</Toast.Body>
            </Toast>
          );
        })}
      </ToastContainer>
    </AlertQueueContext.Provider>
  );
};

export const useAlertQueue = () => {
  const context = useContext(AlertQueueContext);
  if (context === undefined) {
    throw new Error("useAlertQueue must be used within a ErrorQueueProvider");
  }
  return context;
};
