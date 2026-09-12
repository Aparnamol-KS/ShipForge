import { useEffect, useState } from "react";

import {
    Link,
    useNavigate,
    useParams,
} from "react-router-dom";

import {
    createBuild,
    getBuilds,
    getProject,
    type Build,
    type Project,
    getBuildLogs,
    type BuildLog
} from "../api/projects";

import BuildList from "../components/BuildList";

function ProjectDetailsPage() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [project, setProject] = useState<Project | null>(
        null,
    );

    const [builds, setBuilds] = useState<Build[]>([]);

    const [loading, setLoading] = useState(true);
    const [buildsLoading, setBuildsLoading] = useState(true);
    const [creatingBuild, setCreatingBuild] = useState(false);

    const [error, setError] = useState<string | null>(null);
    const [buildError, setBuildError] = useState<string | null>(
        null,
    );
    const [selectedBuildId, setSelectedBuildId] = useState<number | null>(null);
    const [buildLogs, setBuildLogs] = useState<BuildLog[]>([]);
    const [logsLoading, setLogsLoading] = useState(false);

    useEffect(() => {
        const loadProject = async () => {
            if (!projectId) {
                setError("Project ID is missing");
                setLoading(false);
                return;
            }

            try {
                const data = await getProject(Number(projectId));

                setProject(data);
            } catch {
                setError("Project not found");
            } finally {
                setLoading(false);
            }
        };

        loadProject();
    }, [projectId]);

    useEffect(() => {
        if (!projectId) {
            return;
        }

        let cancelled = false;

        const loadBuilds = async () => {
            try {
                const data = await getBuilds(Number(projectId));

                if (!cancelled) {
                    setBuilds(data);
                    setBuildError(null);
                }
            } catch {
                if (!cancelled) {
                    setBuildError("Failed to load builds");
                }
            } finally {
                if (!cancelled) {
                    setBuildsLoading(false);
                }
            }
        };

        loadBuilds();

        const interval = window.setInterval(
            loadBuilds,
            1000,
        );

        return () => {
            cancelled = true;
            window.clearInterval(interval);
        };
    }, [projectId]);

    const handleCreateBuild = async () => {
        if (!projectId) {
            return;
        }

        setCreatingBuild(true);
        setBuildError(null);

        try {
            const build = await createBuild(Number(projectId));

            setBuilds((currentBuilds) => [
                build,
                ...currentBuilds,
            ]);
        } catch {
            setBuildError("Failed to create build");
        } finally {
            setCreatingBuild(false);
        }
    };

    const handleViewLogs = async (buildId: number) => {
        if (!projectId) {
            return;
        }

        setSelectedBuildId(buildId);
        setLogsLoading(true);

        try {
            const data = await getBuildLogs(
                Number(projectId),
                buildId,
            );

            setBuildLogs(data);
        } catch {
            setBuildLogs([]);
        } finally {
            setLogsLoading(false);
        }
    };

    if (loading) {
        return (
            <main className="flex min-h-screen items-center justify-center bg-zinc-950">
                <div className="flex items-center gap-3 text-sm text-zinc-400">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500" />

                    Loading project...
                </div>
            </main>
        );
    }

    if (error || !project) {
        return (
            <main className="min-h-screen bg-zinc-950">
                <div className="mx-auto max-w-6xl px-6 py-10">
                    <Link
                        to="/"
                        className="text-sm text-zinc-500 transition hover:text-zinc-200"
                    >
                        ← Back to projects
                    </Link>

                    <div className="mt-10 rounded-xl border border-red-900/50 bg-red-950/20 p-6">
                        <h1 className="text-base font-semibold text-red-400">
                            Project not found
                        </h1>

                        <p className="mt-2 text-sm text-red-500/70">
                            The project you're looking for doesn't exist.
                        </p>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-zinc-950">
            {/* Header */}
            <header className="border-b border-zinc-800/80">
                <div className="mx-auto max-w-6xl px-6 py-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 ring-1 ring-indigo-500/20">
                                    <span className="font-mono text-sm font-semibold text-indigo-400">
                                        SF
                                    </span>
                                </div>

                                <span className="text-lg font-semibold tracking-tight text-white">
                                    ShipForge
                                </span>
                            </div>

                            <p className="mt-2 text-sm text-zinc-500">
                                Developer deployment platform
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() => navigate("/")}
                            className="text-sm text-zinc-500 transition hover:text-zinc-200"
                        >
                            ← Projects
                        </button>
                    </div>
                </div>
            </header>

            {/* Content */}
            <div className="mx-auto max-w-6xl px-6 py-10">
                {/* Breadcrumb */}
                <div className="mb-8">
                    <Link
                        to="/"
                        className="text-sm text-zinc-500 transition hover:text-zinc-300"
                    >
                        Projects
                    </Link>

                    <span className="mx-2 text-zinc-700">
                        /
                    </span>

                    <span className="text-sm text-zinc-300">
                        {project.name}
                    </span>
                </div>

                {/* Project heading */}
                <section className="mb-8">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                            <div className="flex flex-wrap items-center gap-3">
                                <h1 className="text-3xl font-semibold tracking-tight text-white">
                                    {project.name}
                                </h1>

                                <div className="flex items-center gap-2 rounded-full border border-emerald-900/40 bg-emerald-950/30 px-2.5 py-1">
                                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />

                                    <span className="text-xs font-medium text-emerald-400">
                                        Ready
                                    </span>
                                </div>
                            </div>

                            <p className="mt-2 font-mono text-xs text-zinc-600">
                                project_{project.id}
                            </p>
                        </div>
                    </div>

                    {project.description && (
                        <p className="mt-5 max-w-2xl text-sm leading-6 text-zinc-500">
                            {project.description}
                        </p>
                    )}
                </section>

                {/* Repository */}
                <section className="mb-6">
                    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">
                        <h2 className="text-sm font-semibold text-zinc-200">
                            Repository
                        </h2>

                        {project.repository_url ? (
                            <a
                                href={project.repository_url}
                                target="_blank"
                                rel="noreferrer"
                                className="mt-4 block truncate rounded-lg border border-zinc-800 bg-zinc-950 px-4 py-3 font-mono text-sm text-indigo-400 transition hover:border-zinc-700 hover:text-indigo-300"
                            >
                                {project.repository_url}
                            </a>
                        ) : (
                            <div className="mt-4 rounded-lg border border-dashed border-zinc-800 bg-zinc-950/50 px-4 py-6 text-center">
                                <p className="text-sm text-zinc-500">
                                    No repository connected.
                                </p>

                                <p className="mt-1 text-xs text-zinc-700">
                                    GitHub integration will be available here.
                                </p>
                            </div>
                        )}
                    </div>
                </section>

                {/* Builds */}
                <section className="mb-6">
                    <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <h2 className="text-sm font-semibold text-zinc-200">
                                Builds
                            </h2>

                            <p className="mt-1 text-xs text-zinc-600">
                                Build history for this project.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={handleCreateBuild}
                            disabled={creatingBuild}
                            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {creatingBuild && (
                                <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                            )}

                            {creatingBuild
                                ? "Starting..."
                                : "Run build"}
                        </button>
                    </div>

                    {buildError && (
                        <div className="mb-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
                            {buildError}
                        </div>
                    )}

                    {buildsLoading ? (
                        <div className="rounded-xl border border-zinc-800 bg-zinc-900/30 px-6 py-10 text-center">
                            <div className="mx-auto mb-3 h-4 w-4 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500" />

                            <p className="text-sm text-zinc-500">
                                Loading builds...
                            </p>
                        </div>
                    ) : (
                            <BuildList
                                builds={builds}
                                onViewLogs={handleViewLogs}
                            />
                        
                            
                    )}
                    {selectedBuildId !== null && (
                        <div className="mt-6 rounded-xl border border-zinc-800 bg-zinc-900/50">
                            <div className="border-b border-zinc-800 px-5 py-4">
                                <h2 className="text-sm font-semibold text-zinc-200">
                                    Build #
                                    {
                                        builds.find(
                                            (build) => build.id === selectedBuildId,
                                        )?.build_number
                                    }{" "}
                                    Logs
                                </h2>
                            </div>

                            <div className="p-5">
                                {logsLoading ? (
                                    <p className="text-sm text-zinc-500">
                                        Loading logs...
                                    </p>
                                ) : buildLogs.length === 0 ? (
                                    <p className="text-sm text-zinc-500">
                                        No logs available.
                                    </p>
                                ) : (
                                    <pre className="overflow-x-auto rounded-lg bg-zinc-950 p-4 font-mono text-sm leading-6 text-zinc-300">
                                        {buildLogs
                                            .map((log) => log.output)
                                            .join("\n")}
                                    </pre>
                                )}
                            </div>
                        </div>
                    )}
                </section>

                {/* Project information */}
                <section>
                    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">
                        <h2 className="text-sm font-semibold text-zinc-200">
                            Project information
                        </h2>

                        <div className="mt-5 grid gap-5 sm:grid-cols-2">
                            <div>
                                <p className="text-xs uppercase tracking-wider text-zinc-600">
                                    Project ID
                                </p>

                                <p className="mt-2 font-mono text-sm text-zinc-400">
                                    {project.id}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs uppercase tracking-wider text-zinc-600">
                                    Created
                                </p>

                                <p className="mt-2 text-sm text-zinc-400">
                                    {new Date(
                                        project.created_at,
                                    ).toLocaleString()}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs uppercase tracking-wider text-zinc-600">
                                    Last updated
                                </p>

                                <p className="mt-2 text-sm text-zinc-400">
                                    {new Date(
                                        project.updated_at,
                                    ).toLocaleString()}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs uppercase tracking-wider text-zinc-600">
                                    Status
                                </p>

                                <p className="mt-2 font-mono text-sm text-emerald-400">
                                    ready
                                </p>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    );
}

export default ProjectDetailsPage;