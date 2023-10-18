import RequireAuthentication from "components/auth/RequireAuthentication";
import AudioInput from "components/input/AudioInput";
import { Col, Container, Row } from "react-bootstrap";

const UploadPage = () => {
  return (
    <RequireAuthentication>
      <Container className="mt-5 mb-5">
        <Row className="justify-content-center">
          <Col md={12}>
            <Row>
              <Col md={12} lg={6} className="mt-3">
                <AudioInput tabs={["record"]} />
              </Col>
              <Col md={12} lg={6} className="mt-3">
                <AudioInput tabs={["upload"]} />
              </Col>
            </Row>
          </Col>
        </Row>
      </Container>
    </RequireAuthentication>
  );
};

export default UploadPage;
