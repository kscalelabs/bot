import { Button, Col, Container, Image, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import logo from "../../assets/logo.png";

interface Props {
  error?: string;
  code?: number;
}

const Error = (props: Props) => {
  const { error, code } = props;

  const navigate = useNavigate();

  const navigateToHome = () => {
    navigate("/");
  };

  return (
    <Container
      fluid
      className="h-100 d-flex justify-content-center align-items-center"
      style={{ minHeight: "100vh" }}
    >
      <Row className="text-center">
        <Col>
          <Row className="aspect-ratio aspect-ratio-1x1">
            <Col>
              <Image src={logo} alt="Logo" />
            </Col>
          </Row>
          <Row>
            <h3>{code}</h3>
            <h4>{error}</h4>
          </Row>
          <Row>
            <Col>
              <Button variant="primary" onClick={navigateToHome}>
                <i className="bi bi-house-door-fill me-2"></i> {/* Home icon */}
                Return Home
              </Button>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default Error;
