import SingleGeneration from "components/playback/SingleGeneration";
import { humanReadableError } from "constants/backend";
import { useAlertQueue } from "hooks/alerts";
import { useAuthentication } from "hooks/auth";
import { useEffect, useState } from "react";
import { Col, Container, Row, Spinner } from "react-bootstrap";
import { Navigate, useParams } from "react-router-dom";

interface SingleGenerationResponse {
  id: number;
  output_id: number | null;
  reference_id: number;
  source_id: number;
  task_finished: Date;
}

const SingleGenerationPage = () => {
  const { id } = useParams();
  const [response, setResponse] = useState<SingleGenerationResponse | null>(
    null,
  );

  const { api } = useAuthentication();
  const { addAlert } = useAlertQueue();

  useEffect(() => {
    if (response === null) {
      (async () => {
        try {
          const apiResponse = await api.get<SingleGenerationResponse>(
            "/generation/id",
            {
              params: {
                id,
              },
            },
          );
          setResponse(apiResponse.data);
        } catch (error) {
          addAlert(humanReadableError(error), "error");
        }
      })();
    }
  }, [response, id, api, addAlert]);

  if (id === undefined) {
    return <Navigate to="/generations" />;
  }

  return (
    <Container className="mt-5 mb-5">
      <Row className="justify-content-center">
        <Col lg={12}>
          <Row className="mb-3">
            <Col className="text-center">
              <h1>Generation</h1>
            </Col>
          </Row>
          <Row className="mb-3">
            <Col>
              {response === null ? (
                <div className="d-flex justify-content-center">
                  <Spinner />
                </div>
              ) : (
                <SingleGeneration
                  generationId={response.id}
                  outputId={response.output_id}
                  referenceId={response.reference_id}
                  sourceId={response.source_id}
                  taskFinished={response.task_finished}
                  showLink={false}
                />
              )}
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default SingleGenerationPage;
