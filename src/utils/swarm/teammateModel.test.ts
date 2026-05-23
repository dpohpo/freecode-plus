import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import {
  getHardcodedTeammateModelFallback,
  shouldUseMainLoopModelFallbackForTeammates,
} from './teammateModel.js'

const touchedEnvKeys = [
  'ANTHROPIC_BASE_URL',
  'CLAUDE_CODE_USE_BEDROCK',
  'CLAUDE_CODE_USE_FOUNDRY',
  'CLAUDE_CODE_USE_OPENAI',
  'CLAUDE_CODE_USE_VERTEX',
  'USER_TYPE',
]

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

describe('teammate model fallback', () => {
  test('inherits main-loop default on Anthropic-compatible endpoints', () => {
    process.env.ANTHROPIC_BASE_URL = 'https://api.z.ai/api/anthropic'

    expect(shouldUseMainLoopModelFallbackForTeammates()).toBe(true)
    expect(getHardcodedTeammateModelFallback('glm-5.1')).toBe('glm-5.1')
  })

  test('keeps first-party fallback on Anthropic endpoints', () => {
    process.env.ANTHROPIC_BASE_URL = 'https://api.anthropic.com'

    expect(shouldUseMainLoopModelFallbackForTeammates()).toBe(false)
    expect(getHardcodedTeammateModelFallback('glm-5.1')).not.toBe('glm-5.1')
  })
})
