import SingleGeneration from "components/playback/SingleGeneration";
import { api, humanReadableError } from "constants/backend";
import { useEffect, useState } from "react";
import { Col, Container, Row, Spinner } from "react-bootstrap";
import { Navigate, useParams } from "react-router-dom";

interface SingleGenerationResponse {
  output_id: string;
  reference_id: string;
  source_id: string;
  created: Date;
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
  }, [response]);

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
                  output_id={response.output_id}
                  reference_id={response.reference_id}
                  source_id={response.source_id}
                  created={response.created}
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
