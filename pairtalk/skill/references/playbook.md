# The talk playbook: PairTalk's built-in defaults

Read this before you build or revise a talk. It is what a careful author asks for again and again when they review a research
talk click by click, written down so that a first draft already meets it and the author's comments are about their work, not
about these rules.

- **Authority.** The author's request in front of you, then the vault's `STYLE.md` (base rules, confirmed rules, tentative
  patterns, the *Pacing and script* table), then this file. Where `STYLE.md` says otherwise, follow `STYLE.md`. The visual look
  (palette, type, layout) comes from PairDeck's style guide when the author has one (`pairtalk paths` names it); §3.7 is the
  fallback.
- **Hard rules** are marked ★: they are the comments reviewers write most often. Treat them as rules, not suggestions.
- **Facts bound everything.** Style never changes a claim, a number or a result. Check every number against its source.

## 1. The tool

A talk is a folder: `index.html` (title, `window.DECK_COMMENTS`, the slot `window.DECK_MINUTES`), `slides/order.js` (the
files in order), one file per slide in `slides/`, and `SCRIPT.md` (the speaker notes, one block per click). The skill's
`SKILL.md` describes the slide file format; `qa.md` says how to check every click.

## 2. The story arc of a research talk

Use this as the default storyboard. Draft the structure this way from the start; do not restructure a talk the author has
approved unless they ask. When they say the structure is right, strengthen the links between slides instead.

| Part | What the slides do | Rules |
| --- | --- | --- |
| Title | The thesis as a short title in the paper's own frame; a short phrase as subtitle; authors with exact affiliations; venue and session | Coauthors in author order; check each affiliation at its source |
| The problem you can see | One or two slides on the failure or puzzle in the wild, with real data and a striking build | Numbers you verified. Show a trend across many cases, never one paper or person as the negative example |
| Prior explanations, then ours | Earlier explanations grouped by the mechanism they propose, one row each, short citations; then "Our perspective: …" with a picture | Every click has a title that fits it. Describe others' work charitably and with hedges. Background the audience knows gets one spoken sentence |
| The model | "Our unified view: …" Define the basic object first, then our step on top. Assumptions appear one per click as bold one-line slogans | The last click settles on the simplest, most important content |
| Parameters and questions | Each design choice becomes a symbol defined in one line; known methods as settings of those symbols (two examples per family, then "…"); the research questions close the slide | Bring back the key picture with the symbols on it |
| Results | One slide per question: "Result k · <question>", the answer on the next line, then plain lines | Parallel slides share one style and one sentence pattern |
| Does the theory hold? | A question title, then the test setup as aligned rows with icons | No boxes, no subtitle |
| Evidence | Small multiples with the regime on each panel; a key for line styles | Only the panels that carry the message |
| The fix or the method | The formula with the added term coloured; geometry drawn with equal axes | A title in plain words |
| Takeaways | "Takeaways", three one-line items in the author's words; key phrases in bold | Condense the author's words; do not replace them |
| Backup | Everything cut from the main line | Move a slide here rather than delete it |

**Length.** About 140 spoken words a minute, unless `STYLE.md` records the author's own pace. A 15-minute slot holds about
16 main slides and 2,100 words. When two slides carry one message, keep the more informative one and move the other to the
backup. Fold a transition slide into the end of the slide before when that slide has room.

## 3. On the slide

### 3.1 Titles ★

- **A title is a claim, or the question the slide answers,** on one line of about 60 characters. Two balanced lines only when
  the claim truly needs them. Shorten: drop "not …" clauses and qualifiers the picture already shows.
- **Contribution slides say so:** "Our perspective: …", "Our unified view: …".
- **Titles chain.** Reading the titles alone tells the argument. A question posed on one slide is the title of the slide that
  answers it.
- **The title fits every click.** If click 0 shows other material, give it its own title and cross-fade at click 1.
- **Plain words.** If the author asks what a title means, say directly what changes and what follows.
- **No repetition** of the text right below the title.
- **The author's own wording.** When the author writes a title in rough form, keep their words and fix only the grammar; say
  in the reply what you fixed. This holds for all slide text.

### 3.2 Words ★★ (the most frequent comment)

What the speaker does not say never appears as bullet points on the slide; the speaker always says more than the slide shows.
The slide holds the anchors of the talk: the title, labels, the key number, the formula and the picture. Every explaining
sentence belongs in the script.

**Never put these on a slide:** a takeaway line at the bottom; a subtitle that explains or argues; grey explanatory text under
a card, box, chart or row; statistical fine print and panel counts; run details, caveats and references to the paper's
sections; result chips that repeat what the chart shows; a derivation the audience has no time to read.

**What may stay:** a card title written "setting: finding" with its key number; outline boxes with only the big words; a bold
one-line assumption; two examples per family, then "…"; the first words of a long name, then "…"; what a chart needs to be
read (who or what is compared, what the axis means in plain words); the one line the author marks as the point.

Count the visible words on every main slide. Labels have at most six words.

**All text is large.** No visible text below 32 px on the 1920 × 1080 stage (labels `.lab.s` and up); chart tick labels at
least 28 px. **One quantity, one number:** never two counts of the same thing on a slide unless each is labelled.

### 3.3 Symbols, formulas and definitions ★

- **No undefined symbol, ever.** Define each in one line on the slide where it first appears, starting with the most basic
  object.
- **Prefer a formula to prose when it is precise,** but bring in each quantity only when it is needed; never stack many
  formulas on one slide.
- **Define a parameter once, with its formula, where it is born;** later slides use its name. Remind the audience by bringing
  back the key picture with the symbols on it.
- **Name every equation** in a label before it.
- **Analogies are aligned term by term:** the familiar formula and ours stacked so matching terms share a column, each labelled;
  then both solutions; then the analogy fades and only ours stays.
- **Box the key closed form,** and give each part the same colour in every formula where it appears.
- **State modelling approximations** as bold one-line assumptions, and name what follows from them.
- **The order of a hard idea:** definitions, then a picture, then the formula, then examples.
- **Every statement on a slide is true as stated.** If it holds only under a condition, state the condition briefly.
- **Formulas are typeset** with the maths renderer, never with ASCII or Unicode subscripts.

### 3.4 Figures and data

- **The regime on every panel** (the parameters that set it), and no vague words ("slow", "partial") without their value.
- **A key for line styles**; **axes in the setting's own terms**; **matching points line up** across series.
- **Screen every panel before the author sees it**: drop or explain a trend that looks contrary to the claim or off-message.
- **Measured results, with error bars,** unless the accuracy of a prediction is the point.
- **Geometry stays geometry** (equal axis scales); **crop to where the action is**; **no unexplained gaps** in a series.
- **Side by side beats click-switching** when the point is a comparison.
- **Explain a mechanism with a picture:** icons and a minimal formula, connected by arrows to what they explain.
- **When the author misreads a figure,** explain in the reply and treat the label as the bug.
- **Chart text is large:** in-chart labels 28 px or more; legends as large as the text around them.

### 3.5 Layout and size ★★

- **Fill the frame.** Content takes about 92% of the height and 95% of the width, with similar margins from slide to slide;
  no large empty bands, no small island in the middle. Fix a sparse slide with larger type, a side-by-side layout or wider
  cards.
- **Do not overshoot.** Balanced, not maximal: the space above the content about equals the space below.
- **Cards keep their natural height;** **nothing jumps** (reserve the space of later builds); **no forced wraps** of
  single-line items.

### 3.6 Builds and animation

- **One idea per click.** Parallel items appear one at a time, in the order of the process; each click's script sentence starts
  as its item appears.
- **Contrast by correction:** show the old item, strike it out, write the new one beside it.
- **The opening earns a showpiece build;** elsewhere motion serves reading order.
- **The last click is the summary:** transient explanations fade, and the slide settles on the few things to remember.
- **No empty clicks.** When a click's content is removed, remove the click and merge its script into the click before.

### 3.7 Look (the template's default)

White paper, Computer Modern type, one quiet colour per recurring object, kept on every slide (`css/deck.css` defines the
tokens). Green marks a good or stable outcome and red a failure or condition. Titles centred at the top, 56 px. Lists are
plain aligned rows (icon, label, text), with no boxes and no fills; keep boxes for the key formula, the research questions
and cards that hold a figure, and put a box's label outside it. Check icons (every arrowhead present). The author's PairDeck
style guide, when there is one, replaces this section.

## 4. The script ★

The notes are what the speaker reads aloud.

- **Conversational, first person:** "Let me start with something you have seen", "Here is the idea", "Let me make this
  precise."
- **One note per click, opening with that click's point.** When a build reveals a sentence piece by piece, split the sentence
  across the clicks.
- **A bridge at the end of every slide** to the next one ("Those are the predictions; now let us test them.").
- **Headline numbers stay, detail goes.** Keep the key numbers and the regime; cut seeds, panel counts, caveats and derivations.
- **The note carries what left the slide,** worded as the speaker would say it.
- **The opening states the contribution** in the venue's framing, and the hook says what the data are.
- **No "if asked" sections** in the notes; keep Q&A material in backup slides.
- **The same terms as the slides and the paper.**
- **The total fits the slot** at the author's words per minute.

## 5. Terms

Use the paper's own terms everywhere: on the slides, in legends, in the script and in replies. Name a condition by what it is.
When the author describes something in their own words, use their words. Record the talk's terms in its `NOTES.md`.

## 6. Working through comments

- **The loop:** read the comment and its box; fix the slide; screenshot the affected clicks (`qa.md`); sync the script;
  reply with `pairtalk resolve`.
- **The reply:** the exact new wording, what moved, and an alternative only if it is worth the author's time.
- **One comment, every parallel place.** Apply the same fix to every parallel slide, card and view before you reply, and list
  them in the reply.
- **A question in a comment** gets an answer, and the slide changes so that the next viewer does not need to ask.
- **When a request conflicts with a fact,** do the correct version and say so.
- **Before you wire in a fact or a number,** check it against the paper or the accepted results.
- **Menus for simplification:** when the author asks for suggestions, number the options; they answer with numbers.
- **"Leave as is" means no change.** Never edit another talk's folder; a talk for a new venue is a fork.

## 7. Adapting a talk to another venue

Fork the folder as presented (`pairtalk new <name> --title …`, then copy the slides and the script). Change the framing words,
not the structure; put the venue's program title in as the subtitle if it differs. Add no content when the length is final.
Before the talk, review the slides and the script together from the audience's point of view, and let the author pick what
to apply.

## 8. First-draft checklist

Run this before the author sees anything; each line is a comment they should not have to write.

| Check | Rule |
| --- | --- |
| Every title is one line, a claim or a question, and does not repeat the text below it | §3.1 |
| Each click has a title that matches what is on screen | §3.1 |
| Nothing on a slide the speaker will not say: no subtitles, grey notes, fine print or result chips | §3.2 |
| Card titles say "setting: finding" with a number | §3.2 |
| Every symbol is defined where it first appears; few formulas per slide | §3.3 |
| Every chart panel shows its regime; a key for line styles; axes in plain terms | §3.4 |
| Fill: about 92% of the height and 95% of the width, even margins, nothing oversized | §3.5 |
| No visible text below 32 px; chart labels 28 px or more | §3.2 |
| Lists are plain rows; boxes only for the formula, the questions and figure cards | §3.7 |
| Parallel items build one per click; the last click leaves only the essentials; no empty click | §3.6 |
| The paper's terms everywhere | §5 |
| The script is conversational, one point per click, a bridge per slide, no "if asked", and fits the slot | §4 |
| Every comment applied to all parallel slides, cards and views | §6 |
| Every detail removed from a slide is in that click's note | §4 |
| Every click screenshotted and looked at; no console or font errors (`qa.md`) | QA |
