import { faR, faS } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import { useState } from "react";
import {
  Button,
  ButtonProps,
  OverlayTrigger,
  Spinner,
  Tooltip,
} from "react-bootstrap";
import { Placement } from "react-bootstrap/esm/types";
import SingleAudioPlayback from "./SingleAudioPlayback";

interface ComponentProps {
  audioId: number;
  tooltipPlacement?: Placement;
}

type Props = ComponentProps & ButtonProps;

interface RunResponse {
  output_id: number;
  generation_id: number;
}

const SourceButton = (props: Props) => {
  const { audioId, tooltipPlacement = "top", ...buttonProps } = props;
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
      const response = await api.post<RunResponse>("/infer/run", {
        source_id: audioId,
        reference_id: referenceId,
      });
      addAlert(
        <SingleAudioPlayback
          audioId={response.data.output_id}
          settingsPlacement="top-start"
        />,
        "success",
      );
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
          variant={isSource ? "secondary" : "primary"}
          {...buttonProps}
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
        <Button
          onClick={runInference}
          variant={isReference ? "primary" : "success"}
          {...buttonProps}
          disabled={isDisabled}
        >
          <span>
            {isDisabled ? (
              <Spinner animation="border" style={{ width: 15, height: 15 }} />
            ) : (
              <FontAwesomeIcon icon={faS} style={{ width: 15, height: 15 }} />
            )}
          </span>
        </Button>
      </OverlayTrigger>
    );
  }
};

const ReferenceButton = (props: Props) => {
  const { audioId, tooltipPlacement = "top", ...buttonProps } = props;
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
      const response = await api.post<RunResponse>("/infer/run", {
        source_id: sourceId,
        reference_id: audioId,
      });
      addAlert(
        <SingleAudioPlayback
          audioId={response.data.output_id}
          settingsPlacement="top-start"
        />,
        "success",
      );
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
          variant={isReference ? "secondary" : "primary"}
          {...buttonProps}
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
        <Button
          onClick={runInference}
          variant={isSource ? "primary" : "success"}
          {...buttonProps}
          disabled={isDisabled}
        >
          <span>
            {isDisabled ? (
              <Spinner animation="border" style={{ width: 15, height: 15 }} />
            ) : (
              <FontAwesomeIcon icon={faR} style={{ width: 15, height: 15 }} />
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
