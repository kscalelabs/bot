import AudioPlayback from "components/playback/AudioPlayback";
import { api, humanReadableError } from "constants/backend";
import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  ButtonGroup,
  ButtonToolbar,
  Col,
  Row,
  RowProps,
  Spinner,
} from "react-bootstrap";

const DEFAULT_PAGINATE_LIMIT = 10;

interface ListProps {
  paginationLimit?: number;
}

type Props = ListProps & RowProps;

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

const ListAudios = (props: Props) => {
  const { paginationLimit = DEFAULT_PAGINATE_LIMIT, ...rowProps } = props;
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
            Math.min(start, response.data.count - paginationLimit),
            0
          );
          setInfo(response.data);
          setStart(newStart);
          setAudios(null);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    } else if (audios === null) {
      (async () => {
        try {
          const response = await api.get<QueryMeResponse>("/audio/query/me", {
            params: {
              start: start,
              limit: paginationLimit,
            } as QueryMeRequest,
          });
          setAudios(response.data.uuids);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    }
  }, [info, audios, start, paginationLimit]);

  const handleRefresh = () => {
    setAudios(null);
    setInfo(null);
  };

  console.log(info, start, paginationLimit);

  return (
    <Row {...rowProps}>
      <Col>
        <Row>
          <Col className="text-center">
            {info === null ? (
              <Spinner />
            ) : (
              <ButtonToolbar>
                <ButtonGroup className="me-2">
                  <Button onClick={handleRefresh}>Refresh</Button>
                </ButtonGroup>
                {info.count > paginationLimit && (
                  <ButtonGroup>
                    <Button
                      onClick={() => {
                        setStart(Math.max(start - paginationLimit, 0));
                        setAudios(null);
                      }}
                      disabled={start <= 0}
                    >
                      Previous
                    </Button>
                    <Button
                      onClick={() => {
                        setStart(start + paginationLimit);
                        setAudios(null);
                      }}
                      disabled={start + paginationLimit >= info.count}
                    >
                      Next
                    </Button>
                  </ButtonGroup>
                )}
              </ButtonToolbar>
            )}
          </Col>
        </Row>
        {info !== null &&
          (audios === null ? (
            <Row>
              <Col className="text-center">
                <Spinner />
              </Col>
            </Row>
          ) : (
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
          ))}
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
      </Col>
    </Row>
  );
};

export default ListAudios;
