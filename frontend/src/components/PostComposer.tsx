"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type Post, type TopicOption } from "@/services/api";

export default function PostComposer({
  disabled,
  onPosted,
}: {
  disabled: boolean;
  onPosted: (post: Post) => void;
}) {
  const [content, setContent] = useState("");
  const [topic, setTopic] = useState("");
  const [topics, setTopics] = useState<TopicOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api
      .listTopics()
      .then((data) => {
        setTopics(data);
        if (data.length > 0) {
          setTopic((current) => current || data[0].id);
        }
      })
      .catch(() => {
        setTopics([]);
      });
  }, []);

  const selectedTopic = useMemo(
    () => topics.find((item) => item.id === topic) || null,
    [topics, topic],
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const post = await api.createPost({ content: content.trim() });
      onPosted(post);
      setContent("");
      setSuccess(post.status === "posted" ? "Tweet posted to your connected X account." : "The tweet was saved, but posting to X failed.");
      if (post.status === "failed") {
        setError(post.error_message || "Failed to post to X");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateDraft() {
    if (!topic) return;
    setError("");
    setSuccess("");
    setGenerating(true);
    try {
      const draft = await api.generateDraft(topic);
      setContent(draft.content);
      setSuccess("Draft generated. Review it, edit anything you want, or post it as-is.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleAutoPost() {
    if (!topic) return;
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const post = await api.createPost({ topic, auto_generate: true });
      onPosted(post);
      setContent(post.content);
      setSuccess(post.status === "posted" ? "Automatic topic-based tweet posted to your connected X account." : "The automatic tweet was generated, but posting failed.");
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
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <label className="block text-sm font-semibold">Compose or Auto-Generate</label>
          <p className="text-xs text-gray-500 mt-1">
            Pick a topic to create a tweet automatically, or write your own message and post it to your connected X account.
          </p>
        </div>
        <span className="text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
          Personal account posting
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500">
            Topic-based automation
          </label>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={disabled || topics.length === 0 || loading || generating}
            className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
          >
            {topics.length === 0 ? (
              <option value="">No topics available</option>
            ) : (
              topics.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))
            )}
          </select>
          <div className="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 min-h-24">
            <p className="text-sm font-medium text-blue-900">
              {selectedTopic?.label || "Choose a topic"}
            </p>
            <p className="text-xs text-blue-700 mt-1">
              {selectedTopic?.description || "Select a topic to generate a ready-to-post tweet automatically."}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleGenerateDraft}
              disabled={disabled || !topic || loading || generating}
              className="px-4 py-2 text-sm font-semibold text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {generating ? "Generating..." : "Generate draft"}
            </button>
            <button
              type="button"
              onClick={handleAutoPost}
              disabled={disabled || !topic || loading || generating}
              className="px-4 py-2 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? "Posting..." : "Auto-generate & post"}
            </button>
          </div>
        </div>

        <div className="space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500">
            Manual tweet editor
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={
              disabled
                ? "Connect your X account first..."
                : "Write your own tweet or generate one from a topic."
            }
            disabled={disabled || loading}
            rows={7}
            className="w-full px-4 py-3 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:bg-gray-50 disabled:text-gray-400"
          />
          <div className="flex items-center justify-between gap-3">
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
              className="px-5 py-2 text-sm font-semibold text-white bg-black rounded-lg hover:bg-gray-900 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? "Posting..." : "Post manual tweet"}
            </button>
          </div>
        </div>
      </div>

      {success && (
        <div className="bg-green-50 text-green-700 text-sm px-4 py-3 rounded-lg">
          {success}
        </div>
      )}
      {error && (
        <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
    </form>
  );
}
