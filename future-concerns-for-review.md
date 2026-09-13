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
- Items that have since been fixed (PR #235 and the Tier 2 PR that
  followed it) have been removed, so line numbers may have drifted.
  Locate items by their quoted text.

---

## Figures

### Alt text — mechanism
`\includegraphics[alt={...}]` compiles on the CI toolchain (TeX Live 2023)
but is currently discarded everywhere: the PDF is untagged, and pandoc 2.7
(EPUB/wiki) uses the caption as alt and drops `alt=`. PDF tagging
(`\DocumentMetadata`) fails with the book's listings setup under TL2023.
Pandoc 3.x does honour `alt=`, but then figures without it get empty alt,
which the EPUB filters' `NoAltTagException` rejects, so the filters should
fall back to the caption when pandoc is upgraded. Alt text has been added
to all 48 figures,
plus a sentence of prose wherever a figure carried facts the text did not;
that prose is the only part that reaches readers of every format today.

---

## introduction

### introduction/introduction.tex:6 — dangling pronoun "It"

> "It is a message etched into our Alma Mater and makes up the DNA of our course staff."

The preceding sentence's subject is "we", not a message, so "It" has no clear antecedent — the intended referent is presumably the *belief* stated in line 5. Rewriting requires knowing the author's intent, so flagging rather than changing.

### introduction/introduction.tex:14 — possibly stale staff URL

> \href{http://cs341.cs.illinois.edu/staff}{CS 341 course staff}

Plain `http` (not `https`) and a course-site path that may have moved between semesters. A human should confirm the link still resolves.

### introduction/introduction.tex:17 — vague link text

> "This work is based on the original coursebook located \href{...}{at this url}."

I removed a duplicated "at" ("located at ... at this url"). The remaining link text "at this url" is still non-descriptive, which is an accessibility concern for screen readers; naming the target (e.g. the original SystemProgramming wiki) would be better, but that is a wording change, so left to a human.

### introduction/introduction.tex:20 — reference to "the duck"

> "Oh and the duck? Keep reading until synchronization :)."

Depends on a duck image/joke appearing in the synchronization chapter. Worth a human check that the referenced content still exists in the current build; there is no `\ref{}` tying the two together.

### introduction/introduction.tex:28 — AUTHORS.md included as a code listing

> \lstinputlisting[language=console]{AUTHORS.md}

The Authors section renders a markdown file in a monospaced listing environment. If AUTHORS.md is missing or moves, the build breaks silently in terms of content; also renders prose as code, which is an accessibility/presentation concern. Human decision.

---

## background

### Broken logic in the git-status troubleshooting flow — background/background.tex:168-201

"If you are currently on a branch, and you don't see either \<A\> or \<B\>" ... then line 193 continues "And something like \<C\>". The condition never resolves grammatically or logically: is the trigger *not* seeing A/B, or *seeing* C? As written a student can't tell what state means "don't panic, but your repository may be in an unworkable state". Needs an author rewrite.

### Generic Edstem link — background/background.tex:847-848

> "Use the current semester's CS341 Edstem: \url{https://edstem.org/}"

Left exactly as-is per instructions; noting only that it points at the site root rather than a course, which may be intentional.

### Inconsistent list-introduction punctuation — throughout

Several sentences that introduce an enumerate/lstlisting end without a period (e.g. lines 55, 126, 156, 207, 512, 972). This is consistent enough across the chapter to read as house style, so I left all of them alone rather than making a large punctuation-only diff.

---

## introc

### introc/language_facilities.tex:369 — ungrammatical struct definition
"C-structs are contiguous regions of memory that one can access specific elements of each memory as if they were separate variables."
The relative clause is broken; needs rewriting by someone who knows the intended sentence.

### introc/language_facilities.tex:497-498 — `void` / lvalue claim
"The other use of \keyword{void} is when you are defining an \keyword{lvalue}." and "it can be promoted to any time to any other type."
"any time" appears to be a typo for "any type", but the whole sentence (void* and lvalues) is technically confused, so I did not guess. Also "Pointer arithmetic with this pointer is undefined behavior" contradicts pointers.tex:147-148 which says gcc/clang permit it as a char*.

### introc/common_c_functions.tex:12 — broken sentence
"know that most functions in C handle errors return oriented."
Probably "handle errors in a return-oriented way". Needs an author's wording.

### introc/common_c_functions.tex:317 — broken sentence
"The caller has to be careful from a valid 0 and an error."
Presumably "has to distinguish a valid 0 from an error."

### introc/common_c_functions.tex:341 — dangling fragment
"\keyword{memcpy} and \keyword{memmove} both in \keyword{string.h}?"
This is not a sentence and the itemize ends on it. Possibly a leftover note ("Why are memcpy and memmove both in string.h?").

### introc/c_memory_model.tex:66-98 — figures have no alt text
The three \includegraphics figures (memory_model_empty.eps, memory_model_length.eps, memory_model_full.eps) rely on captions only. The captions are descriptive, but there is no alt-text mechanism for screen readers.

### introc/pointers.tex:94 — confusing sentence
"In addition to adding to an integer, pointers can be added to."
Presumably "In addition to being able to add integers to integers, you can add an integer to a pointer." As written it is close to meaningless.

### introc/crash_course_introduction_to_c.tex:29 — flushing claim
"If the newline isn't included, the buffer will not be flushed (i.e. the write will not complete immediately)." True only for a line-buffered stdout, and the buffer is still flushed at exit. common_c_functions.tex:99-101 states the nuanced version; this simplified claim may mislead.

### introc/crash_course_introduction_to_c.tex:112 — missing word
"taking the sizeof the pointer and dividing it by the size of the first entry" — reads as if a word is missing ("the size of the pointer"). I left it because `sizeof` is being used as an operator name and a fix could change the technical reading.

---

## processes

### processes/processes.tex:142 — "starts at ... and starts at a constant size"
"This section starts at the end of the text segment and starts at a constant size because the number of
globals is known at compile time." The second "starts at" reads like it should be "stays at" / "has a
constant size", but since this is a statement about segment layout I did not want to alter the meaning.
(Compare line 163, which says the BSS "is also static in size".)

### processes/processes.tex:142 vs 127 — two different definitions of "program break"
Line 127 says the program break is the top of the heap ("\keyword{malloc} may push the heap boundary --
called the program break -- upward"); line 142 says "The end of the data segment is called the
\keyword{program break}". Both are defensible historically, but stating both without comment will
confuse students.

### processes/processes.tex:977 — question is cut off mid-sentence
"What is the difference between execs with a p and without a p? What does the operating system" — the
second question has no verb, object, or terminal punctuation. I cannot guess the intended completion.

### processes/processes.tex:683-692 — person shifts between "your" and "its"
"It is good practice to wait on your process' children. If a parent doesn't wait on your children they
become ... If a long-running parent never waits for your children ... Having said that, a program doesn't
always need to wait for your children! Your parent process can continue ..." The second-person "your"
is attached to the parent process rather than the reader, which reads as an error, but fixing it means
rewriting most of the paragraph, so I left it.

### processes/processes.tex:10 — dangling comparison
"most systems that we'll be studying are almost POSIX compatible due more to political reasons." "due
more to" invites a "than ..." that never arrives, and the claim itself (political reasons) is asserted
with no context a student could use.

### processes/processes.tex:185,340,881 — figures have captions but no alt text
`\includegraphics` of `address_space.eps`, `sleepsort_timing.eps`, and `fork_exec_wait.eps` carry only
`\caption{}`. For an accessible PDF these need real alternative descriptions (the sleepsort timing
diagram in particular carries information not present in its caption).

---

## malloc

### malloc/malloc.tex:9 — "use as its accord"
"a contiguous series of addresses that the program can expand or contract and use as its accord". "as its accord" is not an English idiom; likely intended "as it sees fit" or "at its discretion". Needs an author decision on intended meaning rather than a guess.

### malloc/malloc.tex:83 — "these limitations" has no antecedent
"An advanced discussion of these limitations is \href{...}{in this article}." The preceding sentence describes what `calloc` does; no limitations have been mentioned yet. A student cannot tell what limitations are meant. Also the linked host (locklessinc.com) may be dead — worth checking.

### malloc/malloc.tex:211 vs figure caption — "perfect-fit" vs "Best fit"
Prose says "A perfect-fit strategy finds the smallest hole"; the figure caption immediately below says "Best fit finds an exact match", and the rest of the chapter (and the Topics list) uses "Best Fit". Terminology inconsistency that could confuse a student; renaming is an editorial call.

### malloc/malloc.tex:290 — Fibonacci heaps claim
"Your heap could be represented with the max-heap data structure ... Using Fibonacci heaps, however, could be extremely inefficient." Fibonacci heaps have excellent amortized bounds; the claim as written is surprising and unexplained (presumably about constant factors / pointer overhead / cache behavior). Either justify or drop.

### malloc/malloc.tex:430-432 — broken quotation
The `quote` block ends: "...a multiple of 16 on 64-bit systems." For example, if you need to calculate how many 16 byte units are required, don't forget to round up." There is a stray closing double-quote mid-block, and the "For example..." sentence is the book's own commentary sitting inside the glibc quotation. Also the quoted text is self-contradictory ("always a multiple of eight on most systems"). Fixing requires deciding where the quotation actually ends, and possibly re-checking the glibc manual wording.

### malloc/malloc.tex:487 — incomplete sentence
"No more than 3 blocks will need to coalesce into a single block, and using a most recently used block scheme only one linked list entry." The second clause has no verb (presumably "...only one linked list entry needs to be updated"). Repairing it requires knowing the intended claim, so flagged rather than guessed.

### Figures — no alt text
All figures (lines ~199-235, 306-319, 410-414, 475-479, 512-516, 530-534) use `\includegraphics` with a `\caption` only. The captions ("Malloc addition", "Free list good and bad coalesce") do not describe what the diagram shows, so a student using a screen reader or reading the text alone gets nothing. Accessibility improvement needs an author who knows the drawings.

---

## threads

### threads/threads.tex:205 — sentence fragment / duplicated "means"

```
This means that the execution of the code is non-deterministic.
Meaning that the same program can run multiple times and depending on how the kernel schedules the threads could produce inaccurate results.
```

The second sentence is a fragment and repeats "means"; it also needs commas around the "depending on..." clause. Rewriting it is more than a mechanical fix.

### threads/threads.tex:230-231 — confusing register description

```
We will assume that data is stored in the \keyword{eax} register.
The code to increment is the following with no optimization (assume int\_ptr contains eax).
```

"assume int_ptr contains eax" reverses the relationship, and the following assembly actually loads from `[rbp-4]`, not from a register holding `data`. Also the operation is a doubling, described as "increment". Needs an author's eye.

### threads/threads.tex:304 — description of the cast is inaccurate

```
We will instead treat i as a pointer and cast it by value.
```

The code passes the *value* of `i` cast to `void *`; "treat i as a pointer" is backwards, and "cast it by value" is not standard terminology. (The listing itself also uses `int data = ((int) ptr);`, which is implementation-defined on LP64 and normally warns.)

### threads/threads.tex:3 — epigraph

```
\epigraph{If you think your programs were crashing before, wait until they crash ten times as fast}{}
```

I inserted the missing verb ("programs crashing" -> "programs were crashing"). The original may have been intended as "your program's crashing"; flagging in case the author prefers that reading. No terminal punctuation, left as-is (epigraph style).

### threads/threads.tex:551 — awkward question

```
What are a few things that threads share in a process? What are a few things that threads have different?
```

"have different" is ungrammatical but the intended phrasing ("that differ between threads"?) is a judgement call, so left alone.

---

## synchronization

### Mutex description may be misleading

`synchronization/synchronization.tex:235-236` — "If a mutex is locked, the other threads will continue. It's only when a thread attempts to lock a mutex that is already locked, will the thread have to wait." The second sentence is ungrammatical (a mixed "It is only when… that…" / "Only when… will…" construction). Rewording touches a technical claim, so I left it.

### Confusing mutual-exclusion justification

`synchronization/synchronization.tex:404-405` — "How does this guarantee mutual exclusion? When working with atomics we are unsure! But in this simple example, we can because the thread that can successfully expect the lock to be UNLOCKED (0) and swap it…". The sentence has no clear main clause ("we can" what?) and "successfully expect" is odd. Technical passage, left alone.

### Semaphore-vs-mutex passage looks logically inverted

`synchronization/synchronization.tex:472` — "That is usually why a mutex is used to implement a semaphore and vice versa." reads as a non-sequitur after the warning about breaking the mutex abstraction. (The related line 527 claim about unlocking a mutex from another thread has been fixed.)

### Run-on sentence spanning a technical claim

`synchronization/synchronization.tex:531` — "\keyword{sem\_post} is one of a handful of functions that can be correctly used inside a signal handler \keyword{pthread\_mutex\_unlock} is not." Two sentences fused with no punctuation. I did not insert punctuation because the fix (semicolon vs. period vs. "whereas") changes emphasis on an async-signal-safety claim; a one-character insert is easy for the author.

### Structural: "Sketch #1" is never analysed; text jumps to Sketch #2

`synchronization/synchronization.tex:855-877` — the listing is labelled `// Sketch #1` and is syntactically broken (a `push` nested inside `pop`, unbalanced braces), and the very next paragraph starts "Sketch \#2 has implemented the \keyword{post} too early." Sketch #1 is never discussed. Reads like a missing paragraph.

### Bounded-wait definition is awkward

`synchronization/synchronization.tex:1034` — "A thread/process cannot get superseded by another thread infinite amounts of time." Probably "an infinite number of times". Left because the fix is a judgement call on the intended definition.

### Garbled question

`synchronization/synchronization.tex:2267` — "How might the above be a producer consumer problem be used in the above section?" Doubled "be" and duplicated "the above"; the intended question is unclear.

### Possibly incomplete question prompt

`synchronization/synchronization.tex:2357` — "Remember in addition to mutual exclusion, a mutex can only ever be unlocked by the thread who called it." "the thread who called it" is missing what was called (presumably "the thread that locked it").

### Figure without alt text

`synchronization/synchronization.tex:1792-1795` — `\includegraphics{synchronization/drawings/ring_buffer.eps}` with only `\caption{Ring Buffer Visualization}`. No descriptive alternative text for a figure carrying real content (index wrap-around). Accessibility.

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

### deadlock/deadlock.tex:24-29, 68-72, 191-195, 227-231, 268-272, 303-307, 345-349, 387-391 — figures have no alt text
Eight `\includegraphics` calls, none with alt text; several carry load-bearing content (the deadlock cycle, the livelock time evolution, the arbitrator diagram). Only three of the eight are referenced from the prose at all (`ragfigure` is the sole `\label`), so a reader relying on a screen reader loses the content entirely. Needs an accessibility decision at the book level.

---

## ipc

### ipc/ipc.tex:184 — Multi-level page table size arithmetic is confusing/possibly wrong
> "shrunk from 4MiB for the single-level implementation to three page tables of memory or 2KiB for the top-level and 4KiB for the two intermediate levels of size 10KiB."

Ungrammatical and technically muddled: it says "two intermediate levels" when the surrounding text (line 186-188) describes two *sub-tables*, and "4KiB for the two intermediate levels" reads as 4KiB total while 2+4+4=10KiB implies 4KiB each. A human should restate this sentence.

### ipc/ipc.tex:217 — "read and write" in MMU pseudocode
> "get the physical frame from the TLB and perform the read and write."

Should presumably be "the read or write" (a single access is either). Left alone as it is inside the algorithm description.

### ipc/ipc.tex:223 — Broken pseudocode step
> "If so then do the dereference provide the address, cache the results in the TLB"

Run-on with words apparently missing ("provide the address" is unattached) and no terminal punctuation. Intent unclear, needs an author.

### ipc/ipc.tex:248 — Sentence ends with a dangling verb
> "it all depends on if your hardware says that a program can access."

"can access" has no object (access what — that page?). Needs an author to complete.

### ipc/ipc.tex:645 — "your special byte" mixes person
> "a program could write your special byte (e.g.~0xff)"

Probably "a special byte". Left as-is since the chapter deliberately mixes second person elsewhere.

### ipc/ipc.tex:955,980 — "this"/"That quirk" with no antecedent
Section "Determining File Length" opens "using fseek and ftell is a simple way to accomplish this" (no prior referent), and section "Use stat instead" opens "This only works on some architectures and compilers. That quirk is that longs only need to be 4 Bytes big" — the quirk is named only after it is referred to. Reads as if an introductory sentence was lost.

### ipc/ipc.tex — Figures have no alt text
All figures (lines 72-76, 95-99, 104-108, 112-116, 143-147, 161-165, 169-173, 506-510) carry only short `\caption{}` text such as "Splitting Address" and "One level dereference". For an accessible PDF these diagrams — which carry the core address-translation explanation — need real descriptions.

---

## scheduling

### "Unless otherwise stated" is a dangling fragment
`scheduling/scheduling.tex:134`

The line introducing the shared example process list is just `Unless otherwise stated` with no verb and no terminal punctuation. Presumably intended as something like "Unless otherwise stated, the following processes are used in each example:". I did not guess at the intended wording.

### Cross-reference to "the appendix and the section conceptually scheduling" is informal/unverifiable
`scheduling/scheduling.tex:331`

> \textbf{If you need a math-y way of comparing scheduling algorithms, please check out the appendix and the section conceptually scheduling}

There is no `\ref`/`\label` here, and "the section conceptually scheduling" does not read like an actual section title. A human should confirm the target exists and ideally replace this with a real `\ref{}`. The sentence also has no terminal period, but I left it since the whole line may be rewritten.

### Stray capitalization "Convoy Behind them"
`scheduling/scheduling.tex:120`

> ...leaving all other processes with potentially smaller resource needs following like a Convoy Behind them.

"Behind" is capitalized mid-sentence for no apparent reason. It may be deliberate emphasis in this book's informal voice, so I left it. Also note "Convoy effect" (line 260) vs "Convoy Effect" (line 57) vs "convoy effect" (lines 118, 120, 262, 354) are inconsistently capitalized throughout.

### Figures have captions but no alt text
`scheduling/scheduling.tex:146-150, 193-197, 237-241, 287-291`

All four `\includegraphics` calls (sjf.eps, psjf.eps, fcfs.eps, rr.eps) carry only short captions such as "Shortest job first scheduling". The Gantt-chart content — arrival times, ordering, and the resulting timeline — exists only in the image, so a student using a screen reader gets none of it. Worth adding descriptive alt text or an in-text summary of each chart.

### "with a high priority" where "higher" is likely meant
`scheduling/scheduling.tex:66`

> Thus once a process is scheduled it will continue even if another process with a high priority appears on the ready queue.

The point being made is about a process of *higher* priority than the running one. Reads as a wording slip rather than a plain grammar error, so I left it for a human.

---

## networking

### Garbled IPv4 address-splitting sentence — networking/networking.tex:70

"Conceptually the source and destination addresses can be split into two: a network number the upper bits and lower bits represent a particular host number on that network." The sentence has no working structure and a student cannot extract the network/host split from it. Rewriting requires deciding what was meant, so I left it.

### Confusing IPv6 address-notation description — networking/networking.tex:74-75

"We write IPv6 addresses in a sequence of eight, four hexadecimal delimiters like \"1F45:0000:...\"". "eight, four hexadecimal delimiters" is not meaningful — presumably "eight groups of four hexadecimal digits". Also "Since that can get unruly, we can omit the zeros \"1F45::\"" understates the `::`-may-appear-once rule. Technical wording, so left for a human.

### "Ports" bullet says socket where it means port — networking/networking.tex:252-253

"TCP gives the programmer a set of virtual sockets. Clients specify the socket that you want the packet sent to". The concept being introduced is the *port*; calling it a socket here conflicts with the socket API introduced later and will confuse students.

### "High performance and error-prone code won't even assume that!" — networking/networking.tex:244

Unclear as written — presumably means high-performance / error-tolerant code should not assume delivery. As phrased ("error-prone code") it reads as praising buggy code. Needs an author decision.

### Garbled HTTP body description — networking/networking.tex:557

"The actual body of the request delimited by two new lines. The body of the request is either if the size is specified or until the receiver closes their connection." The second sentence is missing its predicate ("either read until the specified length..."). Needs an author rewrite.

### HTTP version/RFC currency — networking/networking.tex:574

"RFC 7231 has the most current specifications on the most common HTTP method today". RFC 7231 was obsoleted by RFC 9110 (HTTP Semantics, 2022), and the chapter's examples are all HTTP/1.0 while HTTP/1.1 and HTTP/2/3 dominate. A human should decide how much to update. Also line 553, "the HTTP/1.0 method" should probably be "protocol"/"version".

### "There are a variety of function calls available to send UDP sockets" — networking/networking.tex:902

You send *packets*, not sockets. Likely "to send data over UDP sockets". I could not fix it without guessing the intent.

### Garbled UDP-vs-TCP efficiency sentence — networking/networking.tex:825

"TCP has \textit{decades} of optimization, meaning your protocol for its use cases needs to be more efficient that to be more beneficial to use it." Not parseable; needs an author rewrite (also contains a then/than-adjacent "that").

### Server stub sentence missing a word — networking/networking.tex:1361

"unmarshal the request into a valid in-memory data call the underlying implementation and send the result back". Probably "into a valid in-memory representation, call the underlying implementation, and send...". Comma/word insertion needs the author's intent.

### Interface-Description-Language sentence loses its subject — networking/networking.tex:1372

"Writing stub code by hand is painful, tedious, error-prone, difficult to maintain and difficult to reverse engineer the wire protocol from the implemented code." The final clause does not attach to the list.

### Comma splice left as-is — networking/networking.tex:1319

"To marshal a linked list, it is unnecessary to send the link pointers, stream the values." Reads as a splice; the fix ("instead, stream the values") is a wording choice so I left it.

### Figures have no alt text — networking/networking.tex:88-92, 236-240

Both `\includegraphics` figures (`ipv6_datagram.eps`, `tcp_header.eps`) carry only captions ("IPv6 Datagram divisibility", "Extra: TCP Header Specification") and no textual description. The IPv6 caption in particular does not explain what the diagram shows. Accessibility issue for screen-reader users.

---

## filesystems

### "three times as slow" claim for indirection — filesystems.tex:226

> "This is three times as slow for reading between blocks, due to increased levels of indirection."

Unclear what the baseline is (three times slower than a direct block? than a single indirect block?), and the factor is asserted without justification. Ambiguous enough to need an author.

### Sentence fragment in the Google disk-failure statistics — filesystems.tex:1142

> "Multiplying that by 60,000+ disks in a single warehouse."

No main verb, and the conclusion (how many failures per day that implies) is never stated — a student cannot finish the arithmetic from what is given. Also worth a date check on the "2-10\% of disks fail per year" figure.

### RAID-10 description is hard to follow — filesystems.tex:1101-1105

> "This means you would get roughly the same speed from the slowdowns but now any one disk can fail and you can recover that disk."

"the same speed from the slowdowns" is not parseable, and the redundancy claim needs care: in RAID-10 any single disk can fail, and *some* two-disk failures are survivable while a mirror pair failing is not. Technical, so left alone.

### RAID-3 bottleneck reasoning — filesystems.tex:1114-1115

> "This means that there is effectively a bottleneck in a separate disk. In practice, this is more likely to cause a failure because one disk is being used 100\% of the time and once that disk fails then the other disks are more prone to failure."

"a bottleneck in a separate disk" is confusing (the bottleneck *is* the dedicated parity disk), and "once that disk fails then the other disks are more prone to failure" is a non-obvious causal claim that needs justification or removal.

### Write-to-file walkthrough mixes up inodes, data blocks, and indices — filesystems.tex:1253-1256

> "For this particular example we would have to go to the 2nd or indexed number 1 inode to perform our write."

This should almost certainly be the 2nd *data block* (the inode is a single object here), and the next sentence then says "go to the $5$th data block", which does not obviously follow from "2nd". Since the whole passage depends on the figure at filesystems.tex:1176, an author who can see the figure should reconcile the numbering.

### Follow-up question is garbled — filesystems.tex:1262

> "How would a program perform a write after adding the offset would extend the length of the file?"

Not a grammatical sentence, and it is unclear how it differs from the next question ("offset is greater than the length of the original file"). Left alone because the intended meaning is genuinely ambiguous.

### Figure has no alt text — filesystems.tex:1174-1178

`\includegraphics{filesystems/images/sample_file.png}` with caption "Sample file filling up". The whole "Simple Filesystem Model" section (file size bounds, reads, writes) is written entirely against this image — a student using a screen reader, or reading the text alone, cannot follow any of the worked calculations. Adding a textual description of the inode's block pointers would fix this.

### Fragment in "Writing to directories" — filesystems.tex:1268-1270

> "If we pretend that the example above is a directory. We know that we will be adding at most one directory entry at a time. Meaning that we have to have enough space for one directory entry in our data blocks."

Two sentence fragments in a row ("If we pretend..." with no main clause, and "Meaning that..."). Fixing them requires deciding what the sentences were meant to join to, so left to an author.

---

## signals

### signals.tex:7 — "Sometimes, a program can choose to ignore events which is supported."
Circular/confusing as written; it is unclear whether the point is that ignoring is a supported disposition, or that only some signals may be ignored (SIGKILL/SIGSTOP cannot). A student would benefit from the caveat being stated explicitly here.

### signals.tex:58-62 — figure has no alt text
`\includegraphics{signals/drawings/signal_lifecycle.eps}` with caption "Signal lifecycle diagram" only. The caption does not convey the lifecycle content to a reader using a screen reader, and the surrounding text (line 56, "As a flowchart") does not describe it either.

### signals.tex:262 — sig_atomic_t range claim
"can be as small as a \keyword{char} and only able to represent (-127 to 127) values" — a technical claim about limits (C requires at least SIG_ATOMIC_MIN/MAX coverage) that I did not want to touch.

### signals.tex:46 — "the process' signal mask"
Possessive of a singular noun ending in s-sound written as `process'`; elsewhere I normalized "processes mask" to "process's mask" (lines 431-432). Left line 46 alone to avoid churn, but the book should pick one convention.

---

## security

### Step 2 refers to an antecedent that doesn't exist — security/security.tex:37

> "First, you should determine if your use is intended or unintended or somewhere in the middle -- get a decision from them."

"them" has no antecedent in the sentence (presumably the system's owners/developers). I fixed "for them" -> "from them" but the referent is still dangling.

### "In lieu" used without an object — security/security.tex:51

> "In lieu, you must be able to say that you reacted as a ``reasonable'' engineer would react."

"In lieu" requires "of X"; the intended phrase is probably "In lieu of that" or "Instead". Left alone as it may be deliberate shorthand.

### "each user has a certain set of permissions that they can do" — security/security.tex:227

Grammatically mismatched ("permissions ... do") and conflates capabilities with permissions. Suggest "a certain set of capabilities" / "set of actions they are permitted to perform", but the wording sits inside a technical definition, so leaving to a human.

### DNS trust sentence is confusing — security/security.tex:324

> "One just has to trust the DNS server gave a reasonable response which is almost always the incorrect answer."

Unclear what "the incorrect answer" refers to — the DNS response, or the decision to trust it. Reads as a garbled sentence; needs the author's intent.

### Review question 381 vs body text — security/security.tex:336 and 381

Line 336 already states "Distributed Denial of Service is the hardest form of attack to stop", which answers review question 10 ("Which is harder to defend against: Syn-Flooding or Distributed Denial of Service?") outright. Intentional? Possibly fine, but flagging.

---

## review

### review/review.tex:135 — truncated bonus question
The item ends: "Bonus: How would you make this code more robust or able to cope with?" The sentence is cut off ("cope with" what — a long `mesg`? a `malloc` failure?). The same sentence also says "val as a double val", which looks like a duplicated word but might be intentional shorthand. Both need an author who knows the intended question; rewriting could change what is being asked.

### review/review.tex:197-203 — question text is split across a code listing
"When would a trivial malloc implementation" / listing / "be acceptable?" I lowercased the stray capital "Be", but the sentence still reads oddly when the listing is set as a display block. A human may prefer to reword (e.g. "When would the trivial malloc implementation shown below be acceptable?").

### review/review.tex:322-337 — two items describe one problem, and item 2 has no question
Item at 322 sets up the graph/`shortest`/`set_edge` scenario and ends at line 335 with a requirement statement but no explicit question ("For performance, multiple threads must be able to call \keyword{shortest} at the same time..."). The next `\item` (337) then asks for the reader-writer implementation of the same scenario. These probably should be one item, or item 1 needs an actual question sentence.

### review/review.tex:519 — chmod question sentence is ungrammatical
"...so that the owner can read, write, and execute permissions the group can read and everyone else has no access." The verb "can" does not fit "permissions", and there is no punctuation separating the owner clause from the group clause. I only fixed the missing spaces after the commas; the rest is a rewrite that touches what the question asks (intended answer is presumably `chmod 740`), so a human should word it.

### review/review.tex:513,515,585 — space before question mark
Three items have "notes.txt} ?" / "listen accept ?" with a space before the "?". Left alone as it may be a deliberate consequence of the `\keyword{}` macro spacing, but a human may want them tightened.

---

## honors

### honors/kernel.tex:11-13 — Windows/Darwin sentence was structurally broken
Original text read as two fragments: "...the Windows kernel, which we won't talk about too much in this chapter." followed by a new line beginning "or \keyword{Darwin}, the UNIX-like kernel for macOS...". I joined them with a comma (minimal fix), but the result now reads as "we won't talk about Windows or Darwin", which may not be the intended meaning — the original may have lost a clause such as "Others may have used XNU or Darwin". Please confirm the intended sentence.

---

## appendix

### appendix/appendix.tex:358 — garbled sentence in the Fork-FILE explanation

> "Summarizing as if two file descriptors are actively being used, the behavior is undefined."

"Summarizing as" is not grammatical, and it is unclear whether the intended meaning is "Summarizing: if two file descriptors are actively being used..." or something narrower (POSIX's condition is about *handles* to the same open file description, not any two descriptors). Because the precise POSIX claim matters, a human should decide the wording.

### appendix/appendix.tex:442 — truncated sentence

> "Also, the messages now encounter additional overhead for serializing and deserializing or at the least."

The sentence ends mid-thought ("or at the least" what?). Needs the author to supply the missing clause.

### appendix/appendix.tex:592 — "a few filesystem hardware"

> "There are a few filesystem hardware nowadays that are truly cutting edge."

Ungrammatical count/mass mismatch; likely intended "a few filesystem hardware technologies" or "a few filesystems". Word choice is the author's call, and the section then discusses StoreMI (a hardware/software caching product), so the right noun is ambiguous.

### appendix/appendix.tex:639 — stray one-word paragraph "Yes"

Section `\subsection{Implementing Software Mutex}` opens with a bare line reading `Yes` before "With a bit of searching, it is possible to find it in production...". This looks like the answer to a question that was deleted (probably "Is Peterson's algorithm ever used in practice?"). The paragraph also has an unexplained "it". A human should restore the missing question or delete the line.

### appendix/appendix.tex:943 — Sequential consistency definition is hard to parse

> "This model says that any change that happens, all changes before it will be synchronized between all threads."

Grammatically broken and technically imprecise (sequential consistency is about a single total order of operations consistent with program order). Needs an author rewrite.

### appendix/appendix.tex:986 — duplicated/garbled clause introducing Go

> "We'll talk about a language go that is similar to C in terms of simplicity and design, go or golang"

The language name appears three times and the sentence has no terminal punctuation. Probably intended: "We'll talk about a language similar to C in terms of simplicity and design: Go (or golang)." Left alone because it is a rewrite, not a typo fix.

### appendix/appendix.tex:1126 vs 1317 — inconsistent symbol for maximum run time

Line 1126 says "Let the maximum amount of time that a process runs be equal to $S$", but line 1317 says "$T$ is the maximum amount of time a process can run for". Meanwhile $S$ is used throughout as the *service time* random variable. A student following the derivations would be confused; needs the author to pick one symbol.

### appendix/appendix.tex:1288 — broken sentence

> "Imagine a series of FCFS queues that a process needs to wait your turn."

Mixes third and second person and is missing words. Rewrite needed.

### appendix/appendix.tex:1393 — dangling "either"

> "given a distribution of jobs that has either low waiting time as described above"

"Either" has no second alternative. Likely a dropped clause.

### appendix/appendix.tex:1461 — orphan fragment in the routing list

> "These protocols are meant to be fast and more trusting because all computers, switches, and routers are part of an ISP.
> communication between two routers."

The last line is a lowercase sentence fragment with no context — apparently a leftover from an edit. Needs the author to restore or delete.

### appendix/appendix.tex:1494 — duplicated "assuming" and unclear claim

> "assuming the probability of receiving a packet assuming each fragment is lost with an independent percentage, the probability of successfully sending a packet drops off exponentially as packet size increases"

The sentence is garbled; I could not tell which "assuming" to drop or how the independence assumption was meant to be phrased.

### appendix/appendix.tex:1522 — garbled sentence about kqueue

> "kqueue is the truest sense of underlying descriptor agnostic."

Not a grammatical sentence; probably intended "kqueue is descriptor-agnostic in the truest sense." Rewrite needed.

### appendix/appendix.tex:171-198, 1409-1413 — figures have no alt text

`\includegraphics` for `struct_clean.eps`, `struct_slop.eps`, and `ip_datagram.eps` have captions ("Six box struct", "IP Datagram divisibility") but no descriptive alternative text. The IP datagram figure in particular carries information not otherwise in the text. Accessibility decision for the author.

---

## post_mortems

### AT&T 1990: "operable when they weren't" may be backwards
`post_mortems/post_mortems.tex:215` — "A series of network delays that caused some telephone switches across the country to think that other switches were operable when they weren't." The usual account of the January 1990 AT&T collapse is that a switch went down for maintenance, and the *recovery* message it sent when coming back up crashed its neighbours via a misplaced `break` in C code — i.e. switches wrongly concluded peers were *inoperable*/failing. Either wording direction is a factual claim about a real incident, so I left it. Also note this sentence is a fragment ("A series of network delays that caused...") with no main verb.

### Appnexus double-free description is hard to follow
`post_mortems/post_mortems.tex:203` — "This is fine until two threads try to delete the same object at once, adding to the list twice. After less time, one of the objects was deleted, the delete was announced to other computers." "After less time" is meaningless as written, and the causal chain from double-add to outage is not explained. A student cannot reconstruct the bug from this. Needs a rewrite by someone who knows the incident.

### Mars Pathfinder paragraph: run-on and tense-mixing
`post_mortems/post_mortems.tex:74,76` — Line 74 mixes past and present ("The finder uses a single bus...", "if an interrupt happened ... and a task is running and a task is to be scheduled"). Line 76 is a comma splice: "The pattern that caused everything to start failing was the data collection thread starts writing to the bus, the information bus thread is waiting on the data." Fixing this properly means restructuring sentences, which is beyond a low-risk copy-edit. Note the classic name for this bug — priority inversion — is never stated, which is the one term a student would want.

### Sentence fragment in the Sony rootkit section
`post_mortems/post_mortems.tex:156` — "What websites visited, what clicks or keys typed etc." has no verb. It reads as a deliberate telegraphic aside in an informal chapter, so I left it, but a human may want "What websites are visited, what clicks or keys are typed, etc."

### Meltdown and Spectre sections are stubs with unverifiable pointers
`post_mortems/post_mortems.tex:60-66` — "There is an example of this in the background section." / "Check in the security section." These are prose pointers, not `\ref{}`s, so they cannot be checked by the build and will silently rot if chapters are renamed or reordered. Consider real `\ref{}`s, or content.

### No `\label{}` anywhere in the chapter
`post_mortems/post_mortems.tex` (whole file) — The chapter and its ~16 sections define no labels, so nothing elsewhere in the book can cross-reference an individual post-mortem. Structural, and a human's call.

---

