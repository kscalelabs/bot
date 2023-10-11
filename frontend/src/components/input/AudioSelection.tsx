import AudioPlayback from "components/playback/AudioPlayback";
import { useClipboard } from "hooks/clipboard";
import { Button, ButtonGroup, Card, CardProps } from "react-bootstrap";

interface ComponentProps {
  uuid: string | null;
  title: string;
  setUuid?: (uuid: string | null) => void;
}

type Props = ComponentProps & CardProps;

const AudioSelection = (props: Props) => {
  const { uuid, title, setUuid = () => {}, ...cardProps } = props;

  const { uuid: clipboardUuid } = useClipboard();

  return (
    <Card {...cardProps}>
      <Card.Header>{title}</Card.Header>
      <Card.Body>
        {uuid === null ? (
          clipboardUuid === null ? (
            <div>Make a selection</div>
          ) : (
            <Button onClick={() => setUuid(clipboardUuid)}>Paste</Button>
          )
        ) : (
          <>
            <AudioPlayback uuid={uuid} />
            <ButtonGroup className="mt-3">
              <Button onClick={() => setUuid(null)} variant="danger">
                Clear
              </Button>
              {clipboardUuid !== null && (
                <Button
                  onClick={() => setUuid(clipboardUuid)}
                  disabled={clipboardUuid === uuid}
                >
                  Paste
                </Button>
              )}
            </ButtonGroup>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default AudioSelection;
