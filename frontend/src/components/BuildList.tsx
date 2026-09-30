
import type { Build } from "../api/projects";

interface BuildListProps {
    builds: Build[];
    onViewLogs: (buildId: number) => void;
    onRetryBuild: (buildId: number) => void;
    onCancelBuild: (buildId: number) => void;
}


const statusStyles: Record<
    Build["status"],
    {
        dot: string;
        text: string;
        background: string;
    }
> = {
    queued: {
        dot: "bg-amber-500",
        text: "text-amber-400",
        background: "border-amber-900/40 bg-amber-950/20",
    },
    running: {
        dot: "bg-blue-500 animate-pulse",
        text: "text-blue-400",
        background: "border-blue-900/40 bg-blue-950/20",
    },
    success: {
        dot: "bg-emerald-500",
        text: "text-emerald-400",
        background: "border-emerald-900/40 bg-emerald-950/20",
    },
    failed: {
        dot: "bg-red-500",
        text: "text-red-400",
        background: "border-red-900/40 bg-red-950/20",
    },
    cancelled: {
        dot: "bg-zinc-500",
        text: "text-zinc-400",
        background: "border-zinc-700/40 bg-zinc-800/20",
    },
};

function formatDate(date: string): string {
    return new Date(date).toLocaleString();
}


function formatDuration(
    startedAt: string | null,
    finishedAt: string | null,
): string {
    if (!startedAt) {
        return "—";
    }

    const start = new Date(startedAt).getTime();

    if (!finishedAt) {
        return "Running...";
    }

    const finish = new Date(finishedAt).getTime();
    const durationSeconds = Math.max(
        0,
        Math.floor((finish - start) / 1000),
    );

    if (durationSeconds < 60) {
        return `${durationSeconds}s`;
    }

    const minutes = Math.floor(durationSeconds / 60);
    const seconds = durationSeconds % 60;

    return `${minutes}m ${seconds}s`;
}


function BuildList({
    builds,
    onViewLogs,
    onRetryBuild,
    onCancelBuild,
}: BuildListProps) {

    if (builds.length === 0) {
        return (
            <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/20 px-6 py-10 text-center">
                <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900">
                    <span className="font-mono text-sm text-zinc-500">
                        &gt;_
                    </span>
                </div>

                <h3 className="text-sm font-medium text-zinc-300">
                    No builds yet
                </h3>

                <p className="mt-1 text-sm text-zinc-600">
                    Run your first build to see its status here.
                </p>
            </div>
        );
    }

    return (
        <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/40">
            {builds.map((build, index) => {
                const style = statusStyles[build.status];

                return (
                    <div
                        key={build.id}
                        className={`flex flex-col gap-4 px-5 py-4 transition hover:bg-zinc-900/70 sm:flex-row sm:items-center sm:justify-between ${index !== builds.length - 1
                            ? "border-b border-zinc-800/70"
                            : ""
                            }`}
                    >
                        {/* Build identity */}
                        <div className="flex items-center gap-4">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-950">
                                <span className="font-mono text-xs text-zinc-500">
                                    #{build.build_number}
                                </span>
                            </div>

                            <div>
                                <p className="text-sm font-medium text-zinc-200">
                                    Build #{build.build_number}
                                </p>

                                <p className="mt-1 font-mono text-[11px] text-zinc-600">
                                    project_{build.project_id}
                                </p>

                            </div>
                            <div className="text-sm text-gray-400">
                                {build.branch && build.commit_sha ? (
                                    <>
                                        {build.branch} ·{" "}
                                        {build.commit_sha.slice(0, 7)}
                                    </>
                                ) : (
                                    "Manual build"
                                )}
                            </div>
                        </div>

                        {/* Status + date */}
                        <div className="flex items-center justify-between gap-6 sm:justify-end">
                            <div
                                className={`flex items-center gap-2 rounded-full border px-2.5 py-1 ${style.background}`}
                            >
                                <span
                                    className={`h-1.5 w-1.5 rounded-full ${style.dot}`}
                                />

                                <span
                                    className={`font-mono text-xs ${style.text}`}
                                >
                                    {build.status}
                                </span>
                                {build.status === "failed" && build.failed_stage && (
                                    <span className="text-xs text-red-400">
                                        Failed at: {build.failed_stage}
                                    </span>
                                )}
                            </div>

                            <div className="text-right">
                                <span className="block text-xs text-zinc-600">
                                    {formatDate(build.created_at)}
                                </span>
                                <span className="mt-1 block font-mono text-[11px] text-zinc-700">
                                    {formatDuration(build.started_at, build.finished_at)}
                                </span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() => onViewLogs(build.id)}
                                className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-white"
                            >
                                View logs
                            </button>

                            {build.status === "failed" && (
                                <button
                                    type="button"
                                    onClick={() => onRetryBuild(build.id)}
                                    className="rounded-lg border border-amber-800 px-3 py-1.5 text-sm text-amber-400 transition hover:border-amber-600 hover:text-amber-300"
                                >
                                    Retry
                                </button>
                            )}
                            {(build.status === "queued" || build.status === "running") && (
                                <button
                                    type="button"
                                    onClick={() => onCancelBuild(build.id)}
                                    className="rounded-lg border border-red-900/60 px-3 py-1.5 text-sm text-red-400 transition hover:border-red-700 hover:text-red-300"
                                >
                                    Cancel
                                </button>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export default BuildList;