import SingleGeneration from "components/playback/SingleGeneration";
import { api, humanReadableError } from "constants/backend";
import { useEffect, useState } from "react";
import { Alert, Col, Container, Row, Spinner } from "react-bootstrap";
import { Navigate, useParams } from "react-router-dom";

interface SingleGenerationResponse {
  id: number;
  output_id: number | null;
  reference_id: number;
  source_id: number;
  task_created: Date;
  task_finished: Date | null;
}

const SingleGenerationPage = () => {
  const { uuid } = useParams();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<SingleGenerationResponse | null>(
    null,
  );

  useEffect(() => {
    if (response === null) {
      (async () => {
        try {
          const apiResponse = await api.get<SingleGenerationResponse>(
            "/generation/id",
            {
              params: {
                output_id: uuid,
              },
            },
          );
          setResponse(apiResponse.data);
        } catch (error) {
          setErrorMessage(humanReadableError(error));
        }
      })();
    }
  }, [response, uuid]);

  if (uuid === undefined) {
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
                  taskCreated={response.task_created}
                  taskFinished={response.task_finished}
                  showLink={false}
                />
              )}
            </Col>
          </Row>
          {errorMessage !== null && (
            <Alert
              variant="danger"
              className="mt-3"
              onClose={() => setErrorMessage(null)}
              dismissible
            >
              <Alert.Heading>Oh snap!</Alert.Heading>
              <div>
                Encountered an error retrieving this generation:
                <br />
                <code>{errorMessage}</code>
              </div>
            </Alert>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default SingleGenerationPage;
