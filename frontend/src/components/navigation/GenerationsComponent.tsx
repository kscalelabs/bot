import { useClipboard } from "hooks/clipboard";
import { ListGroup, Offcanvas } from "react-bootstrap";

interface Props {
  show: boolean;
  setShow: (show: boolean) => void;
}

const GenerationsComponent = (props: Props) => {
  const { show, setShow } = props;
  const { submissionIds } = useClipboard();

  return (
    <Offcanvas show={show} onHide={() => setShow(false)}>
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Generations</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <ListGroup variant="flush">
          <ListGroup.Item>First</ListGroup.Item>
          <ListGroup.Item>Second</ListGroup.Item>
          <ListGroup.Item>Third</ListGroup.Item>
          {submissionIds.map((submissionId) => (
            <ListGroup.Item key={submissionId}>{submissionId}</ListGroup.Item>
          ))}
        </ListGroup>
      </Offcanvas.Body>
    </Offcanvas>
  );
};

export default GenerationsComponent;
