const THEME_KEY = "fam-theme";
const LANG_KEY = "fam-lang";
const THEMES = ["auto", "light", "dark"];
const LANGS = ["zh", "en"];
export function Nav({ here }: { here: string }) {
  return (
    <nav>
      <a href="/">Home</a>
      {["/a", "/b"].map((h) => <a key={h} href={h} aria-current={h === here ? "page" : undefined}>{h}</a>)}
    </nav>
  );
}
