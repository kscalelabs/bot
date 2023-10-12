import { Col, Container, Row } from "react-bootstrap";

const HomePage = () => {
  return (
    <Container className="mt-5 mb-5">
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="mb-3">
            <Col className="text-center">
              <h3>
                don't panic
                <br />
                stay human
              </h3>
            </Col>
          </Row>
          <Row className="mb-3">
            <Col className="text-center">
              <h5>ai-powered voice mixer</h5>
            </Col>
          </Row>
          <Row className="mb-3">
            <Col className="text-center">
              visit the <code>make</code> tab
              <br />
              upload some reference audio file
              <br />
              record yourself saying something
              <br />
              select the two samples in the mixer
              <br />
              click <code>mix</code>
              <br />
              wait for the magic to happen
              <br />
              listen to the result
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
