import { danKoe } from "./dankoe";
import { engineeringPosts } from "./engineering";
import type { Post } from "./types";

export const posts: Post[] = [...engineeringPosts, danKoe];

export function getPost(slug: string): Post | undefined {
  return posts.find((post) => post.slug === slug);
}

export function neighbors(slug: string): { prev?: Post; next?: Post } {
  const index = posts.findIndex((post) => post.slug === slug);
  if (index < 0) return {};
  return {
    prev: index > 0 ? posts[index - 1] : undefined,
    next: index < posts.length - 1 ? posts[index + 1] : undefined,
  };
}
