import logo from "assets/logo_nb.webp";
import { Button, Col, Container, Image, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

interface Props {
  error?: string;
  code?: number;
}

const ErrorPage = (props: Props) => {
  const { error, code } = props;

  const navigate = useNavigate();

  const navigateToHome = () => {
    navigate("/");
  };

  return (
    <Container>
      <Row className="text-center">
        <Col>
          <Row className="aspect-ratio aspect-ratio-1x1">
            <Col>
              <Image
                src={logo}
                alt="Logo"
                style={{
                  maxHeight: "20vh",
                }}
              />
            </Col>
          </Row>
          <Row>
            <h3>{code}</h3>
            <h4>{error}</h4>
          </Row>
          <Row className="mt-3">
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

export default ErrorPage;
