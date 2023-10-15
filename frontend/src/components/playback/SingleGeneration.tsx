import AudioPlayback from "components/playback/AudioPlayback";
import { Card, CardProps, Col, Row } from "react-bootstrap";
import { Link } from "react-router-dom";

interface ComponentProps {
  generationId: number;
  outputId: number | null;
  referenceId: number;
  sourceId: number;
  taskCreated: Date;
  taskFinished: Date | null;
  showLink?: boolean;
}

type Props = ComponentProps & CardProps;

const SingleGeneration = (props: Props) => {
  const {
    generationId,
    outputId,
    referenceId,
    sourceId,
    taskCreated,
    taskFinished,
    showLink = true,
    ...cardProps
  } = props;

  return (
    <Card {...cardProps}>
      <Card.Header>
        Generation {generationId} -
        {` Created ${new Date(taskCreated).toLocaleString()} -`}
        {taskFinished === null
          ? " Processing..."
          : ` Finished ${new Date(taskFinished).toLocaleString()}`}
        {showLink && (
          <span>
            {" - "}
            <strong>
              <Link to={`/generation/${generationId}`}>Link</Link>
            </strong>
          </span>
        )}
      </Card.Header>
      <Card.Body>
        <Row>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <AudioPlayback audioId={sourceId} title="Source" />
          </Col>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <AudioPlayback audioId={referenceId} title="Reference" />
          </Col>
          {outputId !== null && (
            <Col sm={12} md={12} lg={4} className="mt-2">
              <AudioPlayback audioId={outputId} title="Generated" />
            </Col>
          )}
        </Row>
      </Card.Body>
    </Card>
  );
};

export default SingleGeneration;
