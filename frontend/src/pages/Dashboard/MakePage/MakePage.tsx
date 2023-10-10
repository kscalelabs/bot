import AudioInput from "components/input/AudioInput";
import { Col, Container, Row } from "react-bootstrap";

const MakePage = () => {
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={8}>
          <Row>
            <h1>Make</h1>
          </Row>
          <Row className="mb-3">
            <Col>
              <AudioInput />
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default MakePage;
