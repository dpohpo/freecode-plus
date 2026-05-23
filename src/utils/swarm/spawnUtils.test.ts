import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { buildInheritedCliFlags, buildInheritedEnvVars } from './spawnUtils.js'

const touchedEnvKeys = [
  'ANTHROPIC_API_KEY',
  'ANTHROPIC_AUTH_TOKEN',
  'ANTHROPIC_BASE_URL',
  'ANTHROPIC_DEFAULT_HAIKU_MODEL',
  'ANTHROPIC_DEFAULT_OPUS_MODEL',
  'ANTHROPIC_DEFAULT_SONNET_MODEL',
  'ANTHROPIC_CUSTOM_MODEL_OPTION',
  'ANTHROPIC_CUSTOM_MODEL_OPTION_NAME',
  'ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION',
  'ANTHROPIC_MODEL',
  'ANTHROPIC_SMALL_FAST_MODEL',
  'API_TIMEOUT_MS',
  'BUN_BIN',
  'CLAUDE_CODE_EFFORT_LEVEL',
  'CLAUDE_CODE_SUBAGENT_MODEL',
  'CLAUDE_CODE_USE_OPENAI',
  'FREEGLM_TEAM_LAYOUT',
  'FREECODE_AGENT_TEAM_LAYOUT',
  'FREECODE_AGENT_TEAM_MODEL_PROFILES',
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

describe('buildInheritedEnvVars', () => {
  test('forwards compatible-provider model routing without forwarding secrets', () => {
    process.env.ANTHROPIC_BASE_URL = 'https://api.deepseek.com/anthropic'
    process.env.ANTHROPIC_MODEL = 'deepseek-v4-pro'
    process.env.ANTHROPIC_DEFAULT_OPUS_MODEL = 'deepseek-v4-pro'
    process.env.ANTHROPIC_DEFAULT_SONNET_MODEL = 'deepseek-v4-pro'
    process.env.ANTHROPIC_CUSTOM_MODEL_OPTION = 'deepseek-v4-pro'
    process.env.ANTHROPIC_CUSTOM_MODEL_OPTION_NAME = 'DeepSeek V4 Pro'
    process.env.ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION =
      'DeepSeek V4 Pro via DeepSeek Anthropic-compatible API'
    process.env.ANTHROPIC_DEFAULT_HAIKU_MODEL = 'deepseek-v4-flash'
    process.env.ANTHROPIC_SMALL_FAST_MODEL = 'deepseek-v4-flash'
    process.env.CLAUDE_CODE_SUBAGENT_MODEL = 'deepseek-v4-flash'
    process.env.CLAUDE_CODE_EFFORT_LEVEL = 'max'
    process.env.API_TIMEOUT_MS = '3000000'
    process.env.BUN_BIN = '/tmp/freecode-bun'
    process.env.CLAUDE_CODE_USE_OPENAI = '1'
    process.env.FREEGLM_TEAM_LAYOUT = 'grid'
    process.env.FREECODE_AGENT_TEAM_MODEL_PROFILES = '/tmp/profiles.json'
    process.env.ANTHROPIC_AUTH_TOKEN = 'secret-token'
    process.env.ANTHROPIC_API_KEY = 'secret-key'

    const env = buildInheritedEnvVars()

    expect(env).toContain('CLAUDECODE=1')
    expect(env).toContain('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1')
    expect(env).toContain(
      'ANTHROPIC_BASE_URL=https\\://api.deepseek.com/anthropic',
    )
    expect(env).toContain('ANTHROPIC_MODEL=deepseek-v4-pro')
    expect(env).toContain('ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro')
    expect(env).toContain('ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro')
    expect(env).toContain('ANTHROPIC_CUSTOM_MODEL_OPTION=deepseek-v4-pro')
    expect(env).toContain(
      'ANTHROPIC_CUSTOM_MODEL_OPTION_NAME=DeepSeek\\ V4\\ Pro',
    )
    expect(env).toContain(
      'ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION=DeepSeek\\ V4\\ Pro\\ via\\ DeepSeek\\ Anthropic-compatible\\ API',
    )
    expect(env).toContain('ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-flash')
    expect(env).toContain('ANTHROPIC_SMALL_FAST_MODEL=deepseek-v4-flash')
    expect(env).toContain('CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-flash')
    expect(env).toContain('CLAUDE_CODE_EFFORT_LEVEL=max')
    expect(env).toContain('API_TIMEOUT_MS=3000000')
    expect(env).toContain('BUN_BIN=/tmp/freecode-bun')
    expect(env).toContain('CLAUDE_CODE_USE_OPENAI=1')
    expect(env).toContain('FREEGLM_TEAM_LAYOUT=grid')
    expect(env).toContain(
      'FREECODE_AGENT_TEAM_MODEL_PROFILES=/tmp/profiles.json',
    )
    expect(env).not.toContain('ANTHROPIC_AUTH_TOKEN')
    expect(env).not.toContain('ANTHROPIC_API_KEY')
    expect(env).not.toContain('secret-token')
    expect(env).not.toContain('secret-key')
  })

  test('can omit and unset provider env for model profile spawns', () => {
    process.env.ANTHROPIC_BASE_URL = 'https://api.z.ai/api/anthropic'
    process.env.ANTHROPIC_MODEL = 'glm-5.1'

    const env = buildInheritedEnvVars({
      omit: ['ANTHROPIC_BASE_URL', 'ANTHROPIC_MODEL'],
      unset: ['ANTHROPIC_BASE_URL', 'ANTHROPIC_MODEL'],
    })

    expect(env).toContain('-u ANTHROPIC_BASE_URL')
    expect(env).toContain('-u ANTHROPIC_MODEL')
    expect(env).not.toContain(
      'ANTHROPIC_BASE_URL=https\\://api.z.ai/api/anthropic',
    )
    expect(env).not.toContain('ANTHROPIC_MODEL=glm-5.1')
  })
})

describe('buildInheritedCliFlags', () => {
  test('forwards bypass permission mode to spawned teammates', () => {
    const flags = buildInheritedCliFlags({
      permissionMode: 'bypassPermissions',
    })

    expect(flags).toContain('--dangerously-skip-permissions')
    expect(flags).toContain('--permission-mode bypassPermissions')
  })
})
