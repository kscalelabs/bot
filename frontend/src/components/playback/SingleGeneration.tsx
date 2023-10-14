import AudioPlayback from "components/playback/AudioPlayback";
import { Card, CardProps, Col, Row } from "react-bootstrap";
import { Link } from "react-router-dom";

interface ComponentProps {
  output_id: string;
  reference_id: string;
  source_id: string;
  created: Date;
  showLink?: boolean;
}

type Props = ComponentProps & CardProps;

const SingleGeneration = (props: Props) => {
  const {
    output_id,
    reference_id,
    source_id,
    created,
    showLink = true,
    ...cardProps
  } = props;

  return (
    <Card {...cardProps}>
      <Card.Header>
        Created {new Date(created).toLocaleString()}
        {showLink && (
          <span>
            {" - "}
            <strong>
              <Link to={`/generation/${output_id}`}>Link</Link>
            </strong>
          </span>
        )}
      </Card.Header>
      <Card.Body>
        <Row>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <AudioPlayback uuid={source_id} title="Source" />
          </Col>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <AudioPlayback uuid={reference_id} title="Reference" />
          </Col>
          <Col sm={12} md={12} lg={4} className="mt-2">
            <AudioPlayback uuid={output_id} title="Generated" />
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

export default SingleGeneration;
