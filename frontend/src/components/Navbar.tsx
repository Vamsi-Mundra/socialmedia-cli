"use client";

import { useRouter } from "next/navigation";
import type { User } from "@/services/api";

export default function Navbar({ user }: { user: User }) {
  const router = useRouter();

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <span className="text-xl font-bold tracking-tight">
          SocialMedia<span className="text-blue-500">Web</span>
        </span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            {user.name}
          </span>
          <button
            onClick={handleLogout}
            className="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  );
}
