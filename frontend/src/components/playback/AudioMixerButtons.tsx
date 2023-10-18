import { faR, faS, faWandSparkles } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import { useState } from "react";
import { Button, OverlayTrigger, Spinner, Tooltip } from "react-bootstrap";
import { Placement } from "react-bootstrap/esm/types";

interface Props {
  audioId: number;
  tooltipPlacement?: Placement;
}

interface RunResponse {
  id: number;
}

const SourceButton = (props: Props) => {
  const { audioId, tooltipPlacement = "top" } = props;
  const [isDisabled, setIsDisabled] = useState(false);

  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();
  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();
  const isSource = audioId === sourceId,
    isReference = audioId === referenceId;

  const runInference = async () => {
    if (isReference) {
      setReferenceId(null);
      setSourceId(audioId);
      return;
    }
    setIsDisabled(true);
    try {
      await api.post<RunResponse>("/infer/run", {
        source_id: audioId,
        reference_id: referenceId,
      });
      addAlert("Queued mixer job", "success");
    } catch (error) {
      addAlert("Failed to add job", "error");
    } finally {
      setIsDisabled(false);
    }
  };

  if (referenceId === null) {
    return (
      <OverlayTrigger
        placement={tooltipPlacement}
        overlay={
          <Tooltip>{isSource ? "Remove as source" : "Use as source"}</Tooltip>
        }
      >
        <Button
          onClick={() => {
            if (isSource) {
              setSourceId(null);
            } else {
              setSourceId(audioId);
            }
          }}
          variant={isSource ? "success" : "primary"}
        >
          <span>
            <FontAwesomeIcon icon={faS} style={{ width: 15, height: 15 }} />
          </span>
        </Button>
      </OverlayTrigger>
    );
  } else {
    return (
      <OverlayTrigger
        placement={tooltipPlacement}
        overlay={
          <Tooltip>
            {isReference ? "Use as source" : "Mix with reference"}
          </Tooltip>
        }
      >
        <Button onClick={runInference} disabled={isDisabled} variant="primary">
          <span>
            {isDisabled ? (
              <Spinner animation="border" style={{ width: 15, height: 15 }} />
            ) : (
              <FontAwesomeIcon
                icon={isReference ? faS : faWandSparkles}
                style={{ width: 15, height: 15 }}
              />
            )}
          </span>
        </Button>
      </OverlayTrigger>
    );
  }
};

const ReferenceButton = (props: Props) => {
  const { audioId, tooltipPlacement = "top" } = props;
  const [isDisabled, setIsDisabled] = useState(false);

  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();
  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();
  const isSource = audioId === sourceId,
    isReference = audioId === referenceId;

  const runInference = async () => {
    if (isSource) {
      setSourceId(null);
      setReferenceId(audioId);
      return;
    }

    setIsDisabled(true);
    try {
      await api.post<RunResponse>("/infer/run", {
        source_id: sourceId,
        reference_id: audioId,
      });
      addAlert("Queued mixing", "success");
    } catch (error) {
      addAlert("Failed to start mixing", "error");
    } finally {
      setIsDisabled(false);
    }
  };

  if (sourceId === null) {
    return (
      <OverlayTrigger
        placement={tooltipPlacement}
        overlay={
          <Tooltip>
            {isReference ? "Remove as reference" : "Use as reference"}
          </Tooltip>
        }
      >
        <Button
          onClick={() => {
            if (isReference) {
              setReferenceId(null);
            } else {
              setReferenceId(audioId);
            }
          }}
          variant={isReference ? "success" : "primary"}
        >
          <span>
            <FontAwesomeIcon icon={faR} style={{ width: 15, height: 15 }} />
          </span>
        </Button>
      </OverlayTrigger>
    );
  } else {
    return (
      <OverlayTrigger
        placement={tooltipPlacement}
        overlay={
          <Tooltip>{isSource ? "Use as reference" : "Mix with source"}</Tooltip>
        }
      >
        <Button onClick={runInference} disabled={isDisabled} variant="primary">
          <span>
            {isDisabled ? (
              <Spinner animation="border" style={{ width: 15, height: 15 }} />
            ) : (
              <FontAwesomeIcon
                icon={isSource ? faR : faWandSparkles}
                style={{ width: 15, height: 15 }}
              />
            )}
          </span>
        </Button>
      </OverlayTrigger>
    );
  }
};

const AudioMixerButtons = (props: Props) => {
  return (
    <>
      <SourceButton {...props} />
      <ReferenceButton {...props} />
    </>
  );
};

export default AudioMixerButtons;
