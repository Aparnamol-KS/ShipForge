import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import ProjectsPage from "./pages/ProjectsPage";
import ProjectDetailsPage from "./pages/ProjectDetailsPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-zinc-950 text-zinc-100">
        <Routes>
          <Route path="/" element={<ProjectsPage />} />

          <Route
            path="/projects/:projectId"
            element={<ProjectDetailsPage />}
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;