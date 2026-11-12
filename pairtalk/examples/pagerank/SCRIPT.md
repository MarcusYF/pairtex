# Talk script

Edit the text between each pair of `slide-note` markers and save. The agent watching this talk picks up your edits;
without one, run `pairtalk script apply <talk>`. Click 0 is the note on entry. Keep the headings and the marker lines.
`<b>...</b>` marks a bold cue. Reload the deck to see the changes.

<!-- Base hashes prevent an old script from overwriting newer slide notes. -->

## 1 · How PageRank ranks the web (TITLE)

### TITLE.0 · on entry
<!-- slide-note {"sid":"TITLE","k":0,"base":"65bb94a2cbf5f60caaf8a19e81812f905dffc808420f5d03030699a3c9f712e5"} -->
Thank you for coming. In the next eight minutes I want to answer one question: when thousands of pages match your search, <b>which one should come first</b>? The answer that made web search work is called PageRank, and it fits on one slide: a random surfer, a matrix, and one eigenvector.
<!-- /slide-note -->

## 2 · Many pages match. Which should come first? (HOOK)

### HOOK.0 · on entry
<!-- slide-note {"sid":"HOOK","k":0,"base":"c8d5bffd1a085055b9c2b2e1f832ea82b5448402cca8e2a91b9fa0790beb9934"} -->
Let me start with something you do every day. You type a query, say <b>pagerank</b>, into a search box.
<!-- /slide-note -->

### HOOK.1 · click 1
<!-- slide-note {"sid":"HOOK","k":1,"base":"85919c62c0ba78c5305a77595198a10881796e1550e473dd8c082d5cbfd797fd"} -->
Thousands of pages contain that word. Finding them is the easy part: an index of words does it in milliseconds.
<!-- /slide-note -->

### HOOK.2 · click 2
<!-- slide-note {"sid":"HOOK","k":2,"base":"19b3ab77051311197bfba6ee97ef428a0c9f4368065b454edbe92d609ee81fe5"} -->
The hard part is the <b>order</b>. You will read the first three results, maybe five. So the real question is: which page goes first? Word counts cannot answer it, because anyone can repeat a word. We need a signal the page cannot write about itself.
<!-- /slide-note -->

## 3 · A link is a vote, and some voters count more (VOTES)

### VOTES.0 · on entry
<!-- slide-note {"sid":"VOTES","k":0,"base":"05e32a06096c191f7f8130893417e79eea12d06baecdba05c46764f6a96a9508"} -->
Here is a tiny web: five pages, A to E.
<!-- /slide-note -->

### VOTES.1 · click 1
<!-- slide-note {"sid":"VOTES","k":1,"base":"a556b84045dd7a98c1ad4ca872b07472b6088111486fe90abd3354ab5acad6c5"} -->
And here are their links. The idea behind PageRank is that <b>a link is a vote</b>. When page D links to page A, D's author is telling us A is worth reading.
<!-- /slide-note -->

### VOTES.2 · click 2
<!-- slide-note {"sid":"VOTES","k":2,"base":"aa9ea71d20717be24ac7c47e45fc400b98d51553809fa5c0597ab202fb265eed"} -->
So the simplest score counts votes: links in. A and C get three each, B and D one, E none. By this count, C ties for first and B is far behind.
<!-- /slide-note -->

### VOTES.3 · click 3
<!-- slide-note {"sid":"VOTES","k":3,"base":"9f7eb40798616a6f6f0b2de57ebe76b4bcff628507dddef56af7d0bbe15acff7"} -->
But look at where B's one vote comes from: from A, the page everybody points to, and it is A's <b>only</b> link. A vote from an important page should count more. That makes the score recursive: a page is important if important pages link to it. Next, a way to make that precise.
<!-- /slide-note -->

## 4 · A random surfer follows links forever (SURFER)

### SURFER.0 · on entry
<!-- slide-note {"sid":"SURFER","k":0,"base":"11f49642382e46b211fca4d4443b853ce28d5dc869fec53c79e4d694ca18f2c9"} -->
Imagine a surfer who starts on some page, here E, and never stops. On every page, the surfer picks one of its links at random and follows it.
<!-- /slide-note -->

### SURFER.1 · click 1
<!-- slide-note {"sid":"SURFER","k":1,"base":"af676937f76401f30354b2d6d743a58a16a7e4aa47f544069f62050eb3b50697"} -->
Let us watch eight clicks. From E to C, from C to A, A to B, and so on. The counters keep track of how often the surfer has been on each page. It keeps coming back to A and to B.
<!-- /slide-note -->

### SURFER.2 · click 2
<!-- slide-note {"sid":"SURFER","k":2,"base":"068b17466056c6417ddc218c73d159296df0610d12f1d2b5a75df5cf963c00dc"} -->
Now let the surfer run for a very long time. The share of time spent on each page settles down: about 37 percent on A, 35 on B, 21 on C, and only 4 and 3 percent on D and E. <b>That share of time is PageRank.</b>
<!-- /slide-note -->

## 5 · PageRank is the surfer's share of time (SHARE)

### SHARE.0 · on entry
<!-- slide-note {"sid":"SHARE","k":0,"base":"cf19371f5ecdcb6725bd0e58972710c08031dca30359659ee546cd7f40aa9314"} -->
Let me write that down. Call r i the share of time on page i, and d j the number of links out of page j. The surfer reaches page i by clicking from a page j that links to it, and from j it picks that link with chance one over d j. So in the long run, r i is the sum, over the pages j that link to i, of r j divided by d j. This is exactly the recursion from before: a vote from j is worth j's own rank, split over j's links.
<!-- /slide-note -->

### SHARE.1 · click 1
<!-- slide-note {"sid":"SHARE","k":1,"base":"ddf311393f6b592f5fc4445944b59e7c506ebafe9999aba524892706f793bfff"} -->
Put the one-over-d-j's in a matrix M, column by column, and the whole system is one line: r equals M r.
<!-- /slide-note -->

### SHARE.2 · click 2
<!-- slide-note {"sid":"SHARE","k":2,"base":"2d155655539141cf27046e1cb3b02d7e9d929e22f86b258f5d7137e0c864d03b"} -->
So PageRank is an <b>eigenvector</b> of the link matrix, with eigenvalue one. Two questions follow: does such an r always exist, and is it unique? On a real web, the answer is no, and the next slide shows why.
<!-- /slide-note -->

## 6 · Teleporting frees a stuck surfer (STUCK)

### STUCK.0 · on entry
<!-- slide-note {"sid":"STUCK","k":0,"base":"c1848493e552c0eddece0112bb4d84b3dbde53bb03bd4c69bdd728288112620c"} -->
The first problem is a <b>dead end</b>: a page with no links out, like Y here. The surfer arrives and has nowhere to go.
<!-- /slide-note -->

### STUCK.1 · click 1
<!-- slide-note {"sid":"STUCK","k":1,"base":"67eaa5a73fc53f728873e14b4fd3fc38cad650a4ca7a639a5d88d553617ea170"} -->
The second is a <b>trap</b>: P and Q link only to each other. Once the surfer is in, it circles there forever, and every page outside gets a share of zero.
<!-- /slide-note -->

### STUCK.2 · click 2
<!-- slide-note {"sid":"STUCK","k":2,"base":"ca9117a0b3c371540b8926f1d4a08f0dd8a31ab8983580ccc70cab3d2e72cb16"} -->
The fix is simple. At every step, with a small chance, the surfer ignores the links and <b>jumps to a page chosen at random</b>. Dead ends and traps can no longer hold it.
<!-- /slide-note -->

### STUCK.3 · click 3
<!-- slide-note {"sid":"STUCK","k":3,"base":"669e61ac383fb1348a9f536e3d0cf584f66ed71222db4085c03c0097bd7ebe73"} -->
In the formula, that is one extra term. With chance alpha the surfer follows a link, as before; with chance one minus alpha it jumps, and each of the n pages gets an equal share of that jump. The usual choice is alpha equal to 0.85: about six clicks, on average, before a jump.
<!-- /slide-note -->

## 7 · With teleporting, there is exactly one ranking (THEOREM)

### THEOREM.0 · on entry
<!-- slide-note {"sid":"THEOREM","k":0,"base":"31b0a219625807e8abbd4bcd181227c47ce7673f76e9630c303dfa4a1519bcfc"} -->
And with the jump, both questions have a clean answer. If every page has a link out, which we arrange by letting a dead end link to every page, and alpha is strictly between zero and one, then there is <b>exactly one</b> ranking: one vector r, nonnegative, summing to one, that solves the equation. This is the Perron–Frobenius theorem at work: thanks to the jump, every page can reach every other page.
<!-- /slide-note -->

### THEOREM.1 · click 1
<!-- slide-note {"sid":"THEOREM","k":1,"base":"1c08a82672bdb76b030546772efabfcb7d6ff64d4eff308372a7a03ff7084081"} -->
It also tells us how to compute it. Start from any guess, apply the update again and again, and the error shrinks by a factor of at least alpha at every step. With alpha 0.85, that is a guarantee of fifteen percent less error per step. Let us see how fast it really goes.
<!-- /slide-note -->

## 8 · The error shrinks geometrically (CONVERGE)

### CONVERGE.0 · on entry
<!-- slide-note {"sid":"CONVERGE","k":0,"base":"ccd7a1dc9d3bf9133f7801b8a4339285a7a5ac29d92dd90c0920db2536533434"} -->
Here is power iteration on our five-page web. The horizontal axis counts the steps; the vertical axis is the error, the distance to the true ranking, on a log scale, so a straight line means a constant factor per step.
<!-- /slide-note -->

### CONVERGE.1 · click 1
<!-- slide-note {"sid":"CONVERGE","k":1,"base":"3f9e347310bf3ae2f37bf791486f7c929e3610bb4d6620f56d7f5f7fa22ed056"} -->
Starting from the uniform guess, these are the measured errors. After ten steps the error is about one in a thousand; after twenty, about one in a hundred thousand.
<!-- /slide-note -->

### CONVERGE.2 · click 2
<!-- slide-note {"sid":"CONVERGE","k":2,"base":"0f85caf7ba7ecf1d19f30b5b7b3bf022140cf96445378c4d206120f84547e26f"} -->
The dashed line is what the theorem guarantees: a factor 0.85 per step. The real error falls much faster here, because this web is small and well connected. On the whole web, the guarantee is what you plan for: about 57 steps cut the error ten thousand times, whatever the size of the web. That is why PageRank was practical: one pass over the links per step, a few dozen steps.
<!-- /slide-note -->

## 9 · One link from A puts B above C (RANKING)

### RANKING.0 · on entry
<!-- slide-note {"sid":"RANKING","k":0,"base":"891fd238382f99df19747676d8a33af903a2320152d7bd3be90be3b98a8d25cf"} -->
So here is the ranking of our five pages. A first, with 0.37; then B, with 0.35; then C, with 0.21; D and E far behind.
<!-- /slide-note -->

### RANKING.1 · click 1
<!-- slide-note {"sid":"RANKING","k":1,"base":"efbcf3a8853cb38a97d3a04907e1b75d9a6cd6b60a46887298e775a98085ddb3"} -->
Now compare with the simple vote count. C has three links in, B only one. Yet B ranks above C, because B's one link comes from A, the most important page, and it is the only link A gives. This is the whole idea in one picture: <b>a vote is worth the rank of the voter</b>, divided among its links.
<!-- /slide-note -->

## 10 · Takeaways (TAKEAWAYS)

### TAKEAWAYS.0 · on entry
<!-- slide-note {"sid":"TAKEAWAYS","k":0,"base":"2266c2a2b2aaf41bbc12088a65d202adc93fe5f78b07f2eba3f9903f3592f110"} -->
To sum up. First: a link is a vote, and a vote is worth the rank of the page that casts it.
<!-- /slide-note -->

### TAKEAWAYS.1 · click 1
<!-- slide-note {"sid":"TAKEAWAYS","k":1,"base":"356a539db2ad799d145f30892486a08f04e00eb3bd79c70a33e24e54acd9d8ac"} -->
Second: PageRank is the share of time a random surfer spends on each page, an eigenvector of the link matrix.
<!-- /slide-note -->

### TAKEAWAYS.2 · click 2
<!-- slide-note {"sid":"TAKEAWAYS","k":2,"base":"edb82164eca5d821486e3da681a816fc4f95de741d4f3e577a93b7dbd309fff5"} -->
Third: the random jump makes that ranking unique, and power iteration finds it in a few dozen passes over the links, on any web.
<!-- /slide-note -->

## 11 · Thank you (THANKS)

### THANKS.0 · on entry
<!-- slide-note {"sid":"THANKS","k":0,"base":"515b2bd96bdedff15385000d02a4ab5b922b82580f72c0a175a54763dde57642"} -->
Thank you. I am happy to take your questions.
<!-- /slide-note -->

## 12 · The same update on the whole web (SCALE)

### SCALE.0 · on entry
<!-- slide-note {"sid":"SCALE","k":0,"base":"2b5a6226d1d09dcef9961e3684f108b398856595fd6e2515d37a697298c2b8f7"} -->
This slide is for the question of scale. Each step is one pass over all links, so the cost per step grows with the number of links, not with the square of the number of pages. The guarantee from the theorem does not depend on the size of the web at all: 57 steps cut the error ten thousand times at alpha 0.85. Dead ends are handled by letting them link to every page.
<!-- /slide-note -->
