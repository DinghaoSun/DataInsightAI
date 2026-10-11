// Evaluate the actual detail-page computed getters, not duplicated adapter logic.
// No browser, HTTP, database or additional packages required.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { runInNewContext } from 'node:vm'

const source = readFileSync(new URL('../src/views/DatasetDetail.vue', import.meta.url), 'utf8')
function getter(name, payload) {
  const match = source.match(new RegExp(`const ${name} = computed\\(\\(\\) => \\{([\\s\\S]*?)\\n\\}\\)`))
  assert.ok(match, `Detail page getter ${name} must exist`)
  return runInNewContext(`(() => {${match[1]}\n})()`, { analysis: { value: payload } })
}

test('repeated/distinct/null columns display counts, including zero', () => {
  const values = getter('uniqueValues', { analysis: { unique_values: { repeated: 2, distinct: 4, empty: 0 } } })
  assert.equal(values.repeated ?? '--', 2)
  assert.equal(values.distinct ?? '--', 4)
  assert.equal(values.empty ?? '--', 0)
  assert.ok(source.includes("uniqueValues[column] ?? '--'"))
})

test('missing result/map/column stays unknown, not a fabricated zero', () => {
  for (const payload of [null, {}, { analysis: {} }, { analysis: { unique_values: null } }]) {
    assert.equal(getter('uniqueValues', payload).missing ?? '--', '--')
  }
  assert.equal(getter('uniqueValues', { analysis: { unique_values: { a: 1 } } }).missing ?? '--', '--')
})

test('count map participates in field discovery and type fallback', () => {
  const payload = { analysis: { unique_values: { repeated: 2, distinct: 4, empty: 0 } } }
  assert.deepEqual(Array.from(getter('columns', payload)), ['repeated', 'distinct', 'empty'])
  const types = getter('dtypes', payload)
  assert.equal(types.repeated, 'text')
  assert.equal(types.empty, 'text')
})
