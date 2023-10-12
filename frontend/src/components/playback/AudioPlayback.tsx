import {
  faCancel,
  faClipboard,
  faClipboardCheck,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api, humanReadableError } from "constants/backend";
import { useClipboard } from "hooks/clipboard";
import React, { useState } from "react";
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Card,
  CardProps,
  OverlayTrigger,
  Tooltip,
} from "react-bootstrap";

interface AudioProps {
  uuid: string;
  title?: string;
  showDeleteButton?: boolean;
  showSelectionButtons?: boolean;
}

type Props = AudioProps & CardProps;

const AudioPlayback: React.FC<Props> = ({
  uuid,
  title = null,
  showDeleteButton = true,
  showSelectionButtons = true,
  ...cardProps
}) => {
  const [deleting, setDeleting] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const { sourceUuid, setSourceUuid, referenceUuid, setReferenceUuid } =
    useClipboard();

  const handleDelete = async () => {
    setDeleting(true);

    try {
      await api.delete<boolean>("/audio/delete", {
        params: {
          uuid,
        },
      });
      if (sourceUuid === uuid) {
        setSourceUuid(null);
      }
      if (referenceUuid === uuid) {
        setReferenceUuid(null);
      }
      setDeleted(true);
    } catch (error) {
      alert(humanReadableError(error));
      setDeleting(false);
    }
  };

  return (
    <Card {...cardProps}>
      {title !== null && <Card.Header>{title}</Card.Header>}
      {deleted ? (
        <Card.Body>
          <Card.Text>Deleted</Card.Text>
        </Card.Body>
      ) : (
        <Card.Body>
          <Card.Title>Audio</Card.Title>
          <Card.Text>{uuid}</Card.Text>
          <ButtonToolbar>
            {showSelectionButtons && (
              <ButtonGroup className="me-2">
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip id="tooltip-top">Use as source</Tooltip>}
                >
                  <Button
                    onClick={() => setSourceUuid(uuid)}
                    disabled={sourceUuid === uuid}
                    variant={sourceUuid === uuid ? "success" : "primary"}
                  >
                    {sourceUuid === uuid ? (
                      <span>
                        <FontAwesomeIcon icon={faClipboardCheck} /> S
                      </span>
                    ) : (
                      <span>
                        <FontAwesomeIcon icon={faClipboard} /> S
                      </span>
                    )}
                  </Button>
                </OverlayTrigger>
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip id="tooltip-top">Use as reference</Tooltip>}
                >
                  <Button
                    onClick={() => setReferenceUuid(uuid)}
                    disabled={referenceUuid === uuid}
                    variant={referenceUuid === uuid ? "success" : "primary"}
                  >
                    {referenceUuid === uuid ? (
                      <span>
                        <FontAwesomeIcon icon={faClipboardCheck} /> R
                      </span>
                    ) : (
                      <span>
                        <FontAwesomeIcon icon={faClipboard} /> R
                      </span>
                    )}
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            )}
            {showDeleteButton && (
              <OverlayTrigger
                placement="top"
                overlay={<Tooltip id="tooltip-top">Permanently delete</Tooltip>}
              >
                <Button
                  onClick={handleDelete}
                  variant="danger"
                  disabled={deleting}
                >
                  <FontAwesomeIcon icon={faCancel} />
                </Button>
              </OverlayTrigger>
            )}
          </ButtonToolbar>
        </Card.Body>
      )}
    </Card>
  );
};

export default AudioPlayback;
