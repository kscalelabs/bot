import { QueryIdsResponse, SingleIdResponse } from "constants/types";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import { ContainerProps } from "react-bootstrap";
import { Placement } from "react-bootstrap/esm/types";
import AudioPlayback from "./AudioPlayback";

interface ComponentProps {
  audioId: number;
  showDeleteButton?: boolean;
  showMixerButtons?: boolean;
  showLink?: boolean;
  showDownload?: boolean;
  tooltipPlacement?: Placement;
  settingsPlacement?: Placement;
  getResponseIfMissing?: boolean;
}

type Props = ComponentProps & ContainerProps;

const SingleAudioPlayback = (props: Props) => {
  const { audioId } = props;
  const { api } = useAuthentication();

  const [localResponse, setLocalResponse] = useState<SingleIdResponse | null>(
    null,
  );

  useEffect(() => {
    (async () => {
      try {
        const response = await api.post<QueryIdsResponse>("/audio/query/ids", {
          ids: [audioId],
        });
        setLocalResponse(response.data.infos[0]);
      } catch (error) {}
    })();
  }, [audioId, api]);

  return <AudioPlayback response={localResponse} {...props} />;
};

export default SingleAudioPlayback;
