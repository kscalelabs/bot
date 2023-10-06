import { Card, Form } from "react-bootstrap";

const DashboardContent = () => {
  return (
    <Card>
      <Card.Header>File Upload</Card.Header>
      <Card.Body>
        <Form>
          <Form.Group controlId="file-upload">
            <Form.Label>Upload an audio file</Form.Label>
            <Form.Control type="file" />
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default DashboardContent;
