
import { useEffect, useState } from "react";

import {
  createProject,
  getProjects,
  type Project,
} from "./api/projects";


function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch {
        setError("Failed to load projects");
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

  const handleCreateProject = async (event: SubmitEvent) => {
    event.preventDefault();

    setCreating(true);
    setError(null);

    try {
      const project = await createProject({
        name,
        description: description || undefined,
        repository_url: repositoryUrl || undefined,
      });

      setProjects((currentProjects) => [
        ...currentProjects,
        project,
      ]);

      setName("");
      setDescription("");
      setRepositoryUrl("");
    } catch {
      setError("Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return <p>Loading projects...</p>;
  }

  return (
    <div>
      <h1>ShipForge</h1>

      <h2>Create Project</h2>

      <form onSubmit={handleCreateProject}>
        <div>
          <label>
            Name
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Description
            <input
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </label>
        </div>

        <div>
          <label>
            Repository URL
            <input
              value={repositoryUrl}
              onChange={(event) => setRepositoryUrl(event.target.value)}
            />
          </label>
        </div>

        <button type="submit" disabled={creating}>
          {creating ? "Creating..." : "Create Project"}
        </button>
      </form>

      {error && <p>{error}</p>}

      <h2>Projects</h2>

      {projects.length === 0 ? (
        <p>No projects found.</p>
      ) : (
        <ul>
          {projects.map((project) => (
            <li key={project.id}>
              <strong>{project.name}</strong>

              {project.description && (
                <p>{project.description}</p>
              )}

              {project.repository_url && (
                <p>{project.repository_url}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
