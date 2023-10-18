import RequireAuthentication from "components/auth/RequireAuthentication";
import AudioInput from "components/input/AudioInput";
import ListAudios from "components/list/ListAudios";
import { Col, Container, Row } from "react-bootstrap";

const MakePage = () => {
  return (
    <RequireAuthentication>
      <Container className="mt-5 mb-5">
        <Row className="justify-content-center">
          <Col md={8}>
            <Row className="mb-3">
              <Col className="text-center">
                <h2>Add</h2>
              </Col>
            </Row>
            <Row>
              <Col>
                <AudioInput tabs={["record", "upload"]} />
              </Col>
            </Row>
            <Row className="mt-5 mb-3">
              <Col className="text-center">
                <h2>Mix</h2>
              </Col>
            </Row>
            <Row>
              <Col>
                <AudioInput tabs={["mix"]} />
              </Col>
            </Row>
            <Row className="mt-5 mb-3">
              <Col className="text-center">
                <h2>Listen</h2>
              </Col>
            </Row>
            <ListAudios paginationLimit={4} />
          </Col>
        </Row>
      </Container>
    </RequireAuthentication>
  );
};

export default MakePage;
