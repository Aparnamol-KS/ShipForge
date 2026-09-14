import apiClient from "./client";

export interface Project {
    id: number;
    name: string;
    description: string | null;
    repository_url: string | null;
    build_command: string | null;
    created_at: string;
    updated_at: string;
}

export interface ProjectCreate {
    name: string;
    description?: string;
    repository_url?: string;
    build_command?: string;
}

export interface ProjectUpdate {
    name?: string;
    description?: string;
    repository_url?: string;
    build_command?: string;
}

export interface Build {
    id: number;
    project_id: number;
    build_number: number;
    status: "queued" | "running" | "success" | "failed";
    created_at: string;
    started_at: string | null;
    finished_at: string | null;
}

export const getProjects = async (): Promise<Project[]> => {
    const response = await apiClient.get<Project[]>("/projects/");
    return response.data;
};

export const getProject = async (
    projectId: number,
): Promise<Project> => {
    const response = await apiClient.get<Project>(
        `/projects/${projectId}`,
    );

    return response.data;
};

export const createProject = async (
    project: ProjectCreate,
): Promise<Project> => {
    const response = await apiClient.post<Project>(
        "/projects/",
        project,
    );

    return response.data;
};

export const updateProject = async (
    projectId: number,
    project: ProjectUpdate,
): Promise<Project> => {
    const response = await apiClient.patch<Project>(
        `/projects/${projectId}`,
        project,
    );

    return response.data;
};

export const getBuilds = async (
    projectId: number,
): Promise<Build[]> => {
    const response = await apiClient.get<Build[]>(
        `/projects/${projectId}/builds/`,
    );

    return response.data;
};

export const createBuild = async (
    projectId: number,
): Promise<Build> => {
    const response = await apiClient.post<Build>(
        `/projects/${projectId}/builds/`,
    );

    return response.data;
};


export interface BuildLog {
    id: number;
    build_id: number;
    output: string;
    created_at: string;
}


export const getBuildLogs = async (
    projectId: number,
    buildId: number,
): Promise<BuildLog[]> => {
    const response = await apiClient.get<BuildLog[]>(
        `/projects/${projectId}/builds/${buildId}/logs`,
    );

    return response.data;
};