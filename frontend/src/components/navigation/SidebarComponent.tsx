import {
  faCog,
  faMoon,
  faSignIn,
  faSignOut,
  faSun,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuthentication } from "hooks/auth";
import { useTheme } from "hooks/theme";
import { useCallback, useEffect, useState } from "react";
import { ListGroup, Offcanvas } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

interface Props {
  show: boolean;
  setShow: (show: boolean) => void;
}

interface UserInfoResponse {
  email: string;
}

const SidebarComponent = (props: Props) => {
  const { show, setShow } = props;
  const { theme, setTheme } = useTheme();
  const { isAuthenticated, logout, api } = useAuthentication();
  const [email, setEmail] = useState<string | null>(null);
  const navigate = useNavigate();

  const [darkMode, setDarkMode] = useState<boolean>(theme === "dark");

  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      setTheme(prev ? "light" : "dark");
      return !prev;
    });
  }, [setTheme]);

  useEffect(() => {
    (async () => {
      if (isAuthenticated) {
        if (email === null) {
          try {
            const response = await api.get<UserInfoResponse>("/users/me");
            setEmail(response.data.email);
          } catch (error) {}
        }
      } else {
        setEmail(null);
      }
    })();
  }, [email, isAuthenticated, api]);

  return (
    <Offcanvas show={show} onHide={() => setShow(false)} placement="end">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Options</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <ListGroup variant="flush">
          {email && <ListGroup.Item>{email}</ListGroup.Item>}
          <ListGroup.Item onClick={toggleDarkMode} action>
            <FontAwesomeIcon
              icon={darkMode ? faSun : faMoon}
              className="me-2"
              style={{
                width: "1.25em",
              }}
            />{" "}
            {darkMode ? "Light" : "Dark"} Mode
          </ListGroup.Item>
          {isAuthenticated ? (
            <>
              <ListGroup.Item
                onClick={() => {
                  navigate("/settings");
                  setShow(false);
                }}
                action
              >
                <FontAwesomeIcon
                  icon={faCog}
                  className="me-2"
                  style={{
                    width: "1.25em",
                  }}
                />{" "}
                Settings
              </ListGroup.Item>

              <ListGroup.Item onClick={logout} action>
                <FontAwesomeIcon
                  icon={faSignOut}
                  className="me-2"
                  style={{
                    width: "1.25em",
                  }}
                />{" "}
                Log Out
              </ListGroup.Item>
            </>
          ) : (
            <ListGroup.Item
              onClick={() => {
                navigate("/mix");
                setShow(false);
              }}
              action
            >
              <FontAwesomeIcon
                icon={faSignIn}
                className="me-2"
                style={{
                  width: "1.25em",
                }}
              />{" "}
              Log In
            </ListGroup.Item>
          )}
        </ListGroup>
      </Offcanvas.Body>
    </Offcanvas>
  );
};

export default SidebarComponent;
