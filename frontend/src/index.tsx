import App from "App";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "font-awesome/css/font-awesome.min.css";
import "index.css";
import { createRoot } from "react-dom/client";
import reportWebVitals from "reportWebVitals";

const root = createRoot(document.getElementById("root")!);

root.render(<App />);

reportWebVitals();
