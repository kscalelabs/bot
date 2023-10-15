import ListGenerations from "components/list/ListGenerations";
import { Col, Container, Row } from "react-bootstrap";

const GenerationsPage = () => {
  return (
    <Container className="mt-5 mb-5">
      <Row className="justify-content-center">
        <Col lg={12}>
          <Row className="mb-3">
            <Col className="text-center">
              <h1>Generations</h1>
            </Col>
          </Row>
          <ListGenerations showRefreshButton={false} className="mb-3" />
        </Col>
      </Row>
    </Container>
  );
};

export default GenerationsPage;
