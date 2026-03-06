"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="border-b border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <span className="text-xl font-bold tracking-tight">
            SocialMedia<span className="text-blue-500">Web</span>
          </span>
          <div className="flex gap-3">
            <Link
              href="/signin"
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-lg hover:bg-blue-600 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <main className="flex-1 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-extrabold tracking-tight mb-6">
            Post to <span className="text-blue-500">X</span> from anywhere
          </h1>
          <p className="text-xl text-gray-500 mb-10 max-w-lg mx-auto">
            Connect your X/Twitter account, compose your posts, and publish
            directly from a clean, modern interface.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/signup"
              className="px-8 py-3 text-lg font-semibold text-white bg-blue-500 rounded-xl hover:bg-blue-600 transition shadow-lg shadow-blue-200"
            >
              Create Account
            </Link>
            <Link
              href="/signin"
              className="px-8 py-3 text-lg font-semibold text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition"
            >
              Sign In
            </Link>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="text-2xl mb-3">🔗</div>
              <h3 className="font-semibold mb-2">Connect Account</h3>
              <p className="text-sm text-gray-500">
                Link your X/Twitter account securely via OAuth.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="text-2xl mb-3">✍️</div>
              <h3 className="font-semibold mb-2">Compose & Post</h3>
              <p className="text-sm text-gray-500">
                Write your posts and publish them instantly to X.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="text-2xl mb-3">📋</div>
              <h3 className="font-semibold mb-2">Track Posts</h3>
              <p className="text-sm text-gray-500">
                See your post history with direct links to each tweet.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
