import SingleAudioPlayback from "components/playback/SingleAudioPlayback";
import { Col, Container, Row } from "react-bootstrap";
import { Navigate, useParams } from "react-router-dom";

const SingleAudioPage = () => {
  const { id } = useParams();
  const idNumber = parseInt(id || "");

  if (isNaN(idNumber)) {
    return <Navigate to="/library" />;
  }

  return (
    <Container className="mt-5 mb-5">
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="mb-3">
            <Col className="text-center">
              <h1>Audio</h1>
            </Col>
          </Row>
          <Row className="mb-3">
            <SingleAudioPlayback audioId={idNumber} showLink={false} />
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default SingleAudioPage;
