#!/usr/bin/env python3
"""End-to-end test of the PairTeX loop against a local bare repository standing in for Overleaf.

"Ada" is a second clone that commits "Update on Overleaf." and pushes, as Overleaf's git bridge does.
Run: python3 tests/test_e2e.py   (needs git; latexmk for the compile checks)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OW = Path(__file__).resolve().parent.parent / "bin" / "pairtex"
TMP = Path(tempfile.mkdtemp(prefix="ow-test-"))
HOME = TMP / "home"
ENV = dict(os.environ, PAIRTEX_HOME=str(HOME), GIT_TERMINAL_PROMPT="0")
ADA = TMP / "ada"
REPO = HOME / "projects" / "demo" / "repo"
passed = 0

DOC = r"""\documentclass{article}
\newcommand{\ada}[1]{{[Ada: #1]}}
\begin{document}
\section{Introduction}
Iterative preference optimization trains a policy on comparisons of its own samples. In this section we will basically discuss the reasons why reference refresh is used in practice, and we leverage the analysis to explain it. \ada{check this}

The second paragraph stays the same in every version of this test document.

\section{Model}
The model has three parts.
\end{document}
"""


def sh(*args, cwd=None, check=True):
    r = subprocess.run(list(args), cwd=cwd, env=ENV, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise AssertionError(f"{' '.join(map(str, args))} failed:\n{r.stdout}\n{r.stderr}")
    return r


def ow(*args, expect=0, timeout=60):
    r = subprocess.run([sys.executable, str(OW), *args], env=ENV, capture_output=True, text=True, timeout=timeout)
    if r.returncode != expect:
        raise AssertionError(f"ow {' '.join(args)}: exit {r.returncode}, expected {expect}\n--- stdout\n{r.stdout}\n--- stderr\n{r.stderr}")
    return r.stdout


def ok(cond, what):
    global passed
    if not cond:
        raise AssertionError(what)
    passed += 1
    print(f"  ok  {what}")


def ow_as(home, *args, expect=0, timeout=60):
    """ow with another data home (another person's profile and vault)."""
    env = dict(ENV, PAIRTEX_HOME=str(home))
    r = subprocess.run([sys.executable, str(OW), *args], env=env, capture_output=True, text=True, timeout=timeout)
    if r.returncode != expect:
        raise AssertionError(f"pairtex {' '.join(args)} (PAIRTEX_HOME={home}): exit {r.returncode}, expected {expect}\n"
                             f"--- stdout\n{r.stdout}\n--- stderr\n{r.stderr}")
    return r.stdout


def edit_as(clone, name, email, fn, message="Update on Overleaf."):
    """Someone edits main.tex through their own clone of the remote: pull, change, commit, push."""
    sh("git", "pull", "--quiet", "--ff-only", cwd=clone)
    path = clone / "main.tex"
    path.write_text(fn(path.read_text()))
    sh("git", "-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "--quiet", "-am", message, cwd=clone)
    sh("git", "push", "--quiet", "origin", "master", cwd=clone)


def ada_edit(fn, message="Update on Overleaf."):
    """Ada edits main.tex in the Overleaf editor: pull, change, commit, push."""
    edit_as(ADA, "Ada Lovelace", "ada@example.com", fn, message)


def agent_edit(fn):
    path = REPO / "main.tex"
    path.write_text(fn(path.read_text()))


def state():
    return json.loads((HOME / "projects" / "demo" / "state.json").read_text())


def main():
    print(f"scratch: {TMP}")
    (HOME / "style").mkdir(parents=True)  # the vault's name before 0.4 still works
    (HOME / "style" / "STYLE.md").write_text("# test style\n\n### S01 test rule\n")
    (HOME / "profile.json").write_text(json.dumps({"name": "Ada Lovelace", "handle": "Ada", "id_prefix": "c",
                                                   "email": "ada@example.com"}))
    remote = TMP / "remote.git"
    sh("git", "init", "--quiet", "--bare", "--initial-branch=master", str(remote))
    seed = TMP / "seed"
    sh("git", "init", "--quiet", "--initial-branch=master", str(seed))
    (seed / "main.tex").write_text(DOC)
    sh("git", "add", "-A", cwd=seed)
    sh("git", "-c", "user.name=Ada Lovelace", "-c", "user.email=ada@example.com", "commit", "--quiet", "-m", "first", cwd=seed)
    sh("git", "remote", "add", "origin", str(remote), cwd=seed)
    sh("git", "push", "--quiet", "origin", "master", cwd=seed)
    sh("git", "clone", "--quiet", str(remote), str(ADA))

    print("init")
    out = ow("init", "demo", "--remote", str(remote), "--main", "main.tex", "--protect", "ada", "--title", "Demo")
    ok("1 watched .tex files" in out and "0 open" in out, "init clones the project and finds no comments")
    cfg_path = HOME / "projects" / "demo" / "project.json"
    cfg = json.loads(cfg_path.read_text())
    ok(cfg["terminator"] == ".." and cfg["notes"] == "visible", "a new project uses the .. rule and visible notes")
    cfg.update(terminator=None, notes="source")  # the sections up to 0.2 test the earlier rules
    cfg_path.write_text(json.dumps(cfg))

    print("a comment goes out only once it has settled")
    ada_edit(lambda t: t.replace("\\ada{check this}\n", "\\ada{check this}\n%@ tighten this; avoid \"leverage\"\n"))
    out = ow("watch", "demo", "--once", "--settle", "60", expect=1)
    ok("1 still being written" in out, "an unsettled comment is held back")
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c1 · main.tex:6 · Introduction" in out, "the batch names c1 with file, line and section")
    ok("tighten this; avoid \"leverage\"" in out and "the paragraph directly above" in out, "the batch quotes the comment and its paragraph")
    ok(state()["comments"]["c1"]["status"] == "sent", "c1 is recorded as sent")
    out = ow("watch", "demo", "--once", "--settle", "0", expect=1)
    ok("no comment ready" in out, "a sent comment is not sent twice")

    print("the agent edits, answers and publishes")
    agent_edit(lambda t: t.replace(
        "In this section we will basically discuss the reasons why reference refresh is used in practice, and we leverage the analysis to explain it.",
        "We explain why practitioners refresh the reference policy and use the analysis to account for it."))
    out = ow("resolve", "demo", "c1", "Cut the signpost and \"basically\"; \"leverage\" became \"use\".")
    ok("1 paragraph change" in out, "resolve attributes one paragraph change to c1")
    text = (REPO / "main.tex").read_text()
    ok("%@c1 tighten this" in text and "%@c1> Cut the signpost" in text, "the comment becomes thread c1 with the reply under it")
    out = ow("push", "demo", "-m", "tighten the opening paragraph")
    ok("compiles" in out or "not installed" in out, "push runs the compile check")
    ok("published" in out and "answered c1" in out, "push publishes to the remote")
    sh("git", "pull", "--quiet", "--ff-only", cwd=ADA)
    fan_text = (ADA / "main.tex").read_text()
    ok("practitioners refresh" in fan_text and "%@c1> Cut" in fan_text, "Ada sees the edit and the reply in Overleaf")
    log = sh("git", "log", "-1", "--format=%s%n%b", cwd=ADA).stdout
    ok(log.startswith("pairtex: c1: tighten the opening paragraph") and "Co-Authored-By" in log, "commit message names the comment")

    print("Ada revises the new text, accepts the thread, and edits elsewhere")
    def accept(t):
        t = t.replace("We explain why practitioners refresh", "We explain why practitioners periodically refresh")
        t = "\n".join(l for l in t.split("\n") if not l.startswith("%@c1"))
        return t.replace("The model has three parts.", "The model has three components, which we describe next.")
    ada_edit(accept)
    out = ow("learn", "demo")
    ok("closed" in out and "Outcome: revised" in out, "learn reports c1 closed with Ada's revision")
    ok("{+periodically+}" in out, "the revision is shown as a word diff")
    ok("Ada's edit:" in out and "[-parts.-]{+components, which we describe next.+}" in out, "Ada's own edit elsewhere is evidence too")
    ok(out.count("periodically") == 1, "the revision is reported once, not twice")
    ok(state()["comments"]["c1"]["status"] == "closed", "c1 is closed")
    ids = [l.split()[1] for l in out.splitlines() if l.startswith("### E")]
    ow("learn", "demo", "--ack", *ids)
    ok(state()["pending_events"] == [], "acknowledged events leave the queue")
    ev = [json.loads(l) for l in (HOME / "style" / "evidence.jsonl").read_text().splitlines()]
    ok(len(ev) == len(ids) and all(e["project"] == "demo" for e in ev), "evidence.jsonl keeps every event")

    print("guards: coauthor notes, compile errors")
    ow("watch", "demo", "--once", "--settle", "0", expect=1)
    agent_edit(lambda t: t.replace(" \\ada{check this}", ""))
    out = ow("push", "demo", expect=7)
    ok("protected coauthor notes" in out and "check this" in out, "push refuses to drop \\ada{...}")
    sh("git", "checkout", "HEAD", "--", "main.tex", cwd=REPO)
    if shutil.which("latexmk"):
        agent_edit(lambda t: t.replace("The second paragraph stays", "The second \\undefinedmacro paragraph stays"))
        out = ow("push", "demo", "--allow-thread-removal", expect=6)
        ok("new LaTeX error" in out and "Undefined control sequence" in out, "push refuses an edit that breaks the build")
        sh("git", "checkout", "HEAD", "--", "main.tex", cwd=REPO)
    sh("git", "reset", "--quiet", cwd=REPO)

    print("inline comment, then a conflict while the agent works")
    ada_edit(lambda t: t.replace("The model has three components, which we describe next.",
                                 "The model has three components, which we describe next. %@ name the three components here"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c2 · main.tex:" in out and "the line with the comment" in out, "an inline comment refers to its own line")
    agent_edit(lambda t: t.replace("The model has three components, which we describe next.",
                                   "The model has three components: a sampler, a judge and a reference."))
    ow("resolve", "demo", "c2", "Named them: sampler, judge, reference.")
    ada_edit(lambda t: t.replace("The model has three components, which we describe next.",
                                 "Our model has three components, which we describe next."))
    out = ow("push", "demo", "--no-compile", expect=3)
    ok("nothing was published" in out and ".patch" in out, "a conflicting push saves a patch and publishes nothing")
    ok(state()["comments"]["c2"]["status"] == "sent", "c2 goes back to sent")
    text = (REPO / "main.tex").read_text()
    ok("Our model has three components" in text and "%@ name the three" in text, "the checkout now matches Overleaf")
    agent_edit(lambda t: t.replace("Our model has three components, which we describe next.",
                                   "Our model has three components: a sampler, a judge and a reference."))
    ow("resolve", "demo", "c2", "Named them: sampler, judge, reference.")
    out = ow("push", "demo", "--no-compile")
    ok("answered c2" in out, "redone on the new text, the push succeeds")
    sh("git", "pull", "--quiet", "--ff-only", cwd=ADA)
    t = (ADA / "main.tex").read_text()
    ok("Our model has three components: a sampler" in t and "%@c2 name the three" in t and "%@c2> Named" in t,
       "Ada sees c2 answered inline")

    print("Ada writes on the line next to the agent's edit: merged, not a conflict")
    ada_edit(lambda t: t.replace("The second paragraph stays the same in every version of this test document.",
                                 "The second paragraph stays the same in every version of this test document.\n%@ cite the survey here"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c3" in out and "cite the survey" in out, "c3 arrives")
    agent_edit(lambda t: t.replace("The second paragraph stays the same", "The second paragraph, unchanged, stays the same"))
    ow("resolve", "demo", "c3", "Done.")
    ada_edit(lambda t: t.replace("%@ cite the survey here", "%@ cite the survey here\n%@ and the 2024 benchmark"))
    out = ow("push", "demo", "--no-compile")
    ok("published" in out, "Ada adding a line under the comment being answered merges cleanly")
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c4" in out and "and the 2024 benchmark" in out and "Follow-up in thread c3" in out,
       "that line arrives as a follow-up in thread c3")
    ow("resolve", "demo", "c4", "Added the 2024 benchmark citation.")
    ow("push", "demo", "--no-compile")
    agent_edit(lambda t: t.replace("\\section{Model}", "\\section{The model}"))
    ada_edit(lambda t: t.replace("\n\n\\section{Model}", "\n\n%@ later: rename this section?\n\\section{Model}"))
    out = ow("push", "demo", "--no-compile", "-m", "rename section")
    ok("published" in out, "an edit on the line next to Ada's newer line merges and publishes")
    sh("git", "pull", "--quiet", "--ff-only", cwd=ADA)
    t = (ADA / "main.tex").read_text()
    ok("%@ later: rename this section?\n\\section{The model}" in t, "both changes are in Overleaf")
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c5" in out and "rename this section" in out, "Ada's comment from the merge is picked up")
    ow("resolve", "demo", "c5", "Renamed it to The model.")
    ow("push", "demo", "--no-compile")

    print("follow-up in a thread, and status")
    ada_edit(lambda t: t.replace("%@c2> Named them: sampler, judge, reference.",
                                 "%@c2> Named them: sampler, judge, reference.\n%@ say judge or reward model?"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("Follow-up in thread c2" in out, "a %@ line under a thread is a follow-up with its history")
    out = ow("status", "demo")
    ok("to finish first:" in out, "status lists the open comments")
    ow("resolve", "demo", "c6", "Judge, the paper's term.")
    ow("push", "demo", "--no-compile")

    print("another session pushes, then Ada types %@ mid-sentence and edits a heading (first real batch, 2026-11-07)")
    def fork(t):
        t = t.replace("The second paragraph, unchanged, stays the same in every version of this test document.\n", "")
        return t.replace("\n\n\\section{The model}", "\n\nA new paragraph pushed by the writing fork.\n\n\\section{The model}")
    ada_edit(fork, message="fork: polish step 2")
    ada_edit(lambda t: t.replace("Our model has three components: a sampler",
                                 "Our model has three components %@ in this paper: a sampler"))
    ada_edit(lambda t: t.replace("\\section{The model}", "\\section{The model and its parts}"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c7" in out and "in the middle of line" in out and "Before the comment the line read:" in out,
       "a mid-line comment shows the line as it was")
    ok('the comment is "in this paper:"' in out and '"a sampler, a judge and a reference."' in out,
       "the batch separates the comment from the prose it hid")
    evid = out.split("## Writing-style evidence")[1].split("## Next")[0] if "## Writing-style evidence" in out else ""
    ok("and its parts}+}" in evid and "Ada revised the text the agent wrote · The model and its parts" in evid,
       "Ada's heading edit next to the comment is evidence, under the right section")
    ok("{+Our+}" in evid, "a web edit the agent later rewrote is still Ada's evidence")
    ok("writing fork" not in evid and "Ada deleted a paragraph" not in evid, "another session's push is not Ada's writing")
    ok("in this paper" not in evid and "reference.-]" not in evid and "[-:" not in evid,
       "the comment itself, which hid half a line, is not an edit")
    agent_edit(lambda t: t.replace("Our model has three components %@ in this paper: a sampler, a judge and a reference.",
                                   "In this paper our model has three components: a sampler, a judge and a reference. "
                                   "%@ in this paper: a sampler, a judge and a reference."))
    out = ow("resolve", "demo", "c7", "Moved \"in this paper\" to the front.")
    ok("warning" not in out, "the hidden words are back in the prose")
    text = (REPO / "main.tex").read_text()
    ok("and a reference.\n%@c7 in this paper\n%@c7> Moved" in text, "the inline thread moves to its own lines")
    out = ow("push", "demo", "--no-compile")
    ok("answered c7" in out, "c7 is published")
    st = state()
    ids = st["pending_events"]
    ok(ids, "evidence is waiting")
    out = ow("learn", "demo", "--discard", ids[0], "--why", "test")
    ok("discarded 1" in out and ids[0] not in state()["pending_events"], "discard flags the event and drops it")
    ev = {json.loads(l)["id"]: json.loads(l) for l in (HOME / "style" / "evidence.jsonl").read_text().splitlines()}
    ok(ev[ids[0]]["discarded"]["why"] == "test", "the reason stays in evidence.jsonl")
    ow("learn", "demo", "--ack", *state()["pending_events"])

    print("0.2: a question about a bracketed sentence, answered without touching the text")
    sh("git", "pull", "--quiet", "--ff-only", cwd=ADA)
    (ADA / "old.tex").write_text("% an earlier draft\nIterative preference optimisation trains a policy on comparisons "
                                 "between its own samples, which we call the loop.\n")
    sh("git", "add", "old.tex", cwd=ADA)
    sh("git", "-c", "user.name=Ada Lovelace", "-c", "user.email=ada@example.com", "commit", "--quiet", "-m",
       "Update on Overleaf.", cwd=ADA)
    sh("git", "push", "--quiet", "origin", "master", cwd=ADA)
    cfg_path = HOME / "projects" / "demo" / "project.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["earlier_versions"] = ["old.tex"]
    cfg_path.write_text(json.dumps(cfg))
    ada_edit(lambda t: t.replace("Iterative preference optimization trains a policy on comparisons of its own samples.",
                                 "[[Iterative preference optimization trains a policy on comparisons of its own samples.]]")
             .replace("\\ada{check this}\n", "\\ada{check this}\n%? why does the paper open with this sentence?\n"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c8 · question · main.tex:" in out and "**A question" in out, "%? arrives as a question")
    ok('About the bracketed part (line 5): "Iterative preference optimization trains a policy on comparisons of its own '
       'samples."' in out, "the batch names the bracketed sentence")
    ok("History of these lines in Overleaf" in out, "a question comes with the history of its lines")
    ok("The closest passage in the earlier drafts:" in out and "- old.tex:2" in out and "optimisation" in out,
       "and with the closest passage in the earlier drafts")
    agent_edit(lambda t: t.replace("trains a policy on comparisons", "trains a model on comparisons"))
    out = ow("resolve", "demo", "c8", "It names the object first.", expect=7)
    ok("is a question" in out and "{+model+}" in out, "resolve refuses a question whose text changed")
    sh("git", "checkout", "HEAD", "--", "main.tex", cwd=REPO)
    ow("resolve", "demo", "c8", "It names the object of study before the problem, as the abstract does.\n"
                                "The earlier draft also called the iteration the loop.")
    text = (REPO / "main.tex").read_text()
    ok("[[" not in text and "]]" not in text, "resolve removes the brackets")
    ok('%?c8 "Iterative preference optimization trains a policy on … its own samples." why does' in text
       and "%?c8> It names the object" in text and "%?c8> The earlier draft" in text,
       "the thread keeps the ? mark, quotes the sentence and holds a two-line answer")
    out = ow("push", "demo", "--no-compile")
    ok("answered c8" in out, "the answer is published")

    print("0.2: %! with an inline bracket; an editor magic comment is ignored")
    ada_edit(lambda t: "%!TEX program = pdflatex\n" + t.replace(
        "our model has three components: a sampler, a judge and a reference.",
        "our model has three components: [[a sampler, a judge and a reference]]. %! use the paper's names"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c9 · main.tex:" in out and "question" not in out.split("## c9")[1].split("\n")[0], "%! is a change request")
    ok('About the bracketed part' in out and '"a sampler, a judge and a reference"' in out, "its bracketed words are named")
    ok("TEX program" not in out and "## c10" not in out, "%!TEX is not a comment")
    agent_edit(lambda t: t.replace("[[a sampler, a judge and a reference]]", "[[a sampler, a judge and a reference policy]]"))
    ow("resolve", "demo", "c9", "Reference became reference policy, the paper's term.")
    text = (REPO / "main.tex").read_text()
    ok("components: a sampler, a judge and a reference policy.\n%!c9 \"a sampler, a judge and a reference policy\" use "
       "the paper's names\n%!c9> Reference became" in text, "brackets go, and the inline thread moves under the line")
    out = ow("push", "demo", "--no-compile")
    ok("answered c9" in out, "c9 is published")
    out = ow("show", "demo", "c8", "c9")
    ok("[pushed question]" in out and 'About: "a sampler' in out, "show tells questions apart and quotes the part")
    ada_edit(lambda t: "\n".join(l for l in t.split("\n") if not l.startswith("%?c8")))
    out = ow("learn", "demo")
    ok("c8" not in out, "closing a question thread is not style evidence")
    ok(state()["comments"]["c8"]["status"] == "closed", "but the question is closed")

    print("0.2: [[a sentence]] %! mid-line hides the rest of the line, a \\ada note included; a range over two lines")
    ow("learn", "demo", "--ack", *state()["pending_events"])
    ada_edit(lambda t: t.replace(
        "We explain why practitioners periodically refresh the reference policy and use",
        "[[We explain why practitioners periodically refresh the reference policy]] %! say how often and use"))
    out = ow("watch", "demo", "--interval", "0.2", "--settle", "0.5", timeout=30)
    ok("## c10" in out and 'the comment is "say how often"' in out and "\\ada{check this}" in out.split("its last words")[1],
       "the batch splits the comment from the hidden prose, the coauthor note included")
    ok('About the bracketed part (line 6): "We explain why practitioners periodically refresh the reference policy"' in out,
       "and names the bracketed sentence")
    agent_edit(lambda t: t.replace(
        "[[We explain why practitioners periodically refresh the reference policy]] %!",
        "[[We explain why practitioners refresh the reference policy every round or every few rounds]] and use the analysis "
        "to account for it. \\ada{check this} %!"))
    out = ow("resolve", "demo", "c10", "Said how often: every round or every few rounds.")
    ok("warning" not in out, "the hidden words and the coauthor note are back")
    text = (REPO / "main.tex").read_text()
    ok("every few rounds and use the analysis to account for it. \\ada{check this}\n%!c10 \"We explain why practitioners "
       "refresh the reference … every few rounds\" say how often\n%!c10> Said how often" in text,
       "one clean line, the thread under it")
    out = ow("push", "demo", "--no-compile")
    ok("answered c10" in out, "c10 is published")
    import importlib.machinery, importlib.util
    loader = importlib.machinery.SourceFileLoader("owmod", str(OW))
    spec = importlib.util.spec_from_loader("owmod", loader)
    owm = importlib.util.module_from_spec(spec)
    loader.exec_module(owm)
    src = ("A first sentence. [[A second sentence that wraps\nonto the next line.]] A third [[x]] y.\n"
           "%! tighten the second sentence\n")
    opens, _ = owm.scan_file("t.tex", src)
    ok(len(opens) == 1 and [r["text"] for r in opens[0]["ranges"]] == [
        "A second sentence that wraps onto the next line.", "x"], "a comment takes every bracketed part above it, across lines")
    src2 = "One [[two]] three. %! about two\nFour [[five]] six. %! about five\n"
    o2, _ = owm.scan_file("t.tex", src2)
    ok([r["text"] for c in o2 for r in c["ranges"]] == ["two", "five"], "two inline comments each take their own part")
    ok(owm.parse_marker("%!TeX root = main.tex") is None and owm.parse_marker("% plain note") is None
       and owm.parse_marker("text \\% not a comment %? but this is")["mark"] == "?", "marker parsing edge cases")

    print("0.3: a comment ends with '..'; handled comments become green notes in the PDF")
    cfg = json.loads(cfg_path.read_text())
    cfg.update(terminator="..", notes="visible")
    cfg_path.write_text(json.dumps(cfg))
    ow("learn", "demo", "--ack", *state()["pending_events"])
    ada_edit(lambda t: t.replace("\\section{The model and its parts}",
                                 "%! name the parts in the heading, such as PPO, ...\n\\section{The model and its parts}"))
    out = ow("watch", "demo", "--once", expect=1)
    ok("1 without the closing .." in out, "a comment without '..' waits, however long; '...' does not close it")
    ada_edit(lambda t: t.replace("%! name the parts in the heading, such as PPO, ...\n",
                                 "%! name the parts in the heading, such as PPO, ..., 50% & more_x\n% or keep it short..\n"))
    out = ow("watch", "demo", "--interval", "0.2", timeout=30)
    ok("## c11" in out and "> or keep it short\n" in out, "'..' sends it at once, over a plain % line")
    ok("lines 19–20" in out, "the paragraph it refers to starts after the comment's own lines")
    agent_edit(lambda t: t.replace("\\section{The model and its parts}", "\\section{The model: sampler, judge, reference}"))
    out = ow("resolve", "demo", "c11", "Heading now names the parts: sampler, judge, reference (61 → 42 chars).")
    ok("a note in the PDF" in out, "resolve writes a note")
    text = (REPO / "main.tex").read_text()
    ok("\\claude{c11}{name the parts in the heading, such as PPO, ..., 50\\% \\& more\\_x or keep it short}"
       "{Heading now names the parts: sampler, judge, reference (61 $\\to$ 42 chars).}\n\\section{The model:" in text,
       "one green note line replaces the comment, with its text made safe for LaTeX")
    ok("\\quad\\textbf{Claude:}" in text, "the reply is set off from Ada's words")
    ok(owm.tex_text("the DPO type a_t=P\\mu_t. And (\\alpha, x^2) and more_x") ==
       "the DPO type $a_t=P\\mu_t$. And ($\\alpha$, $x^2$) and more\\_x", "bare maths in a comment is set as maths")
    ok("%!c11" not in text and "\\providecommand{\\claude}" in text and text.index("\\providecommand{\\claude}")
       < text.index("\\begin{document}"), "the \\claude macro is defined once in the preamble")
    if shutil.which("latexmk"):
        out = ow("push", "demo", "-m", "name the parts")
        ok("compiles" in out and "answered c11" in out, "the note compiles and is published")
    else:
        ow("push", "demo", "--no-compile")

    print("0.3: maths keeps % threads; Chinese stays in a % line; follow-up under a note; accepting a note")
    ada_edit(lambda t: t.replace("\\end{document}",
             "\\begin{equation}\na=b\n%? is this the right sign?..\n\\end{equation}\n%! 这里太长..\n\\end{document}"))
    out = ow("watch", "demo", "--interval", "0.2", timeout=30)
    ok("## c12 · question" in out and "## c13" in out, "both arrive in one batch")
    ow("resolve", "demo", "c12", "Yes: a equals b by definition.")
    text = (REPO / "main.tex").read_text()
    ok("a=b\n%?c12 is this the right sign?\n%?c12> Yes" in text and "\\claude{c12}" not in text,
       "inside an equation the thread stays in % lines")
    agent_edit(lambda t: t.replace("Our model has three", "The model has three"))
    ow("resolve", "demo", "c13", "Shortened the opening sentence.")
    text = (REPO / "main.tex").read_text()
    ok("%!c13 这里太长\n\\claude{c13}{\\emph{(the line above)}}{Shortened the opening sentence.}" in text,
       "a comment pdflatex cannot print stays verbatim in a % line above its note")
    out = ow("push", "demo", "-m", "c12, c13") if shutil.which("latexmk") else ow("push", "demo", "--no-compile")
    ok("answered c12, c13" in out and ("compiles" in out or not shutil.which("latexmk")),
       "both are published, and the Chinese comment does not break the build")
    ada_edit(lambda t: t.replace("{Shortened the opening sentence.}\n", "{Shortened the opening sentence.}\n%! shorter still..\n"))
    out = ow("watch", "demo", "--interval", "0.2", timeout=30)
    ok("## c14" in out and "Follow-up in thread c13" in out, "a comment under a note is a follow-up in its thread")
    ow("resolve", "demo", "c14", "Cut two more words.")
    ow("push", "demo", "--no-compile")
    ada_edit(lambda t: "\n".join(l for l in t.split("\n") if not l.startswith("\\claude{c11}")))
    out = ow("learn", "demo")
    ok("c11 · " in out and "closed" in out and state()["comments"]["c11"]["status"] == "closed",
       "deleting a note accepts its thread")
    ok("Heading now names" not in out.split("Ada's edit:")[-1] if "Ada's edit:" in out else True,
       "a deleted note is not read as Ada's own edit")

    test_04(remote, owm)
    print(f"\nall {passed} checks passed")
    shutil.rmtree(TMP, ignore_errors=True)


def test_04(remote, owm):
    print("0.4: setup and paths")
    gracehome = TMP / "gracehome"
    ow_as(gracehome, "setup", "--name", "Grace Hopper", "--email", "grace@example.com")
    prof = json.loads((gracehome / "profile.json").read_text())
    ok(prof["handle"] == "Grace" and prof["id_prefix"] == "grace", "setup takes the handle and the id prefix from the name")
    ok((gracehome / "vault" / "STYLE.md").read_text().startswith("# Grace Hopper's writing style") and (gracehome / ".git").exists(),
       "setup starts a style vault from the template, in a git repository")
    paths = json.loads(ow_as(gracehome, "paths", "--json"))
    ok(paths["style guide"] == str(gracehome / "vault" / "STYLE.md"), "paths shows the vault in the data home")
    old = subprocess.run([sys.executable, str(OW.parent / "ow"), "paths", "--json"], capture_output=True, text=True,
                         env=dict(os.environ, OW_HOME=str(gracehome)))
    ok(json.loads(old.stdout)["profile"] == str(gracehome / "profile.json"), "the old name ow and $OW_HOME still work")

    print("0.4: a coauthor's comment belongs to the coauthor; their own loop answers it")
    grace = TMP / "grace"
    sh("git", "clone", "--quiet", str(remote), str(grace))

    def grace_edit(fn):
        edit_as(grace, "Grace Hopper", "grace@example.com", fn)

    ow("learn", "demo", "--ack", *state()["pending_events"])
    grace_edit(lambda t: t.replace("\\section{Introduction}\n", "\\section{Introduction}\n%! Grace asks: define the policy first..\n")
            .replace("trains a policy on comparisons", "trains a policy on pairwise comparisons"))
    out = ow("watch", "demo", "--once", expect=1)
    ok("no comment ready" in out, "Ada's loop leaves Grace's comment alone")
    out = ow("status", "demo")
    ok("left to their authors: 1 comment(s) by Grace Hopper" in out, "status says whose comment it is")
    out = ow("learn", "demo")
    ok("pairwise" not in out, "Grace's edit is not evidence in Ada's vault")
    out = ow_as(gracehome, "init", "demo", "--remote", str(remote), "--main", "main.tex", "--protect", "ada")
    ok("comments by Grace Hopper are answered, ids grace1" in out, "Grace's loop answers Grace's comments, ids grace1, grace2, …")
    ycfg = json.loads((gracehome / "projects" / "demo" / "project.json").read_text())
    ok(ycfg.get("coauthor_prefixes") == ["c"], "init learns the prefix of Ada's notes already in the paper")
    out = ow_as(gracehome, "watch", "demo", "--interval", "0.2", timeout=30)
    ok("## grace1 · main.tex" in out and "define the policy first" in out and "## c" not in out,
       "Grace's loop sends Grace's comment as grace1, and nothing of Ada's")
    yrepo = gracehome / "projects" / "demo" / "repo" / "main.tex"
    yrepo.write_text(yrepo.read_text().replace("trains a policy on pairwise", "trains a policy $\\pi$ on pairwise"))
    ow_as(gracehome, "resolve", "demo", "grace1", "Named the policy at first use.")
    ok("\\claude[Grace]{grace1}{Grace asks: define the policy first}{Named the policy at first use.}" in yrepo.read_text(),
       "Grace's note names Grace, since the macro's default name is Ada")
    out = ow_as(gracehome, "push", "demo", "--no-compile")
    ok("answered grace1" in out, "Grace's loop publishes")
    ada_edit(lambda t: t.replace("{Named the policy at first use.}\n", "{Named the policy at first use.}\n%! say which policy..\n"))
    out = ow("watch", "demo", "--interval", "0.2", timeout=30)
    ok("## c15 · main.tex" in out and "Follow-up" not in out.split("## c15")[1].split("Refers to")[0],
       "Ada's comment under Grace's note is Ada's own, not a follow-up in Grace's thread")
    out = ow_as(gracehome, "watch", "demo", "--once", expect=1)
    ok("no comment ready" in out, "and Grace's loop leaves it alone")
    agent_edit(lambda t: t.replace("a policy $\\pi$ on", "a policy $\\pi$ (the model being trained) on"))
    ow("resolve", "demo", "c15", "Said which policy.")
    ok("\\claude{c15}{say which policy}{Said which policy.}" in (REPO / "main.tex").read_text(),
       "Ada's note needs no name: the macro's default is Ada")
    ow("push", "demo", "--no-compile")
    grace_edit(lambda t: "\n".join(l for l in t.split("\n") if not l.startswith("\\claude[Grace]{grace1}")))
    out = ow("learn", "demo")
    ok("grace1" not in out, "Grace accepting grace1 is not evidence for Ada")
    out = ow_as(gracehome, "learn", "demo")
    ok("grace1 · " in out and "closed" in out, "but it is for Grace, in Grace's own vault")
    ok("changed by others" in out and "then changed it" not in out,
       "Ada's later edit of that sentence is not read as Grace's rewrite")
    ow("learn", "demo", "--ack", *state()["pending_events"])

    print("0.4: a coauthor without a loop, through comments_from; a note macro from 0.3 is upgraded")
    jo = TMP / "jordan"
    sh("git", "clone", "--quiet", str(remote), str(jo))
    old_def = ["% overleaf-writer: Ada's handled comments with Claude's replies, shown in green until Ada deletes the line.",
               "\\usepackage{xcolor}", "\\providecolor{claudecol}{RGB}{34,120,40}",
               "\\providecommand{\\claude}[3]{{\\leavevmode\\color{claudecol}\\small[#1]\\ \\textbf{Ada:} #2\\quad"
               "\\textbf{Claude:} #3}}"]
    ada_edit(lambda t: t.replace("\n".join(owm.note_def("Ada", "Claude")), "\n".join(old_def)))
    ok("[3]{{" in (ADA / "main.tex").read_text(), "(the paper now has the 0.3 macro)")
    edit_as(jo, "Jordan Lee", "jo@example.com", lambda t: t.replace(
        "\\end{document}", "Jordan's closing paragraph.\n%! cite the survey here..\n\\end{document}"))
    ow("watch", "demo", "--once", expect=1)
    cfg_path = HOME / "projects" / "demo" / "project.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["comments_from"] = {"Jordan Lee": "Jordan"}
    cfg_path.write_text(json.dumps(cfg))
    out = ow("watch", "demo", "--interval", "0.2", timeout=30)
    ok("## c16 · main.tex" in out and "from Jordan Lee" in out, "listed in comments_from, Jordan's comment comes to Ada's loop")
    agent_edit(lambda t: t.replace("Jordan's closing paragraph.", "Jordan's closing paragraph, as surveyed by Smith."))
    ow("resolve", "demo", "c16", "Cited the survey.")
    text = (REPO / "main.tex").read_text()
    ok("\\claude[Jordan]{c16}{cite the survey here}{Cited the survey.}" in text, "the note names Jordan")
    ok("\\providecommand{\\claude}[4][Ada]" in text and owm.HIDE_LINE in text and "[3]{{" not in text
       and "\\claude{c15}" in text, "the 0.3 macro is upgraded, keeps Ada as its default, and gains the switch that hides notes")
    if shutil.which("latexmk"):
        out = ow("push", "demo", "-m", "cite the survey", timeout=180)
        ok("compiles" in out and "answered c16" in out, "old and new notes compile together")
    else:
        ow("push", "demo", "--no-compile")

    print("0.4: a paper in any git remote")
    gremote = TMP / "g.git"
    sh("git", "init", "--quiet", "--bare", "--initial-branch=master", str(gremote))
    glocal = TMP / "glocal"
    sh("git", "clone", "--quiet", str(gremote), str(glocal))
    (glocal / "main.tex").write_text(DOC)
    sh("git", "add", "-A", cwd=glocal)
    sh("git", "-c", "user.name=Ada Lovelace", "-c", "user.email=ada@example.com", "commit", "--quiet", "-m", "first", cwd=glocal)
    sh("git", "push", "--quiet", "origin", "master", cwd=glocal)
    out = ow("init", "gdemo", "--git", str(gremote), "--main", "main.tex", "--protect", "ada")
    ok("project gdemo (git)" in out, "init registers a git remote")
    edit_as(glocal, "Ada Lovelace", "ada@example.com", lambda t: t.replace(
        "The model has three parts.", "The model has three components.\n%! name them..").replace(
        "The second paragraph stays", "The second paragraph, unchanged, stays"), message="intro edits")
    out = ow("watch", "gdemo", "--interval", "0.2", timeout=30)
    ok("## c1 · main.tex" in out and "name them" in out, "a comment pushed to a git remote arrives")
    ok("{+paragraph, unchanged,+}" in out and "[-parts.-]{+components.+}" in out,
       "Ada's own commit is evidence, whatever its message")
    grepo = HOME / "projects" / "gdemo" / "repo" / "main.tex"
    grepo.write_text(grepo.read_text().replace("three components.", "three components: a sampler, a judge and a reference."))
    ow("resolve", "gdemo", "c1", "Named them.")
    out = ow("push", "gdemo", "--no-compile")
    log = sh("git", "--git-dir", str(gremote), "log", "-1", "--format=%s").stdout
    ok("answered c1" in out and log.startswith("pairtex: Answer c1"), "the answer is pushed to the remote")

    print("0.4: a paper in a local folder, edited in any editor")
    fd = TMP / "paper"
    fd.mkdir()
    (fd / "main.tex").write_text(DOC)
    (fd / "main.aux").write_text("junk")
    (fd / "main.pdf").write_bytes(b"%PDF-1.5 build output")
    (fd / "fig.pdf").write_bytes(b"%PDF-1.5 a figure")
    out = ow("init", "fdemo", "--folder", str(fd), "--main", "main.tex", "--protect", "ada")
    frepo = HOME / "projects" / "fdemo" / "repo"
    ok("project fdemo (folder)" in out and (frepo / "fig.pdf").exists() and not (frepo / "main.aux").exists()
       and not (frepo / "main.pdf").exists(), "the folder's sources are recorded; build files and the main PDF are not")

    def save(fn):
        path = fd / "main.tex"
        path.write_text(fn(path.read_text()))

    save(lambda t: t.replace("The model has three parts.", "The model has three parts.\n%! name them..")
         .replace("In this section we will basically", "Here we will basically"))
    out = ow("watch", "fdemo", "--interval", "0.2", timeout=30)
    ok("## c1 · main.tex" in out and "name them" in out, "a comment saved in the folder arrives")
    ok("[-In this section-]{+Here+}" in out, "the author's own saved edit is evidence")
    (frepo / "main.tex").write_text((frepo / "main.tex").read_text().replace(
        "The model has three parts.", "The model has three parts: a sampler, a judge and a reference."))
    ow("resolve", "fdemo", "c1", "Named them.")
    save(lambda t: t.replace("\\section{Introduction}", "\\section{Introduction and scope}"))
    out = ow("push", "fdemo", "--no-compile")
    t = (fd / "main.tex").read_text()
    ok("published" in out and "a sampler, a judge and a reference." in t and "\\claude{c1}{name them}{Named them.}" in t
       and "Introduction and scope" in t, "push writes the edit and the note into the folder, keeping the author's newer save")
    ok(not list(fd.glob(".*-tmp")), "no temporary files are left behind")
    save(lambda t: t.replace("{Named them.}\n", "{Named them.}\n%! shorter..\n"))
    out = ow("watch", "fdemo", "--interval", "0.2", timeout=30)
    ok("## c2" in out and "Follow-up in thread c1" in out, "a comment under the note is a follow-up")
    (frepo / "main.tex").write_text((frepo / "main.tex").read_text().replace("a sampler, a judge and a reference.",
                                                                             "sampler, judge, reference."))
    ow("resolve", "fdemo", "c2", "Shorter.")
    save(lambda t: t.replace("parts: a sampler, a judge", "parts: one sampler, a judge"))
    out = ow("push", "fdemo", "--no-compile", expect=3)
    ok("nothing was published" in out and "one sampler, a judge" in (fd / "main.tex").read_text(),
       "when the author rewrote the same line, nothing is written and the author's text stays")

    have_xe = shutil.which("xelatex") and sh("kpsewhich", "ctex.sty", check=False).stdout.strip()
    if have_xe:
        print("0.4: XeLaTeX with Chinese text: the note prints the comment as written")
        xd = TMP / "xpaper"
        xd.mkdir()
        (xd / "main.tex").write_text("% !TEX program = xelatex\n\\documentclass{article}\n\\usepackage{ctex}\n"
                                     "\\begin{document}\n这是第一段。The loop works.\n%! 这句太短..\n\\end{document}\n")
        ow("init", "xdemo", "--folder", str(xd), "--main", "main.tex")
        out = ow("watch", "xdemo", "--interval", "0.2", timeout=30)
        ok("## c1" in out and "这句太短" in out, "the Chinese comment arrives")
        xrepo = HOME / "projects" / "xdemo" / "repo" / "main.tex"
        xrepo.write_text(xrepo.read_text().replace("The loop works.", "The loop works, and it says why."))
        ow("resolve", "xdemo", "c1", "加了原因。Added the reason.")
        t = xrepo.read_text()
        ok("\\claude{c1}{这句太短}{加了原因。Added the reason.}" in t and "%!c1" not in t,
           "with XeLaTeX and ctex the Chinese comment and reply go in the note itself")
        out = ow("push", "xdemo", timeout=300)
        ok("compiles (xelatex" in out and "published" in out, "the compile check uses XeLaTeX, from the main file's magic line")
    else:
        print("  (skipped: XeLaTeX with ctex is not installed)")

    print("0.4: before submission, check and clean")
    out = ow("check", "demo", expect=1)
    ok("notes (" in out and "c15" in out and "note definitions (" in out and "threads (" in out,
       "check lists the notes, threads and macro left in the paper")
    ok("coauthor notes (" in out and "\\ada{check this}" in out, "and the coauthor notes")
    clean = TMP / "clean"
    out = ow("clean", "demo", "--out", str(clean), *(["--compile"] if shutil.which("latexmk") else []), timeout=300)
    t = (clean / "main.tex").read_text()
    ok("\\claude" not in t and "%!" not in t and "%?" not in t and "[[" not in t and "claudecol" not in t
       and "hideclaudenotes" not in t, "the clean copy has no notes, comments, brackets or note macro")
    ok("\\ada{check this}" in t and "still there: " in out, "coauthor notes stay, with a warning")
    if shutil.which("latexmk"):
        ok("compiles:" in out, "the clean copy compiles")
    src = "a % note\n%! c..\n\\begin{verbatim}\n%! kept\n\\end{verbatim}\nb\\% c %\n\\claude{c1}{x}{y}\n"
    new, counts = owm.clean_tex(src)
    ok(new == "a %\n\\begin{verbatim}\n%! kept\n\\end{verbatim}\nb\\% c %\n" and counts["notes"] == 1,
       "clean keeps verbatim text and the % that ends a line")
    new, _ = owm.clean_tex("x % keep me\n% and me\n%? but not me\n", keep_comments=True)
    ok(new == "x % keep me\n% and me\n", "--keep-comments keeps ordinary comments only")

    print("0.4: migrate data from the code folder (the layout before 0.4)")
    leg, nh = TMP / "legacy", TMP / "newhome"
    (leg / "style").mkdir(parents=True)
    shutil.copy(HOME / "style" / "STYLE.md", leg / "style" / "STYLE.md")
    shutil.copy(HOME / "style" / "evidence.jsonl", leg / "style" / "evidence.jsonl")
    shutil.copytree(HOME / "projects" / "gdemo", leg / "projects" / "gdemo")
    lock = leg / "projects" / "gdemo" / "watch.lock"
    lock.write_text(json.dumps({"pid": os.getpid(), "started": "now"}))
    out = ow_as(nh, "migrate", "--from", str(leg), "--to", str(nh), expect=5)
    ok("stop the watchers first: gdemo" in out, "migrate refuses while a watcher runs")
    lock.unlink()
    ow_as(nh, "migrate", "--from", str(leg), "--to", str(nh))
    ok((nh / "vault" / "STYLE.md").exists() and (nh / "projects" / "gdemo" / "repo").exists()
       and not (leg / "style").exists() and not (leg / "projects").exists(), "the vault and the projects move to the data home")
    prof = json.loads((nh / "profile.json").read_text())
    ok(prof["name"] == "Ada Lovelace" and prof["id_prefix"] == "c", "the profile keeps the owner's name and the c prefix")
    out = ow_as(nh, "status", "gdemo")
    ok("answers: Ada Lovelace (Ada)" in out and "1 pushed" in out, "the moved project runs unchanged")


if __name__ == "__main__":
    main()
