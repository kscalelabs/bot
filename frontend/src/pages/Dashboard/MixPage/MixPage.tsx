import RequireAuthentication from "components/auth/RequireAuthentication";
import ListAudios from "components/list/ListAudios";
import { Container } from "react-bootstrap";

const MixPage = () => {
  return (
    <RequireAuthentication>
      <Container className="mt-5 mb-5">
        <ListAudios />
      </Container>
    </RequireAuthentication>
  );
};

export default MixPage;
