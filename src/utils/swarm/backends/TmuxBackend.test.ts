import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { getTmuxTeamLayoutMode } from './TmuxBackend.js'

const touchedEnvKeys = ['FREEGLM_TEAM_LAYOUT', 'FREECODE_AGENT_TEAM_LAYOUT']

let originalEnv: Record<string, string | undefined>

beforeEach(() => {
  originalEnv = {}
  for (const key of touchedEnvKeys) {
    originalEnv[key] = process.env[key]
    delete process.env[key]
  }
})

afterEach(() => {
  for (const key of touchedEnvKeys) {
    const value = originalEnv[key]
    if (value === undefined) {
      delete process.env[key]
    } else {
      process.env[key] = value
    }
  }
})

describe('getTmuxTeamLayoutMode', () => {
  test('defaults Agent Team tmux layout to grid', () => {
    expect(getTmuxTeamLayoutMode()).toBe('grid')
  })

  test('allows opting back into legacy main-vertical layout', () => {
    process.env.FREEGLM_TEAM_LAYOUT = 'main-vertical'

    expect(getTmuxTeamLayoutMode()).toBe('main-vertical')
  })
})
