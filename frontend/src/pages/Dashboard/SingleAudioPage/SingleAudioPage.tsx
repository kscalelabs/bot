import AudioPlayback from "components/playback/AudioPlayback";
import { Col, Container, Row } from "react-bootstrap";
import { Navigate, useParams } from "react-router-dom";

const SingleAudioPage = () => {
  const { uuid } = useParams();

  if (uuid === undefined) {
    return <Navigate to="/library" />;
  }

  // return <AudioPlayback uuid={uuid} />;
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
            <AudioPlayback uuid={uuid} showLink={false} />
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default SingleAudioPage;
