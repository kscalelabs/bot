import AudioRecorder from "components/audio/AudioRecoder";
import AudioUploader from "components/audio/AudioUploader";
import { Col, Container, Row } from "react-bootstrap";

const MakePage = () => {
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={8}>
          <Row>
            <h1>Make</h1>
          </Row>
          <Row>
            <AudioRecorder />
            <AudioUploader />
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default MakePage;
