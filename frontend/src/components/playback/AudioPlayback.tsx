import { faCog } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { QueryIdsResponse, SingleIdResponse } from "constants/types";
import { useAuthentication } from "hooks/auth";
import { useClipboard } from "hooks/clipboard";
import React, { useEffect, useState } from "react";
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
import AudioPlayButton from "./AudioPlayButton";
import AudioPopover from "./AudioPopover";

interface AudioProps {
  audioId: number;
  title?: string;
  showDeleteButton?: boolean;
  showMixerButtons?: boolean;
  response?: SingleIdResponse;
  showLink?: boolean;
  tooltipPlacement?: Placement;
  settingsPlacement?: Placement;
}

type Props = AudioProps & ContainerProps;

const AudioPlayback: React.FC<Props> = ({
  audioId,
  title = null,
  showDeleteButton = true,
  showMixerButtons = true,
  response = null,
  showLink = true,
  tooltipPlacement = "top",
  settingsPlacement = "bottom",
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
          <Button variant="danger" disabled>
            Deleted
          </Button>
        ) : (
          <ButtonGroup className="mt-2 me-2">
            <AudioPlayButton
              name={name}
              audioId={audioId}
              tooltipPlacement={tooltipPlacement}
            />

            {showMixerButtons && (
              <AudioMixerButtons
                audioId={audioId}
                tooltipPlacement={tooltipPlacement}
              />
            )}

            <OverlayTrigger
              trigger="click"
              rootClose
              placement={settingsPlacement}
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
              <Button>
                <FontAwesomeIcon icon={faCog} />
              </Button>
            </OverlayTrigger>
          </ButtonGroup>
        )}
      </ButtonToolbar>
    </Container>
  );
};

export default AudioPlayback;
