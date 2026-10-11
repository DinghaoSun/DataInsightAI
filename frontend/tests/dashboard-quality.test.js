import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { runInNewContext } from 'node:vm'

const source = readFileSync(new URL('../src/views/Dashboard.vue', import.meta.url), 'utf8')
const match = source.match(/const qualityChartState = computed\(\(\) => \{([\s\S]*?)\n\}\);/)
assert.ok(match)
function state(score, count, overrides = {}) {
  const values = { loading: false, qualityError: '', analysisCountError: '',
    qualityScore: score, analysisCount: count, ...overrides }
  const context = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, { value }]))
  return runInNewContext(`(() => {${match[1]}})()`, context)
}

test('actual mean scores including zero/full score and one record are displayable', () => {
  for (const score of [0, 60, 87.5, 100]) assert.equal(state(score, 1), 'ready')
})
test('no records or absent/invalid metrics never fabricate a ring', () => {
  assert.equal(state(0, 0), 'empty')
  for (const score of [null, -1, 101]) assert.equal(state(score, 1), 'unavailable')
  assert.equal(state(60, null), 'unavailable')
})
test('loading and either API failure are explicit states', () => {
  assert.equal(state(60, 1, { loading: true }), 'loading')
  assert.equal(state(60, 1, { qualityError: 'failed' }), 'error')
  assert.equal(state(60, 1, { analysisCountError: 'failed' }), 'error')
})
