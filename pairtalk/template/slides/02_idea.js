// One idea per slide, one step of it per click. data-in="k" shows an element from click k on; data-dim="k" fades it.
Deck.slide({
  id: 'IDEA', title: 'One idea per slide, one step per click', steps: 2,
  notes: [
    "On entry: say the slide's point first.",
    "Click 1: the second part appears as you say it.",
    "Click 2: the first part fades, and the slide settles on what to remember. End with a bridge to the next slide."
  ],
  html: `
    <div class="rows body" style="left:300px;top:330px;width:1320px">
      <div data-in="0" data-dim="2"><span class="num">1</span>The first thing the audience should see</div>
      <div data-in="1"><span class="num">2</span>The step that builds on it</div>
      <div data-in="2" class="c-blue"><span class="num">3</span>What to remember</div>
    </div>`
});
