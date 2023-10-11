import AudioInput from "components/input/AudioInput";
import { Col, Container, Row } from "react-bootstrap";
import ListAudios from "./components/ListAudios";

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
              <AudioInput tabs={["record", "upload"]} />
            </Col>
          </Row>
          <Row className="mb-3">
            <Col>
              <AudioInput tabs={["mix"]} />
            </Col>
          </Row>
          <ListAudios />
        </Col>
      </Row>
    </Container>
  );
};

export default MakePage;
