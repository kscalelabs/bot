import { faSync } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AudioPlayback from "components/playback/AudioPlayback";
import { humanReadableError } from "constants/backend";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  ButtonGroup,
  ButtonToolbar,
  Col,
  Form,
  InputGroup,
  Row,
  RowProps,
  Spinner,
} from "react-bootstrap";

const DEFAULT_PAGINATE_LIMIT = 10;

interface ListProps {
  paginationLimit?: number;
  showRefreshButton?: boolean;
  showSearchBar?: boolean;
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
  ids: number[];
}

const ListAudios = (props: Props) => {
  const {
    paginationLimit = DEFAULT_PAGINATE_LIMIT,
    showRefreshButton = true,
    showSearchBar = true,
    ...rowProps
  } = props;
  const [info, setInfo] = useState<InfoMeResponse | null>(null);
  const [audios, setAudios] = useState<number[] | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [start, setStart] = useState(0);
  const [searchTerm, setSearchTerm] = useState<string>("");

  const { api } = useAuthentication();

  useEffect(() => {
    if (info === null) {
      (async () => {
        try {
          const response = await api.get<InfoMeResponse>("/audio/info/me");
          const newStart = Math.max(
            Math.min(start, response.data.count - paginationLimit),
            0,
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
          if (searchTerm.length > 0) {
            const response = await api.get<QueryMeResponse>("/audio/query/me", {
              params: {
                start: start,
                limit: paginationLimit,
                q: searchTerm,
              } as QueryMeRequest,
            });
            setAudios(response.data.ids);
          } else {
            const response = await api.get<QueryMeResponse>("/audio/query/me", {
              params: {
                start: start,
                limit: paginationLimit,
              } as QueryMeRequest,
            });
            setAudios(response.data.ids);
          }
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    }
  }, [info, audios, start, paginationLimit, searchTerm, api]);

  const handleRefresh = () => {
    setAudios(null);
    setInfo(null);
  };

  return (
    <Row {...rowProps}>
      <Col>
        <Row>
          <Col className="text-center">
            {info === null ? (
              <Spinner />
            ) : (
              <ButtonToolbar>
                {showRefreshButton && (
                  <ButtonGroup className="mt-2 me-2">
                    <Button onClick={handleRefresh}>
                      <FontAwesomeIcon icon={faSync} /> Refresh
                    </Button>
                  </ButtonGroup>
                )}
                {info.count > paginationLimit && (
                  <ButtonGroup className="mt-2 me-2">
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
                {showSearchBar && (
                  <InputGroup className="mt-2 me-2">
                    <Form.Control
                      type="text"
                      placeholder="Search"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onBlur={handleRefresh}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          handleRefresh();
                        }
                      }}
                    />
                  </InputGroup>
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
                  {audios.length === 0 ? (
                    <Col className="mt-3">No samples found</Col>
                  ) : (
                    audios.map((audioId) => (
                      <Col sm={12} md={6} lg={6} key={audioId} className="mt-3">
                        <AudioPlayback audioId={audioId} />
                      </Col>
                    ))
                  )}
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
