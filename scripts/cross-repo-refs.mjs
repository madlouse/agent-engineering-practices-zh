// Finds cross-repository issue references that share one repo prefix across a list:
// 「thin-muscle-coach#185、#101」 reads as "#101 of this repo" once the list is split or copied.
// Every cross-repo number carries its own prefix: 「thin-muscle-coach#185、thin-muscle-coach#101」,
// and cross-repo numbers go after this repo's own numbers in a mixed list.
//
// Two passes keep it linear in the line length: first find runs of 「#N、#M…」, then look at the
// (bounded) text right before each run for a repository name.
const NUMBER_RUN = /#\d+(?:\s*[、，,和及与]\s*#\d+)+/g;
// A repository name: 「owner/repo」, or a name of at least two characters that starts with a lowercase letter.
// A single capital before 「#」 (「A#17、#27」: a rubric item in a review report) is not a repository.
const REPO_PREFIX = /(?:[A-Za-z0-9][\w.-]*\/[\w.-]+|[a-z][\w.-]+)$/;
const PREFIX_WINDOW = 120;

export function findSharedPrefixRefs(line) {
  const out = [];
  for (const m of line.matchAll(NUMBER_RUN)) {
    const before = line.slice(Math.max(0, m.index - PREFIX_WINDOW), m.index);
    const prefix = before.match(REPO_PREFIX);
    if (prefix) out.push(prefix[0] + m[0]);
  }
  return out;
}

// Issue bodies are checked only for issues opened by the repository owner: the repo is public,
// so anyone can open an issue, and a stranger's text must not be able to fail this check.
/** An issue (not a pull request) opened by the repository owner. `author_association` is computed by GitHub and cannot be set by the author. */
export function isOwnerIssue(issue) {
  return !issue.pull_request && issue.author_association === "OWNER";
}

export function findSharedPrefixRefsInIssues(issues) {
  const hits = [];
  let checked = 0;
  for (const issue of issues) {
    if (!isOwnerIssue(issue)) continue;
    checked++;
    (issue.body ?? "").split("\n").forEach((line, i) => {
      for (const ref of findSharedPrefixRefs(line)) hits.push({ number: issue.number, line: i + 1, ref });
    });
  }
  return { checked, hits };
}
