import AudioRecorder from "components/audio/AudioRecoder";
import AudioUploader from "components/audio/AudioUploader";
import { Col, Container, Row } from "react-bootstrap";

const MakePage = () => {
  return (
    <Container>
      <Col>
        <Row>
          <h1>Make</h1>
        </Row>
        <Row>
          <AudioRecorder />
          <AudioUploader />
        </Row>
      </Col>
    </Container>
  );
};

export default MakePage;
