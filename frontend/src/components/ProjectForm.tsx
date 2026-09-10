import { useState } from "react";

import {
    createProject,
    type Project,
} from "../api/projects";

interface ProjectFormProps {
    onProjectCreated: (project: Project) => void;
}

function ProjectForm({
    onProjectCreated,
}: ProjectFormProps) {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [repositoryUrl, setRepositoryUrl] = useState("");
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleCreateProject = async (
        event: React.FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        setCreating(true);
        setError(null);

        try {
            const project = await createProject({
                name,
                description: description || undefined,
                repository_url: repositoryUrl || undefined,
            });

            onProjectCreated(project);

            setName("");
            setDescription("");
            setRepositoryUrl("");
        } catch {
            setError("Failed to create project");
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6 shadow-2xl shadow-black/10">
            {/* Card heading */}
            <div className="mb-6">
                <h3 className="text-base font-semibold text-zinc-100">
                    Create a project
                </h3>

                <p className="mt-1 text-sm text-zinc-500">
                    Add a repository to start building with ShipForge.
                </p>
            </div>

            <form
                onSubmit={handleCreateProject}
                className="space-y-5"
            >
                {/* Project name */}
                <div>
                    <label
                        htmlFor="project-name"
                        className="mb-2 block text-sm font-medium text-zinc-300"
                    >
                        Project name
                    </label>

                    <input
                        id="project-name"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                        placeholder="my-awesome-project"
                        required
                        className="w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3.5 py-2.5 text-sm text-zinc-100 outline-none transition placeholder:text-zinc-600 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
                    />
                </div>

                {/* Description */}
                <div>
                    <label
                        htmlFor="project-description"
                        className="mb-2 block text-sm font-medium text-zinc-300"
                    >
                        Description
                    </label>

                    <textarea
                        id="project-description"
                        value={description}
                        onChange={(event) =>
                            setDescription(event.target.value)
                        }
                        placeholder="What are you building?"
                        rows={3}
                        className="w-full resize-none rounded-lg border border-zinc-800 bg-zinc-950 px-3.5 py-2.5 text-sm text-zinc-100 outline-none transition placeholder:text-zinc-600 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
                    />
                </div>

                {/* Repository URL */}
                <div>
                    <label
                        htmlFor="repository-url"
                        className="mb-2 block text-sm font-medium text-zinc-300"
                    >
                        Repository URL
                    </label>

                    <input
                        id="repository-url"
                        type="url"
                        value={repositoryUrl}
                        onChange={(event) =>
                            setRepositoryUrl(event.target.value)
                        }
                        placeholder="https://github.com/username/repository"
                        className="w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3.5 py-2.5 font-mono text-sm text-zinc-100 outline-none transition placeholder:text-zinc-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
                    />
                </div>

                {error && (
                    <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-3.5 py-2.5 text-sm text-red-400">
                        {error}
                    </div>
                )}

                {/* Submit */}
                <div className="flex justify-end pt-1">
                    <button
                        type="submit"
                        disabled={creating}
                        className="inline-flex items-center gap-2 rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {creating && (
                            <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        )}

                        {creating ? "Creating..." : "Create project"}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default ProjectForm;