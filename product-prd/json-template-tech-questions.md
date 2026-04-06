---
title: "JSON Template Tech Questions – LingoAce Interview Prep"
category: product-prd
subcategory: interview-preparation
source_id: 4253649a-af71-4d93-b8e5-ae03b6474845
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# JSON Template Tech Questions – LingoAce Interview Preparation

## Overview

Anticipated technical and product strategy questions from a LingoAce interviewer (VP of Product, Hiring Manager, or Lead Engineer) specifically about the JSON-Driven Gamified Template Engine architecture. Categorized by interview dimension.

---

## 1. Product Strategy & Scalability

**"Why did you choose a JSON-driven declarative architecture instead of building individual React components for each game?"**
- Answer context: Decoupling engineering from content creation. The JSON schema means new game types don't require code deployment — content teams can author and publish independently.

**"If we wanted to launch a brand new game type next week, does this require a database migration, or is the schema flexible enough to handle it?"**
- Answer context: The polymorphic `Task` object uses optional configuration objects. New game types only need a new config object in the JSON — no database schema migration needed.

**"How does this architecture support rapid experimentation? Can a content creator A/B test a 'Card Flip' vs. a 'Crossword' for the same lesson without engineering help?"**
- Answer context: Yes — the content creator changes `templateType` in the JSON config. The Stage Viewer previews both versions. No engineering involvement.

---

## 2. Gamification & UX

**"You implemented a 'Select Until Correct' loop. Why did you choose a 'Mastery Loop' model over a standard 'Pass/Fail' model, and how did it impact user retention?"**
- Answer context: `selectUntilCorrect: true` flag. Mastery loops prevent students from giving up after a wrong answer. Directly contributed to quiz completion rising from 40% to 89%.

**"How did you handle user feedback for wrong answers? Did the system just say 'Try Again,' or did it offer pedagogical value?"**
- Answer context: The `feedback` payload on each option is pushed to the Chatbot Window (Greenline/Ray). Wrong answers trigger character-delivered explanations, not just "Try Again" text.

**"For subjective questions (e.g., 'What is your favorite color?'), how did the UI differentiate between a 'choice' and a 'correct answer' to avoid confusing the child?"**
- Answer context: If `isCorrect` field is omitted in JSON, the engine applies a Purple Highlight (neutral) instead of Green (success) or Red (error).

**"How did you balance high-quality visuals with performance in low-bandwidth regions? We have users globally."**
- Answer context: Used Lottie (vector JSON) animations instead of MP4 files. Same visual quality, tiny file size, instant load even on 3G.

---

## 3. Technical Logic & Edge Cases

**"Walk me through the validation logic for the 'Drag & Drop' engine. How does the system know if an item dropped in 'Bucket B' is correct?"**
- Answer context: The `categories` array maps each category to its valid `options` array. When item A is dropped into Bucket B, the frontend checks if item A's ID exists in Bucket B's `options` array.

**"In the 'Card Flip' memory game, how did you handle state conflicts? If a user clicks a third card while two are already flipping, what happens?"**
- Answer context: `multiFlipsAllowed: false` creates a mutex state. The third click is blocked/ignored until the existing pair resolves (match revealed or cards flipped back).

**"For the 'Hotspot' engine, how did you manage click detection on irregular shapes? A standard HTML div is a rectangle."**
- Answer context: `MapArea` objects with `shape` (circle/polygon) and `coords` arrays. An invisible SVG overlay calculates if cursor X/Y falls within the defined polygon coordinates.

**"How does the Crossword engine handle intersecting inputs? If I change a letter in 1-Down, does it break the state of 3-Across?"**
- Answer context: `CrosswordLabel` objects bind clues to specific grid coordinates (row, col). The engine validates by intersection — changing a letter updates state for all words sharing that coordinate.

---

## 4. Operations & Content Production

**"This system moves the burden of logic from engineers to content creators. How did you ensure the content team didn't write broken JSON?"**
- Answer context: The split-screen CMS (Editor + Stage Viewer) provides instant visual feedback. Template Guide sets strict constraints. Stage Viewer highlights layout overflows before publish.

**"How does the 'Rich Text' array work? If a curriculum designer wants to embed a modal trigger inside a paragraph, is that possible without code?"**
- Answer context: `RichText` array mixes strings with objects like `{ type: "link" }` or `{ type: "prompt" }`. The renderer parses the array and injects interactive React components into paragraph text.

---

## 5. The "Bonus" Trap Question

**"If we moved to this JSON-schema model, wouldn't it limit creativity? How do you prevent every lesson from feeling like a rigid template?"**
- Defense: Lottie animations allow dynamic, unique visual assets in rigid structures. `RichText` array enables dynamic component injection into any content. Polymorphic architecture (e.g., Memory Game vs. Standard Flip within the same card flip shell) allows endless variants from the same technical foundation.

## Relevance Tags
- `interview-prep` `lingoace` `json-template` `gamification` `technical-questions` `product-strategy`
