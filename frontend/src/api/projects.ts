import apiClient from "./client";

export interface Project {
    id: number;
    name: string;
    description: string | null;
    repository_url: string | null;
    created_at: string;
    updated_at: string;
}

export interface ProjectCreate {
    name: string;
    description?: string;
    repository_url?: string;
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