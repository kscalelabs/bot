import { faSync } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AudioPlaybackList from "components/playback/AudioPlaybackList";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import {
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

const DEFAULT_PAGINATE_LIMIT = 24;

interface ListProps {
  paginationLimit?: number;
  showRefreshButton?: boolean;
  showSearchBar?: boolean;
}

type Props = ListProps & RowProps;

interface QueryMeRequest {
  start: number;
  limit: number;
  source?: string;
}

interface QueryMeResponse {
  ids: number[];
  total: number;
}

const ListAudios = (props: Props) => {
  const {
    paginationLimit = DEFAULT_PAGINATE_LIMIT,
    showRefreshButton = true,
    showSearchBar = true,
    ...rowProps
  } = props;
  const [audios, setAudios] = useState<QueryMeResponse | null>(null);
  const [start, setStart] = useState(0);
  const [searchTerm, setSearchTerm] = useState<string>("");

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  useEffect(() => {
    if (audios === null) {
      (async () => {
        try {
          const response = await api.get<QueryMeResponse>("/audio/query/me", {
            params: {
              start: start,
              limit: paginationLimit,
              q: searchTerm,
            } as QueryMeRequest,
          });
          if (response.data.ids.length === 0 && start > 0) {
            setStart(Math.max(start - paginationLimit, 0));
          } else {
            setAudios(response.data);
          }
        } catch (error) {
          addAlert(humanReadableError(error), "error");
        }
      })();
    }
  }, [audios, start, paginationLimit, searchTerm, api, addAlert]);

  const handleRefresh = () => {
    setAudios(null);
  };

  return (
    <Row {...rowProps}>
      <Col>
        <Row>
          <Col className="text-center">
            {audios === null ? (
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
                {audios.total > paginationLimit && (
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
                      disabled={start + paginationLimit >= audios.total}
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
        {audios !== null && <AudioPlaybackList audioIds={audios.ids} />}
      </Col>
    </Row>
  );
};

export default ListAudios;
