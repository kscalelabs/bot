import {
  faCancel,
  faClipboard,
  faClipboardCheck,
  faRefresh,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { api, humanReadableError } from "constants/backend";
import { QueryIdResponse, QueryIdsResponse } from "constants/types";
import { useClipboard } from "hooks/clipboard";
import React, { useEffect, useState } from "react";
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Card,
  CardProps,
  Form,
  OverlayTrigger,
  Spinner,
  Tooltip,
} from "react-bootstrap";

interface AudioProps {
  uuid: string;
  title?: string;
  showDeleteButton?: boolean;
  showSelectionButtons?: boolean;
  response?: QueryIdResponse;
}

type Props = AudioProps & CardProps;

const AudioPlayback: React.FC<Props> = ({
  uuid,
  title = null,
  showDeleteButton = true,
  showSelectionButtons = true,
  response = null,
  ...cardProps
}) => {
  const [acting, setActing] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const { sourceUuid, setSourceUuid, referenceUuid, setReferenceUuid } =
    useClipboard();
  const [localResponse, setLocalResponse] = useState<QueryIdResponse | null>(
    response
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [editing, setEditing] = useState<boolean | null>(false);
  const [name, setName] = useState<string>("");

  const handleDelete = async () => {
    setActing(true);

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
      setActing(false);
    }
  };

  const refreshInfo = async () => {
    try {
      const response = await api.post<QueryIdsResponse>("/audio/query/ids", {
        uuids: [uuid],
      });
      if (response.data.infos.length === 0) {
        setDeleted(true);
        return;
      }
      setLocalResponse(response.data.infos[0]);
      const name = response.data.infos[0].name;
      if (name !== null) {
        setName(name);
      }
    } catch (error) {
      setErrorMessage(humanReadableError(error));
    }
  };

  const handleRefresh = async () => {
    setLocalResponse(null);
    await refreshInfo();
  };

  const handleEditButtonClick = async () => {
    if (editing) {
      try {
        setEditing(null);
        await api.post<boolean>("/audio/update", {
          uuid,
          name,
        });
        setName(name ?? "");
      } catch (error) {
        setName(localResponse?.name ?? "");
        setErrorMessage(humanReadableError(error));
      } finally {
        setEditing(false);
      }
    } else {
      setEditing(true);
    }
  };

  useEffect(() => {
    (async () => {
      await refreshInfo();
    })();
  }, [uuid]);

  return (
    <Card {...cardProps}>
      {title !== null && <Card.Header>{title}</Card.Header>}
      {deleted ? (
        <Card.Body>
          <Card.Text>Deleted</Card.Text>
        </Card.Body>
      ) : (
        <Card.Body>
          {!localResponse ? (
            <Spinner />
          ) : (
            <>
              <Card.Title>
                {editing === null ? (
                  <Spinner />
                ) : (
                  <>
                    {editing ? (
                      <Form.Control
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        onBlur={handleEditButtonClick}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            handleEditButtonClick();
                          }
                        }}
                        autoFocus
                      />
                    ) : (
                      <span>{name ?? localResponse.name}</span>
                    )}
                    <Button
                      variant="link"
                      size="sm"
                      onClick={handleEditButtonClick}
                    >
                      {editing ? "Save" : "Edit"}
                    </Button>
                  </>
                )}
              </Card.Title>
              <Card.Text>
                <strong>Source:</strong> {localResponse.source}
                <br />
                <strong>Created:</strong>{" "}
                {new Date(localResponse.created).toLocaleString()}
                {localResponse.data && (
                  <>
                    <br />
                    <strong>Duration:</strong>{" "}
                    {localResponse.data.duration.toFixed(1)} seconds
                  </>
                )}
              </Card.Text>
            </>
          )}
          <ButtonToolbar>
            {showSelectionButtons && (
              <ButtonGroup className="mt-2 me-2">
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
            {localResponse !== null && !localResponse.available && (
              <ButtonGroup className="mt-2 me-2">
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip id="tooltip-top">Refresh</Tooltip>}
                >
                  <Button
                    onClick={handleRefresh}
                    variant="primary"
                    disabled={acting}
                  >
                    <FontAwesomeIcon icon={faRefresh} />
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            )}
            {showDeleteButton && (
              <ButtonGroup className="mt-2 me-2">
                <OverlayTrigger
                  placement="top"
                  overlay={
                    <Tooltip id="tooltip-top">Permanently delete</Tooltip>
                  }
                >
                  <Button
                    onClick={handleDelete}
                    variant="danger"
                    disabled={acting}
                  >
                    <FontAwesomeIcon icon={faCancel} />
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            )}
          </ButtonToolbar>
          {errorMessage !== null && (
            <Card.Text className="mt-2 text-danger">
              <OverlayTrigger
                placement="top"
                overlay={<Tooltip id="tooltip-top">Dismiss</Tooltip>}
              >
                <Button
                  onClick={() => setErrorMessage(null)}
                  variant="outline-danger"
                  size="sm"
                  className="me-2"
                >
                  <FontAwesomeIcon icon={faCancel} />
                </Button>
              </OverlayTrigger>
              {errorMessage}
            </Card.Text>
          )}
        </Card.Body>
      )}
    </Card>
  );
};

export default AudioPlayback;
