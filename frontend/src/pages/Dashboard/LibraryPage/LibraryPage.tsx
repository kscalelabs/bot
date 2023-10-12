import ListAudios from "components/list/ListAudios";
import { Col, Container, Row } from "react-bootstrap";

const LibraryPage = () => {
  return (
    <Container className="mt-5 mb-5">
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="mb-3">
            <Col className="text-center">
              <h1>Library</h1>
            </Col>
          </Row>
          <ListAudios showRefreshButton={false} className="mb-3" />
        </Col>
      </Row>
    </Container>
  );
};

export default LibraryPage;
