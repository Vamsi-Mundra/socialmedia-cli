const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type User = {
  id: number;
  email: string;
  name: string;
  twitter_connected: boolean;
  twitter_username?: string | null;
};

export type Post = {
  id: number;
  content: string;
  tweet_id?: string | null;
  tweet_url?: string | null;
  status: string;
  error_message?: string | null;
  created_at: string;
};

export type TopicOption = {
  id: string;
  label: string;
  description: string;
};

export type TweetDraft = {
  topic: string;
  content: string;
};

async function request<T>(path: string, options: RequestInit = {}, requiresAuth = true): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (requiresAuth) {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.detail || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  signup: (payload: { email: string; name: string; password: string }) =>
    request<{ access_token: string; token_type: string; user: User }>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    }, false),

  signin: (payload: { email: string; password: string }) =>
    request<{ access_token: string; token_type: string; user: User }>("/api/auth/signin", {
      method: "POST",
      body: JSON.stringify(payload),
    }, false),

  getMe: () => request<User>("/api/auth/me"),
  connectTwitter: () => request<{ authorize_url: string }>("/api/twitter/connect"),
  disconnectTwitter: () => request<{ message: string }>("/api/twitter/disconnect", { method: "DELETE" }),
  listPosts: () => request<Post[]>("/api/posts"),
  createPost: (payload: { content?: string; topic?: string; auto_generate?: boolean }) =>
    request<Post>("/api/posts", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listTopics: () => request<TopicOption[]>("/api/posts/topics"),
  generateDraft: (topic: string) =>
    request<TweetDraft>("/api/posts/generate", {
      method: "POST",
      body: JSON.stringify({ topic }),
    }),
};
