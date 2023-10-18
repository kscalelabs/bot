import {
  faCancel,
  faClipboard,
  faClipboardCheck,
  faDownload,
  faPause,
  faPlay,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { QueryIdsResponse, SingleIdResponse } from "constants/types";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import React, { useCallback, useEffect, useRef, useState } from "react";
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
import { Link } from "react-router-dom";

interface AudioProps {
  audioId: number;
  title?: string;
  showDeleteButton?: boolean;
  showSelectionButtons?: boolean;
  showLink?: boolean;
  response?: SingleIdResponse;
}

type Props = AudioProps & CardProps;

const AudioPlayback: React.FC<Props> = ({
  audioId,
  title = null,
  showDeleteButton = true,
  showSelectionButtons = true,
  showLink = true,
  response = null,
  ...cardProps
}) => {
  const [acting, setActing] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();
  const [localResponse, setLocalResponse] = useState<SingleIdResponse | null>(
    response,
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [editing, setEditing] = useState<boolean | null>(false);
  const [name, setName] = useState<string>("");
  const [isPlaying, setIsPlaying] = useState(false);
  const { sessionToken, api } = useAuthentication();

  const audioRef = useRef<HTMLAudioElement | null>(null);

  const url = `/audio/media/${audioId}.flac`;

  const getUri = useCallback(() => {
    return api.getUri({
      url,
      method: "get",
      params: {
        access_token: sessionToken,
      },
    });
  }, [url, sessionToken, api]);

  const handleDelete = async () => {
    setActing(true);

    try {
      await api.delete<boolean>("/audio/delete", {
        params: {
          id: audioId,
        },
      });
      if (sourceId === audioId) {
        setSourceId(null);
      }
      if (referenceId === audioId) {
        setReferenceId(null);
      }
      setDeleted(true);
    } catch (error) {
      alert(humanReadableError(error));
      setActing(false);
    }
  };

  const handleEditButtonClick = async () => {
    if (editing) {
      try {
        setEditing(null);
        await api.post<boolean>("/audio/update", {
          id: audioId,
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
      try {
        const response = await api.post<QueryIdsResponse>("/audio/query/ids", {
          ids: [audioId],
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
    })();
  }, [audioId, api]);

  const toggleAudio = () => {
    if (audioRef.current === null) {
      audioRef.current = new Audio(getUri());

      const handleAudioEnd = () => {
        setIsPlaying(false);
      };

      audioRef.current.addEventListener("ended", handleAudioEnd);
    }
    if (audioRef.current !== null) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
    }
    setIsPlaying(!isPlaying);
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
                <br />
                <strong>Duration:</strong> {localResponse.duration.toFixed(1)}{" "}
                seconds
                {showLink && (
                  <>
                    <br />
                    <strong>
                      <Link to={`/audio/${audioId}`}>Link</Link>
                    </strong>
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
                  overlay={<Tooltip>Use as source</Tooltip>}
                >
                  <Button
                    onClick={() => setSourceId(audioId)}
                    disabled={sourceId === audioId}
                    variant={sourceId === audioId ? "success" : "primary"}
                  >
                    {sourceId === audioId ? (
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
                  overlay={<Tooltip>Use as reference</Tooltip>}
                >
                  <Button
                    onClick={() => setReferenceId(audioId)}
                    disabled={referenceId === audioId}
                    variant={referenceId === audioId ? "success" : "primary"}
                  >
                    {referenceId === audioId ? (
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
            {localResponse !== null && (
              <ButtonGroup className="mt-2 me-2">
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>{isPlaying ? "Pause" : "Play"}</Tooltip>}
                >
                  <Button onClick={toggleAudio}>
                    {isPlaying ? (
                      <FontAwesomeIcon icon={faPause} />
                    ) : (
                      <FontAwesomeIcon icon={faPlay} />
                    )}
                  </Button>
                </OverlayTrigger>
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>Download</Tooltip>}
                >
                  <Button as="a" variant="primary" href={getUri()} download>
                    <FontAwesomeIcon icon={faDownload} />
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            )}
            {showDeleteButton && (
              <ButtonGroup className="mt-2 me-2">
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>Permanently delete</Tooltip>}
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
                overlay={<Tooltip>Dismiss</Tooltip>}
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
