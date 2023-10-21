import { faCancel, faEdit } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { SingleIdResponse } from "constants/types";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import React, { ForwardedRef, forwardRef, useCallback, useState } from "react";
import { Button, Form, Popover, PopoverProps, Spinner } from "react-bootstrap";
import { Link } from "react-router-dom";

interface ComponentProps {
  audioId: number;
  response: SingleIdResponse | null;
  name: string;
  setName: (name: string) => void;
  showLink: boolean;
  showDownload: boolean;
  showDeleteButton: boolean;
  setDeleted: (deleted: boolean) => void;
}

type Props = ComponentProps & PopoverProps;

const AudioPopover = forwardRef(
  (props: Props, ref: ForwardedRef<HTMLDivElement>): React.ReactElement => {
    const {
      audioId,
      response,
      name,
      setName,
      showLink,
      showDownload,
      showDeleteButton,
      setDeleted,
      ...popoverProps
    } = props;
    const [editing, setEditing] = useState<boolean | null>(false);
    const [acting, setActing] = useState(false);

    const { api, sessionToken } = useAuthentication();
    const { sourceId, setSourceId, referenceId, setReferenceId } =
      useClipboard();
    const { addAlert } = useAlertQueue();

    const getUri = useCallback(() => {
      const url = `/audio/media/${audioId}.flac`;

      return api.getUri({
        url,
        method: "get",
        params: {
          access_token: sessionToken,
        },
      });
    }, [audioId, sessionToken, api]);

    const handleEditButtonClick = async () => {
      if (editing) {
        try {
          if (name !== response?.name) {
            setEditing(null);
            await api.post<boolean>("/audio/update", {
              id: audioId,
              name,
            });
            setName(name ?? "");
          }
        } catch (error) {
          setName(response?.name ?? "");
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
        addAlert(humanReadableError(error), "error");
        setActing(false);
      }
    };

    return (
      <Popover ref={ref} {...popoverProps}>
        {response === null ? (
          <Spinner style={{ margin: 10 }} />
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
                    style={{ cursor: "pointer" }}
                  />
                  {name ?? response.name}
                </span>
              )}
            </Popover.Header>
            <Popover.Body>
              <strong>Source:</strong> {response.source}
              <br />
              <strong>Created:</strong>{" "}
              {new Date(response.created).toLocaleString()}
              <br />
              <strong>Duration:</strong> {response.duration.toFixed(1)} seconds
              {(showLink || showDownload) && (
                <>
                  <br />
                  <span>
                    {showLink && (
                      <strong>
                        <Link to={`/audio/${audioId}`}>Permalink</Link>
                      </strong>
                    )}
                    {showDownload && (
                      <>
                        {showLink && " | "}
                        <strong>
                          <a href={getUri()} download>
                            Download
                          </a>
                        </strong>
                      </>
                    )}
                  </span>
                </>
              )}
              {showDeleteButton && (
                <>
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
                </>
              )}
            </Popover.Body>
          </>
        )}
      </Popover>
    );
  },
);

export default AudioPopover;
