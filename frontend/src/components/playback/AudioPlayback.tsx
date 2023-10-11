import { useClipboard } from "hooks/clipboard";
import React from "react";
import { Button, Card, CardProps } from "react-bootstrap";

interface AudioProps {
  uuid: string;
  title?: string;
}

type Props = AudioProps & CardProps;

const AudioPlayback: React.FC<Props> = ({
  uuid,
  title = null,
  ...cardProps
}) => {
  const { uuid: clipboardUuid, setUuid } = useClipboard();

  return (
    <Card {...cardProps}>
      {title !== null && <Card.Header>{title}</Card.Header>}
      <Card.Body>
        <Card.Title>Audio</Card.Title>
        <Card.Text>{uuid}</Card.Text>
        <Button
          onClick={() => setUuid(uuid)}
          disabled={clipboardUuid === uuid}
          variant={clipboardUuid === uuid ? "success" : "primary"}
        >
          Copy
        </Button>
      </Card.Body>
    </Card>
  );
};

export default AudioPlayback;
