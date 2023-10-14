import { faSync } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import SingleGeneration from "components/playback/SingleGeneration";
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
  showRefreshButton?: boolean;
}

type Props = ListProps & RowProps;

interface InfoMeResponse {
  count: number;
}

interface QueryMeRequest {
  start: number;
  limit: number;
}

interface SingleGenerationResponse {
  output_id: string;
  reference_id: string;
  source_id: string;
  created: Date;
}

interface QueryMeResponse {
  generations: SingleGenerationResponse[];
}

const ListGenerations = (props: Props) => {
  const {
    paginationLimit = DEFAULT_PAGINATE_LIMIT,
    showRefreshButton = true,
    ...rowProps
  } = props;
  const [info, setInfo] = useState<InfoMeResponse | null>(null);
  const [generations, setGenerations] = useState<
    SingleGenerationResponse[] | null
  >(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [start, setStart] = useState(0);

  useEffect(() => {
    if (info === null) {
      (async () => {
        try {
          const response = await api.get<InfoMeResponse>("/generation/info/me");
          const newStart = Math.max(
            Math.min(start, response.data.count - paginationLimit),
            0,
          );
          setInfo(response.data);
          setStart(newStart);
          setGenerations(null);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    } else if (generations === null) {
      (async () => {
        try {
          const response = await api.get<QueryMeResponse>(
            "/generation/query/me",
            {
              params: {
                start: start,
                limit: paginationLimit,
              } as QueryMeRequest,
            },
          );
          setGenerations(response.data.generations);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    }
  }, [info, generations, start, paginationLimit]);

  const handleRefresh = () => {
    setGenerations(null);
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
                        setGenerations(null);
                      }}
                      disabled={start <= 0}
                    >
                      Previous
                    </Button>
                    <Button
                      onClick={() => {
                        setStart(start + paginationLimit);
                        setGenerations(null);
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
          (generations === null ? (
            <Row>
              <Col className="text-center">
                <Spinner />
              </Col>
            </Row>
          ) : (
            <Row>
              <Col>
                <Row>
                  {generations.length === 0 ? (
                    <Col className="mt-3">No samples found</Col>
                  ) : (
                    <Col>
                      {generations.map((generation, id) => (
                        <SingleGeneration
                          output_id={generation.output_id}
                          reference_id={generation.reference_id}
                          source_id={generation.source_id}
                          created={generation.created}
                          className="mt-3"
                          key={id}
                        />
                      ))}
                    </Col>
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

export default ListGenerations;
