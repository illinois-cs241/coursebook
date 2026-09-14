# Future concerns for review

Open items left over from the full review of the coursebook. Everything
else from that review has been fixed: PRs #234–#241 and the group 4 PR that
followed them.

The item below is a tooling follow-up that was deliberately left out of
those PRs; it needs a pandoc upgrade rather than a text change.

---

## Tooling

### Alt text is not yet delivered to readers (tracked in issue #238)
All 48 figures have `\includegraphics[alt={...}]`. The key compiles on the
CI toolchain (TeX Live 2023), but it currently reaches no reader:

- **PDF:** untagged. Tagging with `\DocumentMetadata` fails with the book's
  listings setup under TeX Live 2023.
- **EPUB and wiki:** pandoc 2.7 drops `alt=` and uses the caption as the
  alt text.

Pandoc 3.x does honour `alt=`, but it leaves figures without the key with
empty alt text, which the filters' `NoAltTagException` rejects. When pandoc
is upgraded, the filters should fall back to the figure caption. Where a
figure carried facts the text did not, a sentence of prose was added beside
it; that prose is the only part that reaches readers of every format today.
