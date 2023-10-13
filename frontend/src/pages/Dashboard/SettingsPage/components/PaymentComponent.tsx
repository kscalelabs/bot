import { Card, Col, Row } from "react-bootstrap";

interface PaymentPlanProps {
  title: string;
  description: string;
  price: number;
}

const PaymentPlanCard = (props: PaymentPlanProps) => {
  const { title, description, price } = props;
  return (
    <Col className="mb-3" md={12} lg={12} xl={4}>
      <Card>
        <Card.Body>
          <Card.Title>{title}</Card.Title>
          <Card.Text>{description}</Card.Text>
          <Card.Text>{price}</Card.Text>
        </Card.Body>
      </Card>
    </Col>
  );
};

const PaymentComponent = () => {
  return (
    <Col>
      <Row className="mb-3">
        <Col className="text-center">
          <h2>Payment</h2>
        </Col>
      </Row>

      <Row>
        <PaymentPlanCard
          title="Plan 1"
          description="Details for plan 1"
          price={10.0}
        />
        <PaymentPlanCard
          title="Plan 2"
          description="Details for plan 2"
          price={20.0}
        />
        <PaymentPlanCard
          title="Plan 3"
          description="Details for plan 3"
          price={30.0}
        />
      </Row>
    </Col>
  );
};

export default PaymentComponent;
