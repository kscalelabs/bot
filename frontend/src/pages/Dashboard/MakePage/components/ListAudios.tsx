import AudioPlayback from "components/playback/AudioPlayback";
import { api, humanReadableError } from "constants/backend";
import { useEffect, useState } from "react";
import { Alert, Button, ButtonGroup, Col, Row, Spinner } from "react-bootstrap";

const PAGINATE_LIMIT = 10;

interface InfoMeResponse {
  count: number;
}

interface QueryMeRequest {
  start: number;
  limit: number;
  source?: string;
}

interface QueryMeResponse {
  uuids: string[];
}

const ListAudios = () => {
  const [info, setInfo] = useState<InfoMeResponse | null>(null);
  const [audios, setAudios] = useState<string[] | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [start, setStart] = useState(0);

  useEffect(() => {
    if (info === null) {
      (async () => {
        try {
          const response = await api.get<InfoMeResponse>("/audio/info/me");
          const newStart = Math.max(
            Math.min(start, response.data.count - PAGINATE_LIMIT),
            0
          );
          setInfo(response.data);
          setStart(newStart);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    } else {
      (async () => {
        try {
          const response = await api.get<QueryMeResponse>("/audio/query/me", {
            params: {
              start: start,
              limit: PAGINATE_LIMIT,
              source: "recorded",
            } as QueryMeRequest,
          });
          setAudios(response.data.uuids);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    }
  }, [info, start]);

  const handleRefresh = () => {
    setAudios(null);
    setInfo(null);
  };

  console.log(info, start, PAGINATE_LIMIT);

  return (
    <>
      {audios === null ? (
        <Row>
          <Col className="text-center">
            <Spinner />
          </Col>
        </Row>
      ) : (
        <>
          <Row>
            <ButtonGroup>
              <Button onClick={handleRefresh}>Refresh</Button>
              {info !== null && info.count > PAGINATE_LIMIT && (
                <>
                  <Button
                    onClick={() => {
                      setStart(Math.max(start - PAGINATE_LIMIT, 0));
                    }}
                    disabled={start <= 0}
                  >
                    Previous
                  </Button>
                  <Button
                    onClick={() => {
                      setStart(start + PAGINATE_LIMIT);
                    }}
                    disabled={start + PAGINATE_LIMIT >= info.count}
                  >
                    Next
                  </Button>
                </>
              )}
            </ButtonGroup>
          </Row>
          <Row>
            <Col>
              <Row>
                {audios.map((uuid) => (
                  <Col sm={12} md={6} lg={6} key={uuid} className="mt-3">
                    <AudioPlayback uuid={uuid} />
                  </Col>
                ))}
              </Row>
            </Col>
          </Row>
        </>
      )}
      {errorMessage && (
        <Row>
          <Alert
            variant="warning"
            className="mt-3"
            onClose={() => setErrorMessage(null)}
            dismissible
          >
            <Alert.Heading>Oh snap!</Alert.Heading>
            <div>
              An error occurred while fetching your information.
              <br />
              <code>{errorMessage}</code>
            </div>
          </Alert>
        </Row>
      )}
    </>
  );
};

export default ListAudios;
