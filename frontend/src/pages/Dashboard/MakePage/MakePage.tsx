import AudioInput from "components/input/AudioInput";
import ListAudios from "components/list/ListAudios";
import { Col, Container, Row } from "react-bootstrap";

const MakePage = () => {
  return (
    <Container className="mt-5 mb-5">
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="mb-3">
            <Col className="text-center">
              <h1>Make</h1>
            </Col>
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
          <ListAudios paginationLimit={4} />
        </Col>
      </Row>
    </Container>
  );
};

export default MakePage;
