import React from "react";
import { Card, CardProps } from "react-bootstrap";

interface AudioProps {
  uuid: string;
  title?: string;
}

type Props = AudioProps & CardProps;

const AudioPlayback: React.FC<Props> = ({
  uuid,
  title = "Audio",
  ...cardProps
}) => {
  return (
    <Card {...cardProps}>
      <Card.Header>{title}</Card.Header>
      <Card.Body>
        <Card.Title>Audio</Card.Title>
        <Card.Text>{uuid}</Card.Text>
      </Card.Body>
    </Card>
  );
};

export default AudioPlayback;
