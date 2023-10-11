import {
  faClipboard,
  faClipboardCheck,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useClipboard } from "hooks/clipboard";
import React from "react";
import { Button, ButtonGroup, Card, CardProps } from "react-bootstrap";

interface AudioProps {
  uuid: string;
  title?: string;
  showSelectionButtons?: boolean;
}

type Props = AudioProps & CardProps;

const AudioPlayback: React.FC<Props> = ({
  uuid,
  title = null,
  showSelectionButtons = true,
  ...cardProps
}) => {
  const { sourceUuid, setSourceUuid, referenceUuid, setReferenceUuid } =
    useClipboard();

  return (
    <Card {...cardProps}>
      {title !== null && <Card.Header>{title}</Card.Header>}
      <Card.Body>
        <Card.Title>Audio</Card.Title>
        <Card.Text>{uuid}</Card.Text>
        {showSelectionButtons && (
          <ButtonGroup>
            <Button
              onClick={() => setSourceUuid(uuid)}
              disabled={sourceUuid === uuid}
              variant={sourceUuid === uuid ? "success" : "primary"}
            >
              {sourceUuid === uuid ? (
                <span>
                  <FontAwesomeIcon icon={faClipboardCheck} /> Source
                </span>
              ) : (
                <span>
                  <FontAwesomeIcon icon={faClipboard} /> Source
                </span>
              )}
            </Button>
            <Button
              onClick={() => setReferenceUuid(uuid)}
              disabled={referenceUuid === uuid}
              variant={referenceUuid === uuid ? "success" : "primary"}
            >
              {sourceUuid === uuid ? (
                <span>
                  <FontAwesomeIcon icon={faClipboardCheck} /> Reference
                </span>
              ) : (
                <span>
                  <FontAwesomeIcon icon={faClipboard} /> Reference
                </span>
              )}
            </Button>
          </ButtonGroup>
        )}
      </Card.Body>
    </Card>
  );
};

export default AudioPlayback;
