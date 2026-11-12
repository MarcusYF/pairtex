# Content: accuracy and story

The author's name is on these decks, often next to their own work. Being accurate matters more than flair: an elegant slide
that overstates a result is a failure.

## The fact sheet

Before designing, read the whole source and write a fact sheet. Keep it next to the deck (`facts.md`, or `sources.md` for a
report) or in your scratch space, and summarise it in your report to the author.

```
claim / number                              source location            how shown
A: 273 of 350 succeed (78%)                 Table 1                    slide 4 bars
within small stones, A 93% vs B 87%         Table 1                    slide 3 bars, "computed" rates
A falls below B once > 52% are large        computed from Table 1      slide 6 slider marker, labelled "computed"
```

Rules:
- Every number and factual claim on a slide comes from the fact sheet, which comes from the source.
- **Headline numbers are numbers you verified**: recomputed, or read from a primary source. A third party's count may appear in
  the picture with its source, never as the headline. When an outside count and yours differ in definition, say so in the note.
- **Derived values.** A value computed by applying the source's own formula to its own data is allowed. Mark it "computed" on
  the slide or in its note, and write the computation in the fact sheet. Do not extrapolate beyond the source's setting
  without saying so.
- A value read off a plot gets "≈" on the slide and "approximate" in the note. Exact values come from text or tables.
- Toy examples, invented curves and stylised pictures say "illustration" or "schematic" on the slide.
- Keep the source's qualifiers: "in the worst case", "in simulations", "under these assumptions", "on this dataset". Shorten
  them, never drop them.
- Prefer a faithful qualitative statement to a precise one that needs mathematics.
- Use the exact title, author order and venue the source of record uses.

### Sources by kind

- **Papers:** the full PDF or HTML version. Do not try to get around a bot check on any site.
- **Reading PDFs.** Text extraction garbles formulas set in maths fonts: read numbers and symbols off page images.
- **Citing slides.** Keynote and PowerPoint exports put each build on its own PDF page, so cite the slide number printed on the
  slide, and say which numbering you used.
- **Unpublished or confidential work:** show only what the author allows in public (often the public abstract). Ask if unsure.
- **Course material:** use the course's slides and notes, and match their notation and terms so students recognise them. Keep the
  house colour roles and show the mapping in a legend.
- **Projects and tools:** the README, the docs and the actual behaviour. Use clearly fictional sample data and say so on the page;
  never show real accounts, paths, e-mail addresses or private data.
- **Research and investigations:** prefer primary sources (papers, official documents, data, the code). Record each source's
  URL or path and the date you read it; put "as of <date>" on anything that changes quickly. When sources disagree, show the
  disagreement. Mark every claim as confirmed (several sources or a primary one), single-source, or your inference, and carry
  the mark onto the slide (a small chip or a note).

## Images from the source

Do not reuse photographs of real people, screenshots, or figures cut from slides, papers or websites. Redraw the idea in the
house style and name the original in the note ("after Fig. 3 of the paper"). Reused images raise consent and copyright issues,
and they break the style. Exception: when the point is what something really looks like (a model's actual output, an
observable failure), real images may be shown, from your own runs or verified sources, each with alt text and a source line.

## Audience and voice

- **Default reader:** a smart non-specialist (a prospective student, a colleague from another field, a practitioner).
- **Voice:** plain, warm, short sentences. Introduce a term the first time it appears, or replace it with a picture.
- **Language:** the author's choice; the default is the author's language, or English for anything public.

## Story structures

Use 6 to 10 slides; one idea per slide; the headline states the point. Titles chain into one argument from slide to slide.

**Paper (the default)**
1. Title: the exact title, with the question the paper answers as the subtitle.
2. Setting: the actors and what each does (a flow diagram that builds up).
3. The problem or tension: why the question is hard or matters (often a contrast).
4 to 6. Results: one idea each (a chart, a schematic, a mechanism picture). After an abstract result, a worked example small
   enough to check by hand.
7. Evidence or "Try it": data from the paper, with an interaction.
8. Takeaways: three numbered points, then links.

**Overview** (several works on one theme)
The question that unifies them → the landscape (actors and tension) → one slide per work or thread (a picture of its key
finding) → how the pieces fit → open questions → links.

**Course concept** (a web companion to a lecture)
A hook question students can answer intuitively → the picture behind the concept → the mechanism, step by step → "Try it" (a
slider or toggle on a worked example) → a common misconception, as a contrast → recap in three points.

**Project or tool**
The problem in the user's words → how it works (actors and flow) → "Try it": a walkthrough or demo with a fictional but realistic
example, labelled as such → two or three design choices that make it useful or trustworthy → takeaways, status and links.

**Proposal or pitch**
The problem and who feels it → why now: when a current public event bears on it, one dated, sourced sentence about the event
(its exact status: preliminary findings are not a decision), then what it asks for mapped to what the proposal does → the
approach (a picture) → aims or milestones (a timeline that builds up) → expected impact, stated modestly → team and links.

**Report** (findings of an investigation, for the author or a team)
1. Title: the question as asked, with the date and scope as the subtitle ("as of 2026-03-02 · 12 sources").
2. The answer: the bottom line in one picture, with how confident you are (a verdict card with a confidence bar, or the
   winning option highlighted among the alternatives).
3 to 6. Evidence: one slide per supporting finding, each a picture. Source numbers go in the note.
7. Uncertainty: the claims sorted into confirmed, single-source, inference, and still unknown. Conflicts stay visible.
8. Implications or next steps, when the question calls for a decision: three numbered points.
9. Sources: numbered titles with links and access dates (this slide may be a compact list).

**Experiment results** (a report on runs, training or simulations)
- A setup slide (or a row in a setup table) per experiment family: the model or system, the data and how it was built, the
  labels or judge, the objective, every parameter that sets the regime, how predictions were made, the compute. Each result
  slide repeats the parameters that set its regime in its panel labels.
- The raw evidence, not only derived metrics: the logged loss or metric as recorded, against its reference; a few
  representative examples followed across the settings compared (small multiples, the theory overlaid when there is one),
  chosen so the regimes are visible side by side. Say what was not logged.
- Means with ± 1 standard deviation over runs, and the number of runs in the legend (`style.md` §5).

**A concept the rest rests on** (an equilibrium, an index, a model)
Right after the answer: the definition as a formula, set large and colour-coded by part, with one box per symbol saying what it
is in the running example. Then, in order: the role of each parameter (with limiting cases), how each part is measured (method,
data, result so far), and what it explains that the alternatives do not (a table of phenomena against theories, with the
evidence for each row).

When the answer depends on a parameter or on regimes, show for each regime what changes in the object the reader already
thinks in, with the unchanged data drawn once and stated as unchanged. A label such as "isolated" or "pooled" is not an
explanation.

When a discussion with the author built up concepts ("what does X mean", "is my reading right"), add a short Concepts block
after the answer: one picture per concept with the running example, and a partly-right reading shown as a tempting shortcut,
with what holds and what fails.

## Follow-ups

When a deck already exists for a project and a new result extends it, update that deck: add a slide only for a new phenomenon
or check, fold the rest into the existing slides, and add a dated entry to its `sources.md`. Do not build a separate deck for
each increment unless the author asks.

## Interaction ideas

- Toggle between two policies or scenarios and redraw the bars from a table in the source.
- A slider over a parameter that moves a clearly labelled schematic, or recomputes a chart from the source's numbers.
- Step through rounds of a process (learning, competition, an attack), one button per round.
- "Guess first": the reader picks an answer, then the slide reveals the result.

Every interaction must teach something the static slide cannot, and its data must come from the fact sheet or be labelled as
a schematic.
