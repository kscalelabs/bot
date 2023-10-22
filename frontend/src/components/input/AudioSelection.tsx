import { faClose } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import SingleAudioPlayback from "components/playback/SingleAudioPlayback";
import { useClipboard } from "hooks/clipboard";
import {
  Button,
  ButtonGroup,
  Card,
  CardProps,
  OverlayTrigger,
  Tooltip,
} from "react-bootstrap";

interface ComponentProps {
  isSource: boolean;
}

type Props = ComponentProps & CardProps;

const AudioSelection = (props: Props) => {
  const { isSource, ...cardProps } = props;

  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();

  const title = isSource ? "Source" : "Reference";
  const audioId = isSource ? sourceId : referenceId;
  const setId = isSource ? setSourceId : setReferenceId;

  return (
    <Card {...cardProps}>
      <Card.Header>{title}</Card.Header>
      <Card.Body>
        {audioId === null ? (
          <div>Make a selection</div>
        ) : (
          <>
            <SingleAudioPlayback
              audioId={audioId}
              showDeleteButton={false}
              showMixerButtons={false}
            />
            <ButtonGroup className="mt-3 me-2">
              <OverlayTrigger
                placement="top"
                overlay={<Tooltip id="tooltip-top">Clear</Tooltip>}
              >
                <Button onClick={() => setId(null)} variant="warning">
                  <FontAwesomeIcon icon={faClose} />
                </Button>
              </OverlayTrigger>
            </ButtonGroup>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default AudioSelection;
