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