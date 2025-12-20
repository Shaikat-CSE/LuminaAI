import { FileData, Source } from '../types';

// API Base URL - uses environment variable or defaults to localhost
const API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_URL)
    || 'http://localhost:9000/api/v1';

export interface QueryResponse {
    answer: string;
    sources: Source[];
    ocr_text?: string;
}

export interface UploadResponse {
    file_id: string;
    filename: string;
    file_type: string;
    chunk_count: number;
    status: string;
    message: string;
}

export interface HealthResponse {
    status: string;
    version: string;
    vector_store: string;
    embedding_model: string;
    document_count: number;
}

// Upload a file to the backend
export const uploadFile = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload file');
    }

    return response.json();
};

// Query documents with a question
export const queryDocuments = async (
    question: string,
    imageBase64?: string,
    topK: number = 5
): Promise<QueryResponse> => {
    const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question,
            image_base64: imageBase64,
            top_k: topK,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to query documents');
    }

    return response.json();
};

// Clear all documents from the backend
export const clearAllDocuments = async (): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/documents`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error('Failed to clear documents');
    }
};

// Delete a specific document by file ID
export const deleteDocument = async (fileId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/documents/${fileId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error('Failed to delete document');
    }
};

// Get system health status
export const getHealth = async (): Promise<HealthResponse> => {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error('Backend is not healthy');
    }

    return response.json();
};

// Get system statistics
export const getStats = async () => {
    const response = await fetch(`${API_BASE_URL}/stats`);

    if (!response.ok) {
        throw new Error('Failed to get stats');
    }

    return response.json();
};
