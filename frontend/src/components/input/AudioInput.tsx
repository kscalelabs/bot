import AudioMixer from "components/input/AudioMixer";
import AudioRecorder from "components/input/AudioRecoder";
import AudioUploader from "components/input/AudioUploader";
import { useState } from "react";
import { Card, Nav } from "react-bootstrap";

type Tab = "record" | "upload" | "mix";

interface Props {
  tabs?: Tab[];
}

const AudioInput = (props: Props) => {
  const { tabs = ["record", "upload", "mix"] } = props;
  if (tabs.length === 0) throw new Error("Tabs must not be empty");

  const [currentTab, setCurrentTab] = useState<Tab>(tabs[0]);

  const getCurrentTab = () => {
    switch (currentTab) {
      case "record":
        return <AudioRecorder />;
      case "upload":
        return <AudioUploader />;
      case "mix":
        return <AudioMixer />;
    }
  };

  return (
    <Card>
      {tabs.length > 1 && (
        <Card.Header>
          <Nav
            variant="tabs"
            activeKey={currentTab}
            onSelect={(event) => {
              setCurrentTab(event as Tab);
            }}
          >
            <Nav.Item>
              <Nav.Link eventKey="record" hidden={!tabs.includes("record")}>
                Record
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="upload" hidden={!tabs.includes("upload")}>
                Upload
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="mix" hidden={!tabs.includes("mix")}>
                Mix
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
      )}
      {getCurrentTab()}
    </Card>
  );
};

export default AudioInput;
