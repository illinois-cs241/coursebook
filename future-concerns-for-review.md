# Future concerns for review

Items found during a full proofreading pass over every chapter that were
**deliberately not fixed**, because they need an author's judgement rather
than a copy-edit: technical claims that look wrong or outdated, garbled
sentences whose intent is unclear, structural gaps, and errors inside code
listings (where a "bug" is often the whole point of the example).

The language fixes from the same pass are in the accompanying commit. This
file is the leftovers.

## How to read this

- Items are grouped by chapter and carry `file:line` references. Line
  numbers refer to the commit this file was added in.
- **These findings are unverified unless marked otherwise.** They were
  produced by an automated pass and will contain false positives. Confirm
  before acting, especially on technical claims.
- Items that have since been fixed (PRs #234-#240 and the batch that
  followed them) have been removed, so line numbers may have drifted.
  Locate items by their quoted text. What remains needs an author's
  decision or new content.

---

## Figures

### Alt text — mechanism
`\includegraphics[alt={...}]` compiles on the CI toolchain (TeX Live 2023)
but is currently discarded everywhere: the PDF is untagged, and pandoc 2.7
(EPUB/wiki) uses the caption as alt and drops `alt=`. PDF tagging
(`\DocumentMetadata`) fails with the book's listings setup under TL2023.
Pandoc 3.x does honour `alt=`, but then figures without it get empty alt,
which the EPUB filters' `NoAltTagException` rejects, so the filters should
fall back to the caption when pandoc is upgraded (tracked in issue #238).
Alt text has been added
to all 48 figures,
plus a sentence of prose wherever a figure carried facts the text did not;
that prose is the only part that reaches readers of every format today.

---

## processes

### processes/processes.tex:142 vs 127 — two different definitions of "program break"
Line 127 says the program break is the top of the heap ("\keyword{malloc} may push the heap boundary --
called the program break -- upward"); line 142 says "The end of the data segment is called the
\keyword{program break}". Both are defensible historically, but stating both without comment will
confuse students.

### processes/processes.tex:977 — question is cut off mid-sentence
"What is the difference between execs with a p and without a p? What does the operating system" — the
second question has no verb, object, or terminal punctuation. I cannot guess the intended completion.

---

## malloc

### malloc/malloc.tex:83 — "these limitations" has no antecedent
"An advanced discussion of these limitations is \href{...}{in this article}." The preceding sentence describes what `calloc` does; no limitations have been mentioned yet. A student cannot tell what limitations are meant. Also the linked host (locklessinc.com) may be dead — worth checking.

### malloc/malloc.tex:290 — Fibonacci heaps claim
"Your heap could be represented with the max-heap data structure ... Using Fibonacci heaps, however, could be extremely inefficient." Fibonacci heaps have excellent amortized bounds; the claim as written is surprising and unexplained (presumably about constant factors / pointer overhead / cache behavior). Either justify or drop.

### malloc/malloc.tex:430-432 — broken quotation
The `quote` block ends: "...a multiple of 16 on 64-bit systems." For example, if you need to calculate how many 16 byte units are required, don't forget to round up." There is a stray closing double-quote mid-block, and the "For example..." sentence is the book's own commentary sitting inside the glibc quotation. Also the quoted text is self-contradictory ("always a multiple of eight on most systems"). Fixing requires deciding where the quotation actually ends, and possibly re-checking the glibc manual wording.

---

## synchronization

### Structural: "Sketch #1" is never analysed; text jumps to Sketch #2

`synchronization/synchronization.tex:855-877` — the listing is labelled `// Sketch #1` and is syntactically broken (a `push` nested inside `pop`, unbalanced braces), and the very next paragraph starts "Sketch \#2 has implemented the \keyword{post} too early." Sketch #1 is never discussed. Reads like a missing paragraph.

---

## deadlock

### deadlock/deadlock.tex:79 — "necessary *and* sufficient conditions ... non-zero probability"
"There are four \emph{necessary} and \emph{sufficient} conditions for deadlock -- meaning if these conditions hold then there is a non-zero probability that the system will deadlock at any given iteration." Sufficiency normally means deadlock *does* occur, not that it *may* occur with non-zero probability; the gloss contradicts the term. The Coffman conditions are standardly stated as necessary (and sufficient only for single-instance resources). Needs an author decision, not a copy-edit.

### deadlock/deadlock.tex:111 — garbled definition of the state functions
"$h_t: R \rightarrow P \cup \{\text{unassigned}\}$ that maps resources to the processes that own them (this is a function, meaning that we have mutual exclusion) and or unassigned and $w_t: ...$". The stray "and or unassigned and" makes the sentence unparseable. Rewriting it means deciding what the author meant, so I left it.

### deadlock/deadlock.tex:114 — "The evolution of the system is at each step at every time."
Not a sentence, and it introduces the bulleted transition rules. Probably intended something like "At each time step the system evolves as follows:". Needs an author's intent.

### deadlock/deadlock.tex:123-129 — proof of the reverse direction
Line 124 begins "More formally, this system is deadlocked means if $\exists t_0, ...$" (missing a word/"that"), and line 129 claims "Hold and wait simply proves the condition that from this point onward, the system will not change, which is all the conditions that we needed to show." The logic of what is assumed versus proved is hard to follow, and line 107 says "let us build a system with the three requirements not including circular wait" while the argument then uses circular wait (lines 127-128). This is a substantive correctness question about the proof, not a wording issue.

### deadlock/deadlock.tex:145 — "philosopher" appears before the Dining Philosophers section
The livelock paragraph continues the pen-and-paper students example but says "if the philosopher picks up the same device again and again". Dining Philosophers is not introduced until section 4 (line 181). A student reading linearly has no referent yet.

### deadlock/deadlock.tex:148 — "You must formally prove in a system by what is known as an invariant."
Missing an object ("prove *what*?"). Likely "You must formally prove freedom from livelock in a system by ...". Author's meaning needed.

### deadlock/deadlock.tex:188 — claim about the original problem
"The original problem required each philosopher to have two forks, but one can eat with a single fork so we rule this out." The reasoning is unclear (the problem is defined with two utensils precisely to create contention), and it sits oddly beside the chopstick framing on lines 185-187. A human should decide whether to keep, reword, or drop it.

### deadlock/deadlock.tex:221 — "This looks good but."
Reads as a truncated sentence. It may be a deliberate deadpan joke (the chapter is informal elsewhere), so I left it rather than adding "...". Flagging for the author to confirm.

### deadlock/deadlock.tex:299 — "with only one philosopher acting in pickup the left then the right fork"
Ungrammatical inside a proof; the intended sense is probably "acting under the pick-up-left-then-right rule". Since it is proof text, I left the wording to the author.

### deadlock/deadlock.tex:378-383 — Dijkstra proof reduction
Line 378 "If the last philosopher $p_{n-1}$ holds the first lock meaning the previous philosopher $p_{n-2}$ is waiting on $r_{n-1}$ meaning $r_{n-2}$ is available" is a run-on with no main verb, and line 380 concludes "we now have $n$ resources but only $n-1$ philosophers" without stating which philosopher was removed. Also line 379 uses "her" while the rest of the passage uses "he/his". The substance of the reduction needs an author's check.

---

## ipc

### ipc/ipc.tex:184 — Multi-level page table size arithmetic is confusing/possibly wrong
> "shrunk from 4MiB for the single-level implementation to three page tables of memory or 2KiB for the top-level and 4KiB for the two intermediate levels of size 10KiB."

Ungrammatical and technically muddled: it says "two intermediate levels" when the surrounding text (line 186-188) describes two *sub-tables*, and "4KiB for the two intermediate levels" reads as 4KiB total while 2+4+4=10KiB implies 4KiB each. A human should restate this sentence.

### ipc/ipc.tex:955,980 — "this"/"That quirk" with no antecedent
Section "Determining File Length" opens "using fseek and ftell is a simple way to accomplish this" (no prior referent), and section "Use stat instead" opens "This only works on some architectures and compilers. That quirk is that longs only need to be 4 Bytes big" — the quirk is named only after it is referred to. Reads as if an introductory sentence was lost.

---

## scheduling

### Cross-reference to "the appendix and the section conceptually scheduling" is informal/unverifiable
`scheduling/scheduling.tex:331`

> \textbf{If you need a math-y way of comparing scheduling algorithms, please check out the appendix and the section conceptually scheduling}

There is no `\ref`/`\label` here, and "the section conceptually scheduling" does not read like an actual section title. A human should confirm the target exists and ideally replace this with a real `\ref{}`. The sentence also has no terminal period, but I left it since the whole line may be rewritten.

---

## networking

### HTTP version/RFC currency — networking/networking.tex:574

"RFC 7231 has the most current specifications on the most common HTTP method today". RFC 7231 was obsoleted by RFC 9110 (HTTP Semantics, 2022), and the chapter's examples are all HTTP/1.0 while HTTP/1.1 and HTTP/2/3 dominate. A human should decide how much to update. Also line 553, "the HTTP/1.0 method" should probably be "protocol"/"version".

---

## filesystems

### "three times as slow" claim for indirection — filesystems.tex:226

> "This is three times as slow for reading between blocks, due to increased levels of indirection."

Unclear what the baseline is (three times slower than a direct block? than a single indirect block?), and the factor is asserted without justification. Ambiguous enough to need an author.

### RAID-10 description is hard to follow — filesystems.tex:1101-1105

> "This means you would get roughly the same speed from the slowdowns but now any one disk can fail and you can recover that disk."

"the same speed from the slowdowns" is not parseable, and the redundancy claim needs care: in RAID-10 any single disk can fail, and *some* two-disk failures are survivable while a mirror pair failing is not. Technical, so left alone.

### RAID-3 bottleneck reasoning — filesystems.tex:1114-1115

> "This means that there is effectively a bottleneck in a separate disk. In practice, this is more likely to cause a failure because one disk is being used 100\% of the time and once that disk fails then the other disks are more prone to failure."

"a bottleneck in a separate disk" is confusing (the bottleneck *is* the dedicated parity disk), and "once that disk fails then the other disks are more prone to failure" is a non-obvious causal claim that needs justification or removal.

### Write-to-file walkthrough mixes up inodes, data blocks, and indices — filesystems.tex:1253-1256

> "For this particular example we would have to go to the 2nd or indexed number 1 inode to perform our write."

This should almost certainly be the 2nd *data block* (the inode is a single object here), and the next sentence then says "go to the $5$th data block", which does not obviously follow from "2nd". Since the whole passage depends on the figure at filesystems.tex:1176, an author who can see the figure should reconcile the numbering.

---

## review

### review/review.tex:135 — truncated bonus question
The item ends: "Bonus: How would you make this code more robust or able to cope with?" The sentence is cut off ("cope with" what — a long `mesg`? a `malloc` failure?). The same sentence also says "val as a double val", which looks like a duplicated word but might be intentional shorthand. Both need an author who knows the intended question; rewriting could change what is being asked.

### review/review.tex:322-337 — two items describe one problem, and item 2 has no question
Item at 322 sets up the graph/`shortest`/`set_edge` scenario and ends at line 335 with a requirement statement but no explicit question ("For performance, multiple threads must be able to call \keyword{shortest} at the same time..."). The next `\item` (337) then asks for the reader-writer implementation of the same scenario. These probably should be one item, or item 1 needs an actual question sentence.

---

## appendix

### appendix/appendix.tex:442 — truncated sentence

> "Also, the messages now encounter additional overhead for serializing and deserializing or at the least."

The sentence ends mid-thought ("or at the least" what?). Needs the author to supply the missing clause.

### appendix/appendix.tex:639 — stray one-word paragraph "Yes"

Section `\subsection{Implementing Software Mutex}` opens with a bare line reading `Yes` before "With a bit of searching, it is possible to find it in production...". This looks like the answer to a question that was deleted (probably "Is Peterson's algorithm ever used in practice?"). The paragraph also has an unexplained "it". A human should restore the missing question or delete the line.

### appendix/appendix.tex:1126 vs 1317 — inconsistent symbol for maximum run time

Line 1126 says "Let the maximum amount of time that a process runs be equal to $S$", but line 1317 says "$T$ is the maximum amount of time a process can run for". Meanwhile $S$ is used throughout as the *service time* random variable. A student following the derivations would be confused; needs the author to pick one symbol.

### appendix/appendix.tex:1461 — orphan fragment in the routing list

> "These protocols are meant to be fast and more trusting because all computers, switches, and routers are part of an ISP.
> communication between two routers."

The last line is a lowercase sentence fragment with no context — apparently a leftover from an edit. Needs the author to restore or delete.

---

