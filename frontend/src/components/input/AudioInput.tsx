import AudioRecorder from "components/input/AudioRecoder";
import { useState } from "react";
import { Card, Nav } from "react-bootstrap";
import AudioUploader from "./AudioUploader";

type Tab = "record" | "upload";

const AudioInput = () => {
  const [currentTab, setCurrentTab] = useState<Tab>("record");

  const getCurrentTab = () => {
    switch (currentTab) {
      case "record":
        return <AudioRecorder />;
      case "upload":
        return <AudioUploader />;
    }
  };

  return (
    <Card>
      <Card.Header>
        <Nav
          variant="pills"
          activeKey={currentTab}
          onSelect={(event) => {
            setCurrentTab(event as Tab);
          }}
        >
          <Nav.Item>
            <Nav.Link eventKey="record">Record</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="upload">Upload</Nav.Link>
          </Nav.Item>
        </Nav>
      </Card.Header>
      {getCurrentTab()}
    </Card>
  );
};

export default AudioInput;
