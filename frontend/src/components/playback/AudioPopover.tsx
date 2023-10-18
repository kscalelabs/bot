import { faCancel, faEdit } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { humanReadableError } from "constants/backend";
import { SingleIdResponse } from "constants/types";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import React, { ForwardedRef, forwardRef, useState } from "react";
import { Button, Form, Popover, Spinner } from "react-bootstrap";
import { Link } from "react-router-dom";

interface Props {
  audioId: number;
  localResponse: SingleIdResponse | null;
  name: string;
  setName: (name: string) => void;
  showLink: boolean;
  showDeleteButton: boolean;
  setDeleted: (deleted: boolean) => void;
}

const AudioPopover = forwardRef(
  (props: Props, ref: ForwardedRef<HTMLDivElement>): React.ReactElement => {
    const {
      audioId,
      localResponse,
      name,
      setName,
      showLink,
      showDeleteButton,
      setDeleted,
      ...popoverProps
    } = props;
    const [editing, setEditing] = useState<boolean | null>(false);
    const [acting, setActing] = useState(false);

    const { api } = useAuthentication();
    const { sourceId, setSourceId, referenceId, setReferenceId } =
      useClipboard();
    const { addAlert } = useAlertQueue();

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
        addAlert(humanReadableError(error), "error");
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
                    style={{ cursor: "pointer" }}
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
