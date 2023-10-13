import { api } from "constants/backend";
import { useEffect, useState } from "react";
import { Col, Container, Row } from "react-bootstrap";
import AdminComponent from "./components/AdminComponent";
import DeleteAccountComponent from "./components/DeleteAccountComponent";
import PaymentComponent from "./components/PaymentComponent";

const SettingsPage = () => {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    (async () => {
      try {
        const response = await api.get<boolean>("/users/admin/check");
        console.log(response);
        setIsAdmin(response.data);
      } catch (error) {}
    })();
  });

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="mb-3">
            <Col className="text-center">
              <h1>Settings</h1>
            </Col>
          </Row>
          <Row className="mb-3">
            <PaymentComponent />
          </Row>
          <Row className="mb-3">
            <DeleteAccountComponent />
          </Row>
          {isAdmin && (
            <Row className="mb-3">
              <AdminComponent />
            </Row>
          )}
          <Row className="mt-5">
            <p>
              <i>Seeing issues? Send an email to</i> <code>ben@dpsh.dev</code>
            </p>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default SettingsPage;
