import { faPause, faPlay } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { SingleIdResponse } from "constants/types";
import { useAuthentication } from "hooks/auth";
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Container,
  ContainerProps,
  OverlayTrigger,
} from "react-bootstrap";
import { Placement } from "react-bootstrap/esm/types";
import AudioMixerButtons from "./AudioMixerButtons";
import AudioPopover from "./AudioPopover";

interface ComponentProps {
  audioId: number;
  response: SingleIdResponse | null;
  showDeleteButton?: boolean;
  showMixerButtons?: boolean;
  showLink?: boolean;
  showDownload?: boolean;
  tooltipPlacement?: Placement;
  settingsPlacement?: Placement;
}

type Props = ComponentProps & ContainerProps;

const AudioPlayback: React.FC<Props> = ({
  audioId,
  response,
  showDeleteButton = true,
  showMixerButtons = true,
  showLink = true,
  showDownload = true,
  tooltipPlacement = "top",
  settingsPlacement = "bottom-start",
  ...containerProps
}) => {
  const [deleted, setDeleted] = useState(false);
  const [name, setName] = useState<string | null>(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const { sessionToken, api } = useAuthentication();
  const audioRef = useRef<HTMLAudioElement | null>(null);

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

  useEffect(() => {
    if (audioRef.current !== null) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsPlaying(false);
  }, [audioId]);

  return (
    <Container {...containerProps}>
      <ButtonToolbar>
        {deleted ? (
          <Button className="mt-2 me-2" variant="danger" disabled>
            Deleted
          </Button>
        ) : (
          <ButtonGroup className="mt-2 me-2">
            <OverlayTrigger
              show={showOverlay}
              placement={settingsPlacement}
              overlay={
                <AudioPopover
                  audioId={audioId}
                  response={response}
                  name={name ?? response?.name ?? ""}
                  setName={setName}
                  showLink={showLink}
                  showDownload={showDownload}
                  showDeleteButton={showDeleteButton}
                  setDeleted={setDeleted}
                  onMouseOver={() => setShowOverlay(true)}
                  onMouseLeave={() => setShowOverlay(false)}
                />
              }
            >
              <Button
                variant={isPlaying ? "warning" : "primary"}
                onClick={toggleAudio}
                onMouseEnter={() => setShowOverlay(true)}
                onMouseLeave={() => setShowOverlay(false)}
                disabled={response === null}
              >
                <p
                  style={{
                    width: 150,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    margin: 0,
                    padding: 0,
                    textAlign: "left",
                  }}
                >
                  {isPlaying ? (
                    <FontAwesomeIcon
                      icon={faPause}
                      className="me-2"
                      style={{ width: 20 }}
                    />
                  ) : (
                    <FontAwesomeIcon
                      icon={faPlay}
                      className="me-2"
                      style={{ width: 20 }}
                    />
                  )}
                  {name ?? response?.name}
                </p>
              </Button>
            </OverlayTrigger>

            {showMixerButtons && (
              <AudioMixerButtons
                audioId={audioId}
                tooltipPlacement={tooltipPlacement}
                disabled={response === null}
              />
            )}
          </ButtonGroup>
        )}
      </ButtonToolbar>
    </Container>
  );
};

export default AudioPlayback;
