import { api } from "@/lib/api";

type Post = { id: number; content: string; status: string; published_at: string | null; engagement: Record<string, number> | null };

async function getPosts() {
  try { return await api.get<Post[]>("/social/posts?limit=50"); } catch { return []; }
}

export default async function SocialPage() {
  const posts = await getPosts();
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold text-white">Social Media</h1>
      <div className="space-y-3">
        {posts.length === 0 && <p className="text-gray-400">No posts yet.</p>}
        {posts.map((p) => (
          <div key={p.id} className="bg-gray-800 rounded-lg p-4">
            <p className="text-white">{p.content}</p>
            <div className="flex gap-4 mt-2 text-sm text-gray-400">
              <span className={`capitalize ${p.status === "published" ? "text-green-400" : "text-yellow-400"}`}>{p.status}</span>
              {p.published_at && <span>{new Date(p.published_at).toLocaleDateString()}</span>}
              {p.engagement && Object.entries(p.engagement).map(([k, v]) => (
                <span key={k}>{k}: {v}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
