import AudioPlayback from "components/playback/AudioPlayback";
import { humanReadableError } from "constants/backend";
import {
  QueryIdsRequest,
  QueryIdsResponse,
  SingleIdResponse,
} from "constants/types";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import { Col, Row } from "react-bootstrap";

interface Props {
  audioIds: number[];
}

const AudioPlaybackList = (props: Props) => {
  const { audioIds } = props;
  const [audioInfos, setAudioInfos] = useState<Map<
    number,
    SingleIdResponse
  > | null>(null);

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  useEffect(() => {
    if (audioIds !== null && audioInfos === null) {
      (async () => {
        try {
          const response = await api.post<QueryIdsResponse>(
            "/audio/query/ids",
            {
              ids: audioIds,
            } as QueryIdsRequest,
          );
          // setAudioInfos(response.data);
          const infos = new Map<number, SingleIdResponse>();
          response.data.infos.forEach((info) => {
            infos.set(info.id, info);
          });
          setAudioInfos(infos);
        } catch (error) {
          addAlert(humanReadableError(error), "error");
        }
      })();
    }
  }, [audioIds, audioInfos, api, addAlert]);

  return (
    <Row>
      <Col>
        <Row>
          {audioIds.length === 0 ? (
            <Col className="mt-3">No samples found</Col>
          ) : (
            audioIds.map((audioId) => (
              <Col sm={12} md={6} lg={4} xxl={3} key={audioId} className="mt-3">
                <AudioPlayback
                  audioId={audioId}
                  response={
                    audioInfos === null ? null : audioInfos.get(audioId) ?? null
                  }
                />
              </Col>
            ))
          )}
        </Row>
      </Col>
    </Row>
  );
};

export default AudioPlaybackList;
