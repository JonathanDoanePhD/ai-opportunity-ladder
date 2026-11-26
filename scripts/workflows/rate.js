export const meta = {
  name: 'ai-opportunity-ladder-rate',
  description: 'Rate O*NET tasks for AI capability, speedup, human relationship and physical presence per protocol, writing validated JSON to disk',
  phases: [{ title: 'Tag', detail: 'one agent per batch of about 200 tasks' }],
}
const ROOT = '/home/user/claude_projects/projects/11-ai-opportunity-ladder'
const SCHEMA = {
  type: 'object',
  properties: { batch: { type: 'string' }, n_records: { type: 'integer' }, n_ai_capable: { type: 'integer' }, valid: { type: 'boolean' }, issues: { type: 'string' } },
  required: ['batch', 'n_records', 'n_ai_capable', 'valid', 'issues'],
}
// args: {jobs: [{pass: 'main'|'reference', batch: 'batch_0001', model?: 'sonnet'}]}
const prompt = (j) => `You are rating O*NET job tasks for a research study of how AI affects career pathways for young people.
Another rater rates some batches independently: do NOT open anything under ${ROOT}/data/coded/ except your own output file.

1. Read ${ROOT}/docs/protocol.md and follow it exactly.
2. Read the input batch ${ROOT}/data/interim/batches/task/${j.batch}.jsonl (one JSON record per line: id = O*NET task id, occupation, task). Read EVERY task in full (print in chunks), keeping each occupation in mind. Decide each task's four ratings yourself, one task at a time: do NOT use keyword matching, rule tables or regex to assign ratings (a script may only write the ratings you decided, keyed by id).
3. For every record produce one object with exactly these keys: id, ai_alone, ai_speedup, human_core, physical, notes. "id" is the task id string. notes: at most 8 words naming what the task acts on, in your own words.
4. Write the JSON list to ${ROOT}/data/coded/${j.pass}/${j.batch}.json (create folders if needed; a short Python script that maps your ratings by id is fine).
5. Run: python3 -I ${ROOT}/scripts/validate.py ${ROOT}/data/coded/${j.pass}/${j.batch}.json and fix until it prints VALID.
6. Keep ALL temporary files in your PRIVATE folder ${ROOT}/data/interim/tmp/${j.pass}_${j.batch}/ (create it). Never use the shared scratchpad or /tmp: other agents run at the same time. Build the output by matching each record's id, never by position. Do not modify any other files. Do not run git.
Return counts from your final file (n_ai_capable = number of tasks you rated ai_alone 2 or 3); valid=true only if the validator printed VALID. In "issues", confirm you rated every task individually and note hard calls briefly.`
// shorthand: args {main: [...batches], reference: [...batches], model: 'sonnet'} -> jobs (reference interleaved, default model)
if (!args.jobs) {
  const jobs = (args.main || []).map(b => ({ pass: 'main', batch: b, model: args.model || 'sonnet' }))
  ;(args.reference || []).forEach((b, k) => jobs.splice(Math.min(jobs.length, 6 + k * 12), 0, { pass: 'reference', batch: b }))
  args.jobs = jobs
}
log(`Tagging ${args.jobs.length} batch(es)`)
const results = await parallel(args.jobs.map(j => () =>
  agent(prompt(j), { label: `${j.pass} ${j.batch}`, phase: 'Tag', schema: SCHEMA, ...(j.model ? { model: j.model } : {}) })))
const ok = results.filter(Boolean)
log(`Done: ${ok.filter(r => r.valid).length}/${args.jobs.length} valid`)
return ok
