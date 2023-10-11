import { faClose } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AudioPlayback from "components/playback/AudioPlayback";
import { Button, ButtonGroup, Card, CardProps } from "react-bootstrap";

interface ComponentProps {
  uuid: string | null;
  setUuid: (uuid: string | null) => void;
  title: string;
}

type Props = ComponentProps & CardProps;

const AudioSelection = (props: Props) => {
  const { uuid, setUuid, title, ...cardProps } = props;

  return (
    <Card {...cardProps}>
      <Card.Header>{title}</Card.Header>
      <Card.Body>
        {uuid === null ? (
          <div>Make a selection</div>
        ) : (
          <>
            <AudioPlayback uuid={uuid} showSelectionButtons={false} />
            <ButtonGroup className="mt-3 me-2">
              <Button onClick={() => setUuid(null)} variant="danger">
                <FontAwesomeIcon icon={faClose} /> Clear
              </Button>
            </ButtonGroup>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default AudioSelection;
