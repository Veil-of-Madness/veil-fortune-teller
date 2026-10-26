// Writes the final reading for three drawn cards.
// The page sends only card ids and whether each is reversed; the prompt is built
// here from cards.json, so the endpoint can't be used for anything but readings.
// Needs the ANTHROPIC_API_KEY environment variable, set in Netlify's site settings.
import cards from "../../cards.json";

const MODEL = "claude-haiku-5-5";
const POSITIONS = ["What has passed", "What stands now", "What approaches"];
const TYPES = {
  Attack: "Attack (a blade: force, conflict, action)",
  Effect: "Effect (an eye: change, insight, the uncanny)",
  Block: "Block (a shield: protection, patience, endurance)",
};
const byId = Object.fromEntries(cards.map((c) => [c.id, c]));

const SYSTEM = `You are the reader for a tarot deck made from the cards of a Lovecraftian deckbuilding game.
Write the final reading for a three-card spread: what has passed, what stands now, and what approaches.

Voice: ominous, literary and intimate, like a fortune teller who has seen the deep and come back. Speak directly to the querent as "you". Cosmic dread, the sea, dreams, old knowledge and hidden costs are welcome; gore is not.

Each card comes with its omen (its tarot title), its meaning in this position and its keywords. Do not restate the three meanings one after another. Weave the cards into one story: how the past card leads into the present one, how the present one shapes what approaches, and what the three say together. Name each card by its omen at least once. A reversed card speaks of its shadow side; treat it as a warning or something turned inward.

Length: 140 to 200 words, in two or three paragraphs, then one final short line of counsel on its own.
Format: plain text only, paragraphs separated by a blank line. No headings, no lists, no markdown, no preamble.`;

function describe(pick, i) {
  const c = byId[pick.id];
  return [
    `${POSITIONS[i]}: ${c.omen}${pick.reversed ? " (reversed)" : ""}`,
    `Game card: ${c.name}, type ${TYPES[c.source] || c.source}`,
    `Meaning here: ${pick.reversed ? c.reversed : c.upright}`,
    `Keywords: ${c.keywords.join(", ")}`,
  ].join("\n");
}

const json = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Use POST" });
  if (!process.env.ANTHROPIC_API_KEY) return json(500, { error: "ANTHROPIC_API_KEY is not set" });

  let picks;
  try {
    ({ picks } = await req.json());
  } catch {
    return json(400, { error: "Send JSON: { picks: [{ id, reversed }, x3] }" });
  }
  const valid =
    Array.isArray(picks) &&
    picks.length === 3 &&
    picks.every((p) => p && byId[p.id] && typeof p.reversed === "boolean") &&
    new Set(picks.map((p) => p.id)).size === 3;
  if (!valid) return json(400, { error: "Send exactly three different card ids" });

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 2000,
        system: SYSTEM,
        messages: [{ role: "user", content: picks.map(describe).join("\n\n") }],
      }),
    });
    if (!res.ok) {
      console.error("Claude API error", res.status, await res.text());
      return json(502, { error: "The reader is silent right now" });
    }
    const data = await res.json();
    const reading = data.content.filter((b) => b.type === "text").map((b) => b.text).join("\n").trim();
    if (!reading) return json(502, { error: "Empty reading" });
    return json(200, { reading });
  } catch (err) {
    console.error(err);
    return json(502, { error: "The reader is silent right now" });
  }
};

export const config = { path: "/api/reading" };
