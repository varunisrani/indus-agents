/**
 * AI Client Module
 * Placeholder - communicates with backend proxy
 */

export async function chat(prompt) { return { text: 'Demo response' }; }
export async function explain(command) { return { text: 'Demo explanation' }; }
export async function suggest(task) { return { text: 'Demo suggestion' }; }

export default { chat, explain, suggest };