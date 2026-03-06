"use client";

import { useState } from "react";
import { api, type Post } from "@/lib/api";

export default function PostComposer({
  disabled,
  onPosted,
}: {
  disabled: boolean;
  onPosted: (post: Post) => void;
}) {
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    setError("");
    setLoading(true);
    try {
      const post = await api.createPost(content.trim());
      onPosted(post);
      setContent("");
      if (post.status === "failed") {
        setError(post.error_message || "Failed to post to X");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const charCount = content.length;
  const isOverLimit = charCount > 280;

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-5">
      <label className="block text-sm font-semibold mb-3">Compose Post</label>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={
          disabled
            ? "Connect your X account first..."
            : "What's happening?"
        }
        disabled={disabled}
        rows={4}
        className="w-full px-4 py-3 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:bg-gray-50 disabled:text-gray-400"
      />
      <div className="flex items-center justify-between mt-3">
        <span
          className={`text-xs ${
            isOverLimit ? "text-red-500 font-medium" : "text-gray-400"
          }`}
        >
          {charCount}/280
        </span>
        <button
          type="submit"
          disabled={disabled || loading || !content.trim() || isOverLimit}
          className="px-5 py-2 text-sm font-semibold text-white bg-blue-500 rounded-lg hover:bg-blue-600 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? "Posting..." : "Post to X"}
        </button>
      </div>
      {error && (
        <div className="mt-3 bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
    </form>
  );
}
