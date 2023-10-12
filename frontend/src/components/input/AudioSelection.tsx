import { faClose } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AudioPlayback from "components/playback/AudioPlayback";
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

  const { sourceUuid, setSourceUuid, referenceUuid, setReferenceUuid } =
    useClipboard();

  const title = isSource ? "Source" : "Reference";
  const uuid = isSource ? sourceUuid : referenceUuid;
  const setUuid = isSource ? setSourceUuid : setReferenceUuid;

  return (
    <Card {...cardProps}>
      <Card.Header>{title}</Card.Header>
      <Card.Body>
        {uuid === null ? (
          <div>Make a selection</div>
        ) : (
          <>
            <AudioPlayback
              uuid={uuid}
              showDeleteButton={false}
              showSelectionButtons={false}
            />
            <ButtonGroup className="mt-3 me-2">
              <OverlayTrigger
                placement="top"
                overlay={<Tooltip id="tooltip-top">Clear</Tooltip>}
              >
                <Button onClick={() => setUuid(null)} variant="warning">
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
