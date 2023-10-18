import {
  faCancel,
  faClipboard,
  faClipboardCheck,
  faEdit,
  faPause,
  faPlay,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { QueryIdsResponse, SingleIdResponse } from "constants/types";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import React, {
  ForwardedRef,
  forwardRef,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Container,
  ContainerProps,
  Dropdown,
  Form,
  OverlayTrigger,
  Popover,
  Spinner,
  Tooltip,
} from "react-bootstrap";
import { Link } from "react-router-dom";

interface AudioPopoverProps {
  audioId: number;
  localResponse: SingleIdResponse | null;
  name: string;
  setName: (name: string) => void;
  showLink: boolean;
  setDeleted: (deleted: boolean) => void;
}

const AudioPopover = forwardRef(
  (
    props: AudioPopoverProps,
    ref: ForwardedRef<HTMLDivElement>,
  ): React.ReactElement => {
    const {
      audioId,
      localResponse,
      name,
      setName,
      showLink,
      setDeleted,
      ...popoverProps
    } = props;
    const { api } = useAuthentication();
    const { sourceId, setSourceId, referenceId, setReferenceId } =
      useClipboard();

    const [editing, setEditing] = useState<boolean | null>(false);
    const [acting, setActing] = useState(false);

    const handleEditButtonClick = async () => {
      if (editing) {
        try {
          if (name !== localResponse?.name) {
            setEditing(null);
            await api.post<boolean>("/audio/update", {
              id: audioId,
              name,
            });
            setName(name ?? "");
          }
        } catch (error) {
          setName(localResponse?.name ?? "");
        } finally {
          setEditing(false);
        }
      } else {
        setEditing(true);
      }
    };

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

    return (
      <Popover ref={ref} {...popoverProps}>
        {localResponse === null ? (
          <Spinner />
        ) : (
          <>
            <Popover.Header as="h3">
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
                <span>
                  <FontAwesomeIcon
                    icon={faEdit}
                    onClick={handleEditButtonClick}
                    className="me-2"
                  />
                  {name ?? localResponse.name}
                </span>
              )}
            </Popover.Header>
            <Popover.Body>
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
              <br />
              <Button
                variant="danger"
                onClick={handleDelete}
                className="mt-2"
                disabled={acting}
              >
                <FontAwesomeIcon icon={faCancel} className="me-2" />
                Permanently Delete
              </Button>
            </Popover.Body>
          </>
        )}
      </Popover>
    );
  },
);

interface AudioPlayButtonProps {
  name: string;
  audioId: number;
}

const AudioPlayButton = (props: AudioPlayButtonProps) => {
  const { name, audioId } = props;
  const { sessionToken, api } = useAuthentication();

  const [isPlaying, setIsPlaying] = useState(false);

  const url = `/audio/media/${audioId}.flac`;

  const audioRef = useRef<HTMLAudioElement | null>(null);

  const getUri = useCallback(() => {
    return api.getUri({
      url,
      method: "get",
      params: {
        access_token: sessionToken,
      },
    });
  }, [url, sessionToken, api]);

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

  const nameTruncated = name.length > 20 ? name.slice(0, 20) + "..." : name;

  return (
    <Button variant={isPlaying ? "warning" : "success"} onClick={toggleAudio}>
      {nameTruncated}
      {isPlaying ? (
        <FontAwesomeIcon
          icon={faPause}
          className="ms-2"
          style={{ width: 20 }}
        />
      ) : (
        <FontAwesomeIcon icon={faPlay} className="ms-2" style={{ width: 20 }} />
      )}
    </Button>
  );
};

interface AudioProps {
  audioId: number;
  title?: string;
  showDeleteButton?: boolean;
  showSelectionButtons?: boolean;
  response?: SingleIdResponse;
  showLink?: boolean;
}

type Props = AudioProps & ContainerProps;

const AudioPlayback: React.FC<Props> = ({
  audioId,
  title = null,
  showDeleteButton = true,
  showSelectionButtons = true,
  response = null,
  showLink = true,
  ...containerProps
}) => {
  const [deleted, setDeleted] = useState(false);
  const { sourceId, setSourceId, referenceId, setReferenceId } = useClipboard();
  const [localResponse, setLocalResponse] = useState<SingleIdResponse | null>(
    response,
  );
  const [name, setName] = useState<string>("");
  const { api } = useAuthentication();

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
      } catch (error) {}
    })();
  }, [audioId, api]);

  return (
    <Container {...containerProps}>
      <ButtonToolbar>
        {deleted ? (
          <ButtonGroup className="mt-2 me-2">
            <Button variant="danger" disabled>
              Deleted
            </Button>
          </ButtonGroup>
        ) : (
          <Dropdown as={ButtonGroup} className="mt-2 me-2">
            <AudioPlayButton name={name} audioId={audioId} />

            {showSelectionButtons && (
              <>
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
              </>
            )}

            <OverlayTrigger
              trigger="click"
              rootClose
              placement="bottom"
              overlay={
                <AudioPopover
                  audioId={audioId}
                  localResponse={localResponse}
                  name={name}
                  setName={setName}
                  showLink={showLink}
                  setDeleted={setDeleted}
                />
              }
            >
              <Dropdown.Toggle split id="dropdown-split-basic" />
            </OverlayTrigger>
          </Dropdown>
        )}
      </ButtonToolbar>
    </Container>
  );
};

export default AudioPlayback;
