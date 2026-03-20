"use client";

import { Suspense, useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, type User, type Post } from "@/services/api";
import Navbar from "@/components/Navbar";
import TwitterConnect from "@/components/TwitterConnect";
import PostComposer from "@/components/PostComposer";
import PostList from "@/components/PostList";

export default function Dashboard() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState("");

  const loadData = useCallback(async () => {
    try {
      const [userData, postsData] = await Promise.all([
        api.getMe(),
        api.listPosts(),
      ]);
      setUser(userData);
      setPosts(postsData);
    } catch {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      router.push("/signin");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/signin");
      return;
    }
    loadData();
  }, [router, loadData]);

  useEffect(() => {
    const twitter = searchParams.get("twitter");
    if (twitter === "connected") {
      setNotification("X/Twitter account connected successfully!");
      loadData();
      window.history.replaceState({}, "", "/dashboard");
      const timer = setTimeout(() => setNotification(""), 5000);
      return () => clearTimeout(timer);
    }
    if (twitter === "error") {
      setNotification("Failed to connect X/Twitter. Please try again.");
      window.history.replaceState({}, "", "/dashboard");
      const timer = setTimeout(() => setNotification(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [searchParams, loadData]);

  function handlePosted(post: Post) {
    setPosts((prev) => [post, ...prev]);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />

      {notification && (
        <div className="max-w-2xl mx-auto px-4 mt-4">
          <div
            className={`text-sm px-4 py-3 rounded-lg ${
              notification.includes("success")
                ? "bg-green-50 text-green-700"
                : "bg-yellow-50 text-yellow-700"
            }`}
          >
            {notification}
          </div>
        </div>
      )}

      <main className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        <TwitterConnect user={user} onUpdate={loadData} />
        <PostComposer
          disabled={!user.twitter_connected}
          onPosted={handlePosted}
        />
        <PostList posts={posts} />
      </main>
    </div>
  );
}
