import { Card, CardProps, Col, Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import SingleAudioPlayback from "./SingleAudioPlayback";

interface ComponentProps {
  generationId: number;
  outputId: number | null;
  referenceId: number;
  sourceId: number;
  taskFinished: Date;
  showLink?: boolean;
}

type Props = ComponentProps & CardProps;

const SingleGeneration = (props: Props) => {
  const {
    generationId,
    outputId,
    referenceId,
    sourceId,
    taskFinished,
    showLink = true,
    ...cardProps
  } = props;

  return (
    <Card {...cardProps}>
      <Card.Header>Generation {generationId}</Card.Header>
      <Card.Body>
        <Card.Text>
          Created {new Date(taskFinished).toLocaleString()}
          <br />
          {taskFinished === null
            ? " Processing..."
            : ` Finished ${new Date(taskFinished).toLocaleString()}`}
          {showLink && (
            <>
              <br />
              <strong>
                <Link to={`/generation/${generationId}`}>Link</Link>
              </strong>
            </>
          )}
        </Card.Text>
        <Row>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <SingleAudioPlayback audioId={sourceId} title="Source" />
          </Col>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <SingleAudioPlayback audioId={referenceId} title="Reference" />
          </Col>
          {outputId !== null && (
            <Col sm={12} md={12} lg={4} className="mt-2">
              <SingleAudioPlayback audioId={outputId} title="Generated" />
            </Col>
          )}
        </Row>
      </Card.Body>
    </Card>
  );
};

export default SingleGeneration;
