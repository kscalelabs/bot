import RequireAuthentication from "components/auth/RequireAuthentication";
import { useAuthentication } from "hooks/auth";
import AdminAudioComponent from "pages/Dashboard/SettingsPage/components/AdminAudioComponent";
import AdminGenerationComponent from "pages/Dashboard/SettingsPage/components/AdminGenerationComponent";
import AdminUserComponent from "pages/Dashboard/SettingsPage/components/AdminUserComponent";
import DeleteAccountComponent from "pages/Dashboard/SettingsPage/components/DeleteAccountComponent";
import PaymentComponent from "pages/Dashboard/SettingsPage/components/PaymentComponent";
import { useEffect, useState } from "react";
import { Col, Container, Row } from "react-bootstrap";

const SettingsPage = () => {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const { api } = useAuthentication();

  useEffect(() => {
    (async () => {
      try {
        const response = await api.get<boolean>("/admin/check");
        setIsAdmin(response.data);
      } catch (error) {}
    })();
  });

  return (
    <RequireAuthentication>
      <Container className="mt-5 mb-5">
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
              <>
                <Row className="mb-3">
                  <Col className="text-center">
                    <h2>Admin</h2>
                  </Col>
                </Row>
                <Row className="mb-3">
                  <Col className="text-center">
                    <h3>User</h3>
                  </Col>
                </Row>
                <Row className="mb-3">
                  <AdminUserComponent />
                </Row>
                <Row className="mb-3">
                  <Col className="text-center">
                    <h3>Audio</h3>
                  </Col>
                </Row>
                <Row className="mb-3">
                  <AdminAudioComponent />
                </Row>
                <Row className="mb-3">
                  <Col className="text-center">
                    <h3>Generation</h3>
                  </Col>
                </Row>
                <Row className="mb-3">
                  <AdminGenerationComponent />
                </Row>
              </>
            )}
            <Row className="mt-5">
              <p>
                <i>Seeing issues? Send an email to</i> <code>ben@dpsh.dev</code>
              </p>
            </Row>
          </Col>
        </Row>
      </Container>
    </RequireAuthentication>
  );
};

export default SettingsPage;
