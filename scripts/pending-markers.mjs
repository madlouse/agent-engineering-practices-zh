// A "pending" marker flags a sentence that says something is not decided yet, e.g. 〔Resend 留存：待定〕.
// Every sentence that states the open status carries the marker; history and the rules about checking do not.
// The pattern is built from parts so that this file and prose quoting the regex never match themselves.
const OPEN = "〔";
const CLOSE = "〕";
const PENDING = new RegExp(`${OPEN}([^${OPEN}${CLOSE}\\n]+)：待定${CLOSE}`, "g");

/** Returns one entry per marker found in `text`: `{ line, topic }`, lines counted from 1. */
export function findPending(text) {
  const hits = [];
  text.split("\n").forEach((content, i) => {
    for (const m of content.matchAll(PENDING)) hits.push({ line: i + 1, topic: m[1] });
  });
  return hits;
}

/**
 * Removes the markers themselves, so that a check on wording (check-vague) does not report the word inside a marker.
 * Only the bracketed marker goes: the same word outside a marker stays and is still reported. Markers never span
 * lines, so line numbers are unchanged.
 */
export function stripPending(text) {
  return text.replace(PENDING, "");
}
