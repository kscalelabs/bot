import { faPause, faPlay } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuthentication } from "hooks/auth";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button, OverlayTrigger, Tooltip } from "react-bootstrap";
import { Placement } from "react-bootstrap/esm/types";

interface Props {
  name: string;
  audioId: number;
  tooltipPlacement?: Placement;
}

const AudioPlayButton = (props: Props) => {
  const { name, audioId, tooltipPlacement = "top" } = props;
  const { sessionToken, api } = useAuthentication();

  const [isPlaying, setIsPlaying] = useState(false);

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

  useEffect(() => {
    if (audioRef.current !== null) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsPlaying(false);
  }, [audioId]);

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

  const button = (
    <Button variant={isPlaying ? "warning" : "primary"} onClick={toggleAudio}>
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
        {name}
      </p>
    </Button>
  );

  return name.length > 15 ? (
    <OverlayTrigger
      placement={tooltipPlacement}
      overlay={<Tooltip>{name}</Tooltip>}
    >
      {button}
    </OverlayTrigger>
  ) : (
    button
  );
};

export default AudioPlayButton;
