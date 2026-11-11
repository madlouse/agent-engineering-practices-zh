// Finds cross-repository issue references that share one repo prefix across a list:
// 「thin-muscle-coach#185、#101」 reads as "#101 of this repo" once the list is split or copied.
// Every cross-repo number carries its own prefix: 「thin-muscle-coach#185、thin-muscle-coach#101」.
const SHARED_PREFIX = /([A-Za-z][\w.-]*(?:\/[\w.-]+)?)#\d+(?:\s*[、，,和及与]\s*#\d+)+/g;

export function findSharedPrefixRefs(line) {
  return [...line.matchAll(SHARED_PREFIX)].map((m) => m[0]);
}
