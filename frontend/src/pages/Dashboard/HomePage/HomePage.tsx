import { Col, Container, Row } from "react-bootstrap";

const HomePage = () => {
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={8}>
          <h1>Home</h1>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
