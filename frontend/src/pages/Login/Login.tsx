import React from "react";
import logo from "./logo.png";

const Login: React.FC = () => {
  return (
    <div className="container">
      <div className="content">
        <img src={logo} alt="logo" />
        <div>don't panic</div>
        <div>stay human</div>
      </div>
    </div>
  );
};

export default Login;
