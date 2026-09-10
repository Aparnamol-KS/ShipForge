import { Link } from "react-router-dom";

import type { Project } from "../api/projects";

interface ProjectListProps {
    projects: Project[];
}

function ProjectList({
    projects,
}: ProjectListProps) {
    if (projects.length === 0) {
        return (
            <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/20 px-6 py-12 text-center">
                <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900">
                    <span className="font-mono text-sm text-zinc-500">
                        —
                    </span>
                </div>

                <h3 className="text-sm font-medium text-zinc-300">
                    No projects yet
                </h3>

                <p className="mt-1 text-sm text-zinc-600">
                    Create your first project to get started.
                </p>
            </div>
        );
    }

    return (
        <div className="grid gap-4 md:grid-cols-2">
            {projects.map((project) => (
                <article
                    key={project.id}
                    className="group rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 transition hover:border-zinc-700 hover:bg-zinc-900/70"
                >
                    {/* Top row */}
                    <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                            <h3 className="truncate text-base font-semibold text-zinc-100">
                                {project.name}
                            </h3>

                            <p className="mt-1 font-mono text-xs text-zinc-600">
                                project_{project.id}
                            </p>
                        </div>

                        {/* Status */}
                        <div className="flex shrink-0 items-center gap-2 rounded-full border border-emerald-900/40 bg-emerald-950/30 px-2.5 py-1">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />

                            <span className="text-xs font-medium text-emerald-400">
                                Ready
                            </span>
                        </div>
                    </div>

                    {/* Description */}
                    {project.description && (
                        <p className="mt-5 line-clamp-2 text-sm leading-6 text-zinc-500">
                            {project.description}
                        </p>
                    )}

                    {/* Repository */}
                    {project.repository_url && (
                        <div className="mt-5 rounded-lg border border-zinc-800/80 bg-zinc-950/70 px-3 py-2.5">
                            <p className="mb-1 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                                Repository
                            </p>

                            <p className="truncate font-mono text-xs text-zinc-400">
                                {project.repository_url}
                            </p>
                        </div>
                    )}

                    {/* Footer */}
                    <div className="mt-5 flex items-center justify-between border-t border-zinc-800/70 pt-4">
                        <span className="font-mono text-[11px] text-zinc-600">
                            created {new Date(project.created_at).toLocaleDateString()}
                        </span>

                        <Link
                            to={`/projects/${project.id}`}
                            className="text-xs font-medium text-zinc-500 transition group-hover:text-indigo-400"
                        >
                            View project →
                        </Link>
                    </div>
                </article>
            ))}
        </div>
    );
}

export default ProjectList;