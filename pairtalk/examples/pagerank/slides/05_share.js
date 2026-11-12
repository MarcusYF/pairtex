// The equation: PageRank is the surfer's long-run share of time.
Deck.slide({
  id: 'SHARE', title: "PageRank is the surfer's share of time", steps: 2,
  notes: [
    "Let me write that down. Call r i the share of time on page i, and d j the number of links out of page j. The surfer reaches page i by clicking from a page j that links to it, and from j it picks that link with chance one over d j. So in the long run, r i is the sum, over the pages j that link to i, of r j divided by d j. This is exactly the recursion from before: a vote from j is worth j's own rank, split over j's links.",
    "Put the one-over-d-j's in a matrix M, column by column, and the whole system is one line: r equals M r.",
    "So PageRank is an <b>eigenvector</b> of the link matrix, with eigenvalue one. Two questions follow: does such an r always exist, and is it unique? On a real web, the answer is no, and the next slide shows why."
  ],
  html: `
    <style>
      .slide[data-id="SHARE"] .sh-eq { position: absolute; left: 0; right: 0; top: 214px; text-align: center; font-size: 64px; }
      .slide[data-id="SHARE"] .sh-def { position: absolute; left: 470px; top: 430px; font-size: 40px; line-height: 1.25; }
      .slide[data-id="SHARE"] .sh-def > div { margin-bottom: 26px; }
      .slide[data-id="SHARE"] .sh-def .sh-s { display: inline-block; width: 150px; }
      .slide[data-id="SHARE"] .sh-mat { position: absolute; left: 0; right: 0; top: 760px; text-align: center; font-size: 56px; }
      .slide[data-id="SHARE"] .sh-where { font-size: 40px; color: var(--ink2); margin-left: 60px; }
      .slide[data-id="SHARE"] .sh-eig { position: absolute; left: 0; right: 0; top: 900px; text-align: center; font-size: 40px; }
      .slide[data-id="SHARE"] .sh-rmr { position: relative; display: inline-block; }
      .slide[data-id="SHARE"] .sh-ring { position: absolute; left: -26px; right: -26px; top: -14px; bottom: -14px; border: 4px solid var(--gold); border-radius: 12px; }
    </style>
    <div class="sh-eq" data-in="0">\\( r_i = \\sum_{j \\to i} \\frac{r_j}{d_j} \\)</div>
    <div class="sh-def" data-in="0" data-dim="1">
      <div><span class="sh-s">\\( r_i \\)</span>share of time the surfer spends on page \\( i \\)</div>
      <div><span class="sh-s">\\( d_j \\)</span>number of links out of page \\( j \\)</div>
      <div><span class="sh-s">\\( j \\to i \\)</span>page \\( j \\) links to page \\( i \\)</div>
    </div>
    <div class="sh-mat" data-in="1"><span class="sh-rmr">\\( r = M r \\)<span class="sh-ring" data-in="2"></span></span><span class="sh-where">with \\( M_{ij} = 1/d_j \\) if \\( j \\to i \\), else \\( 0 \\)</span></div>
    <div class="sh-eig c-gold" data-in="2">an eigenvector of \\( M \\), with eigenvalue 1</div>`
});
