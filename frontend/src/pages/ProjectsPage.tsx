import { useEffect, useState } from "react";

import {
    getProjects,
    type Project,
} from "../api/projects";

import ProjectForm from "../components/ProjectForm";
import ProjectList from "../components/ProjectList";

function ProjectsPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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

    const handleProjectCreated = (project: Project) => {
        setProjects((currentProjects) => [
            ...currentProjects,
            project,
        ]);
    };

    if (loading) {
        return (
            <main className="flex min-h-screen items-center justify-center bg-zinc-950">
                <div className="flex items-center gap-3 text-sm text-zinc-400">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500" />
                    Loading projects...
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-zinc-950">
            {/* Header */}
            <header className="border-b border-zinc-800/80">
                <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
                    <div>
                        <div className="flex items-center gap-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 ring-1 ring-indigo-500/20">
                                <span className="font-mono text-sm font-semibold text-indigo-400">
                                    SF
                                </span>
                            </div>

                            <h1 className="text-lg font-semibold tracking-tight text-white">
                                ShipForge
                            </h1>
                        </div>

                        <p className="mt-2 text-sm text-zinc-500">
                            Developer deployment platform
                        </p>
                    </div>

                    <div className="hidden items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 sm:flex">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />

                        <span className="font-mono text-xs text-zinc-400">
                            API Online
                        </span>
                    </div>
                </div>
            </header>

            {/* Main content */}
            <div className="mx-auto max-w-6xl px-6 py-10">
                {/* Page heading */}
                <section className="mb-8">
                    <p className="mb-2 font-mono text-xs uppercase tracking-widest text-indigo-400">
                        Workspace
                    </p>

                    <h2 className="text-3xl font-semibold tracking-tight text-white">
                        Projects
                    </h2>

                    <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
                        Connect your repositories and manage your projects from one
                        place.
                    </p>
                </section>

                {error && (
                    <div className="mb-6 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
                        {error}
                    </div>
                )}

                {/* Create project */}
                <section className="mb-10">
                    <ProjectForm
                        onProjectCreated={handleProjectCreated}
                    />
                </section>

                {/* Project list */}
                <section>
                    <div className="mb-4 flex items-center justify-between">
                        <div>
                            <h3 className="text-sm font-semibold text-zinc-200">
                                Your projects
                            </h3>

                            <p className="mt-1 text-xs text-zinc-500">
                                {projects.length}{" "}
                                {projects.length === 1 ? "project" : "projects"}
                            </p>
                        </div>
                    </div>

                    <ProjectList projects={projects} />
                </section>
            </div>
        </main>
    );
}

export default ProjectsPage;