import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'fs'
import { tmpdir } from 'os'
import { join } from 'path'
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { jsonParse } from '../slowOperations.js'
import {
  detectProfileAliasFromModelName,
  getTeammateModelProfileAliases,
  resolveTeammateModelProfile,
} from './modelProfiles.js'

const touchedEnvKeys = [
  'FREECODE_AGENT_TEAM_MODEL_PROFILES',
  'FREECODE_AGENT_TEAM_GENERATED_SETTINGS_DIR',
  'ZAI_API_KEY',
  'ZHIPU_API_KEY',
  'DEEPSEEK_API_KEY',
  'DEEPSEEK_API_KEY_HELPER',
  'DEEPSEEK_ANTHROPIC_AUTH_TOKEN',
  'DEEPSEEK_AGENT_TEAM_MODEL',
  'DEEPSEEK_AGENT_TEAM_SMALL_MODEL',
  'DEEPSEEK_EFFORT_LEVEL',
  'DEEPSEEK_API_TIMEOUT_MS',
  'ANTHROPIC_AUTH_TOKEN',
  'ANTHROPIC_API_KEY',
]

let originalEnv: Record<string, string | undefined>
let tempDir: string

beforeEach(() => {
  originalEnv = {}
  for (const key of touchedEnvKeys) {
    originalEnv[key] = process.env[key]
    delete process.env[key]
  }
  tempDir = mkdtempSync(join(tmpdir(), 'freecode-model-profiles-'))
  process.env.FREECODE_AGENT_TEAM_MODEL_PROFILES = join(
    tempDir,
    'profiles.json',
  )
  process.env.FREECODE_AGENT_TEAM_GENERATED_SETTINGS_DIR = join(
    tempDir,
    'generated',
  )
})

afterEach(() => {
  rmSync(tempDir, { recursive: true, force: true })
  for (const key of touchedEnvKeys) {
    const value = originalEnv[key]
    if (value === undefined) {
      delete process.env[key]
    } else {
      process.env[key] = value
    }
  }
})

describe('teammate model profiles', () => {
  test('resolves GLM profile into a generated settings file', () => {
    process.env.ZAI_API_KEY = 'test-zai-token'

    const profile = resolveTeammateModelProfile('glm')

    expect(profile?.alias).toBe('glm')
    expect(profile?.model).toBe('glm-5.1')
    expect(profile?.settingsPath).toBeTruthy()
    const settings = jsonParse(
      readFileSync(profile!.settingsPath!, 'utf-8'),
    ) as { env: Record<string, string> }
    expect(settings.env.ANTHROPIC_BASE_URL).toBe(
      'https://api.z.ai/api/anthropic',
    )
    expect(settings.env.ANTHROPIC_AUTH_TOKEN).toBe('test-zai-token')
    expect(settings.env.ANTHROPIC_MODEL).toBe('glm-5.1')
  })

  test('uses BigModel endpoint for GLM when only ZHIPU key is present', () => {
    process.env.ZHIPU_API_KEY = 'test-zhipu-token'

    const profile = resolveTeammateModelProfile('glm')

    const settings = jsonParse(
      readFileSync(profile!.settingsPath!, 'utf-8'),
    ) as { env: Record<string, string> }
    expect(settings.env.ANTHROPIC_BASE_URL).toBe(
      'https://open.bigmodel.cn/api/anthropic',
    )
    expect(settings.env.ANTHROPIC_AUTH_TOKEN).toBe('test-zhipu-token')
  })

  test('resolves official Claude aliases without generated settings', () => {
    const profile = resolveTeammateModelProfile('opus')

    expect(profile?.alias).toBe('opus')
    expect(profile?.model).toBe('opus')
    expect(profile?.settingsPath).toBeUndefined()
    expect(profile?.clearEnv).toContain('ANTHROPIC_BASE_URL')
  })

  test('resolves DeepSeek profile with API key settings and no Claude auth token', () => {
    process.env.DEEPSEEK_API_KEY = 'test-deepseek-key'

    const profile = resolveTeammateModelProfile('deepseekvpro')

    expect(profile?.alias).toBe('deepseekvpro')
    expect(profile?.model).toBe('deepseek-v4-pro')
    expect(profile?.settingsPath).toBeTruthy()
    const settings = jsonParse(
      readFileSync(profile!.settingsPath!, 'utf-8'),
    ) as {
      model: string
      env: Record<string, string>
    }
    expect(settings.model).toBe('deepseek-v4-pro')
    expect(settings).not.toHaveProperty('availableModels')
    expect(settings.env.ANTHROPIC_BASE_URL).toBe(
      'https://api.deepseek.com/anthropic',
    )
    expect(settings.env.ANTHROPIC_API_KEY).toBe('test-deepseek-key')
    expect(settings.env.ANTHROPIC_AUTH_TOKEN).toBeUndefined()
    expect(settings.env.ANTHROPIC_MODEL).toBe('deepseek-v4-pro')
    expect(settings.env.ANTHROPIC_DEFAULT_OPUS_MODEL).toBe('deepseek-v4-pro')
  })

  test('resolves DeepSeek profile with apiKeyHelper settings when no direct key is present', () => {
    process.env.DEEPSEEK_API_KEY_HELPER = 'printf helper-key'

    const profile = resolveTeammateModelProfile('deepseekvpro')

    expect(profile?.alias).toBe('deepseekvpro')
    const settings = jsonParse(
      readFileSync(profile!.settingsPath!, 'utf-8'),
    ) as {
      apiKeyHelper?: string
      env: Record<string, string>
    }
    expect(settings.apiKeyHelper).toBe('printf helper-key')
    expect(settings.env.ANTHROPIC_API_KEY).toBeUndefined()
    expect(settings.env.ANTHROPIC_AUTH_TOKEN).toBeUndefined()
    expect(settings.env.ANTHROPIC_BASE_URL).toBe(
      'https://api.deepseek.com/anthropic',
    )
  })

  test('resolves configured custom profiles for future providers', () => {
    writeFileSync(
      process.env.FREECODE_AGENT_TEAM_MODEL_PROFILES!,
      JSON.stringify(
        {
          profiles: {
            kimi: {
              model: 'kimi-k2',
              baseUrl: 'https://api.moonshot.cn/anthropic',
              apiKey: 'test-kimi-key',
              smallFastModel: 'kimi-k2-turbo',
              availableModels: ['kimi-k2', 'kimi-k2-turbo'],
            },
          },
        },
        null,
        2,
      ),
    )

    const profile = resolveTeammateModelProfile('kimi')

    expect(profile?.alias).toBe('kimi')
    expect(profile?.model).toBe('kimi-k2')
    expect(getTeammateModelProfileAliases()).toContain('kimi')
    expect(detectProfileAliasFromModelName('kimi-k2')).toBe('kimi')

    const settings = jsonParse(
      readFileSync(profile!.settingsPath!, 'utf-8'),
    ) as {
      model: string
      env: Record<string, string>
    }
    expect(settings.model).toBe('kimi-k2')
    expect(settings.env.ANTHROPIC_BASE_URL).toBe(
      'https://api.moonshot.cn/anthropic',
    )
    expect(settings.env.ANTHROPIC_API_KEY).toBe('test-kimi-key')
  })
})

describe('detectProfileAliasFromModelName', () => {
  test('detects GLM models', () => {
    expect(detectProfileAliasFromModelName('glm-5.1')).toBe('glm')
    expect(detectProfileAliasFromModelName('glm-4-flash')).toBe('glm')
    expect(detectProfileAliasFromModelName('GLM-5.0')).toBe('glm')
  })

  test('detects DeepSeek models', () => {
    expect(detectProfileAliasFromModelName('deepseek-v4-pro[1m]')).toBe(
      'deepseekvpro',
    )
    expect(detectProfileAliasFromModelName('deepseek-v4-flash')).toBe(
      'deepseekvpro',
    )
  })

  test('returns null for Claude models', () => {
    expect(detectProfileAliasFromModelName('claude-opus-4-6')).toBeNull()
    expect(detectProfileAliasFromModelName('claude-sonnet-4-6')).toBeNull()
    expect(detectProfileAliasFromModelName('opus')).toBeNull()
  })

  test('returns null for empty/unknown', () => {
    expect(detectProfileAliasFromModelName('')).toBeNull()
    expect(detectProfileAliasFromModelName('unknown-model')).toBeNull()
  })
})
