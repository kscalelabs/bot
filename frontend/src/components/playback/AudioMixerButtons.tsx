import {
  faClipboard,
  faClipboardCheck,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useClipboard } from "hooks/clipboard";
import { Button, OverlayTrigger, Tooltip } from "react-bootstrap";
import { Placement } from "react-bootstrap/esm/types";

interface Props {
  audioId: number;
  tooltipPlacement?: Placement;
}

const SourceButton = (props: Props) => {
  const { audioId, tooltipPlacement = "top" } = props;
  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();

  return (
    <OverlayTrigger
      placement={tooltipPlacement}
      overlay={<Tooltip>Use as source</Tooltip>}
    >
      <Button
        onClick={() => setSourceId(audioId)}
        disabled={sourceId === audioId}
        variant={sourceId === audioId ? "success" : "primary"}
      >
        {sourceId === audioId ? (
          <span>
            <FontAwesomeIcon icon={faClipboardCheck} />
          </span>
        ) : (
          <span>
            <FontAwesomeIcon icon={faClipboard} />
          </span>
        )}
      </Button>
    </OverlayTrigger>
  );
};

const ReferenceButton = (props: Props) => {
  const { audioId, tooltipPlacement = "top" } = props;
  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();

  return (
    <>
      <OverlayTrigger
        placement={tooltipPlacement}
        overlay={<Tooltip>Use as reference</Tooltip>}
      >
        <Button
          onClick={() => setReferenceId(audioId)}
          disabled={referenceId === audioId}
          variant={referenceId === audioId ? "success" : "primary"}
        >
          {referenceId === audioId ? (
            <span>
              <FontAwesomeIcon icon={faClipboardCheck} />
            </span>
          ) : (
            <span>
              <FontAwesomeIcon icon={faClipboard} />
            </span>
          )}
        </Button>
      </OverlayTrigger>
    </>
  );
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
