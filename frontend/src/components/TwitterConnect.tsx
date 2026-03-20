"use client";

import { useState } from "react";
import { api, type User } from "@/services/api";

export default function TwitterConnect({
  user,
  onUpdate,
}: {
  user: User;
  onUpdate: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleConnect() {
    setError("");
    setLoading(true);
    try {
      const data = await api.connectTwitter();
      window.location.href = data.authorize_url;
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  async function handleDisconnect() {
    setError("");
    setLoading(true);
    try {
      await api.disconnectTwitter();
      onUpdate();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (user.twitter_connected) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </div>
            <div>
              <p className="font-medium text-sm">X/Twitter Connected</p>
              {user.twitter_username && (
                <p className="text-xs text-gray-500">Posting as @{user.twitter_username}</p>
              )}
            </div>
          </div>
          <button
            onClick={handleDisconnect}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition disabled:opacity-50"
          >
            Disconnect
          </button>
        </div>
        <div className="rounded-lg bg-gray-50 border border-gray-100 px-4 py-3 text-xs text-gray-600">
          This dashboard posts only to the X account that the current signed-in user connected. Any user can sign in, connect their own X account, and publish to their own profile.
        </div>
        {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="font-medium text-sm">Connect X/Twitter</p>
          <p className="text-xs text-gray-500 mt-0.5">
            Any signed-in user can link their own X account and post directly into that account.
          </p>
        </div>
        <button
          onClick={handleConnect}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-white bg-black rounded-lg hover:bg-gray-800 transition disabled:opacity-50 flex items-center gap-2"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
          {loading ? "Connecting..." : "Connect"}
        </button>
      </div>
      {error && <p className="text-xs text-red-500 mt-3">{error}</p>}
    </div>
  );
}
