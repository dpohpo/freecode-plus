import { chmodSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs'
import { homedir } from 'os'
import { dirname, join } from 'path'
import { jsonParse } from '../slowOperations.js'

export const TEAMMATE_MODEL_PROFILE_ALIASES = [
  'glm',
  'deepseekvpro',
  'opus',
  'sonnet',
  'haiku',
] as const

export const PROFILE_ENV_KEYS_TO_CLEAR = [
  'ANTHROPIC_BASE_URL',
  'ANTHROPIC_MODEL',
  'ANTHROPIC_SMALL_FAST_MODEL',
  'ANTHROPIC_DEFAULT_HAIKU_MODEL',
  'ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION',
  'ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME',
  'ANTHROPIC_DEFAULT_HAIKU_MODEL_SUPPORTED_CAPABILITIES',
  'ANTHROPIC_DEFAULT_OPUS_MODEL',
  'ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION',
  'ANTHROPIC_DEFAULT_OPUS_MODEL_NAME',
  'ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES',
  'ANTHROPIC_DEFAULT_SONNET_MODEL',
  'ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION',
  'ANTHROPIC_DEFAULT_SONNET_MODEL_NAME',
  'ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES',
  'ANTHROPIC_CUSTOM_MODEL_OPTION',
  'ANTHROPIC_CUSTOM_MODEL_OPTION_NAME',
  'ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION',
  'ANTHROPIC_AUTH_TOKEN',
  'ANTHROPIC_API_KEY',
  'CLAUDE_CODE_SUBAGENT_MODEL',
  'CLAUDE_CODE_EFFORT_LEVEL',
  'CLAUDE_CODE_DISABLE_1M_CONTEXT',
  'API_TIMEOUT_MS',
] as const

type TeamModelProfile = {
  model: string
  baseUrl?: string
  authToken?: string
  apiKey?: string
  apiKeyHelper?: string
  smallFastModel?: string
  defaultOpusModel?: string
  defaultSonnetModel?: string
  defaultHaikuModel?: string
  availableModels?: string[]
  effortLevel?: string
  apiTimeoutMs?: string
  extraEnv?: Record<string, string>
}

type ProfileConfig = {
  profiles?: Record<string, TeamModelProfile>
}

export type ResolvedTeammateModelProfile = {
  alias: string
  model: string
  settingsPath?: string
  clearEnv: readonly string[]
}

function getProfileConfigPath(): string {
  return (
    process.env.FREECODE_AGENT_TEAM_MODEL_PROFILES ||
    join(homedir(), '.config', 'free-code', 'agent-team-model-profiles.json')
  )
}

function getGeneratedSettingsDir(): string {
  return (
    process.env.FREECODE_AGENT_TEAM_GENERATED_SETTINGS_DIR ||
    join(dirname(getProfileConfigPath()), 'agent-team-generated-settings')
  )
}

function readConfiguredProfiles(): Record<string, TeamModelProfile> {
  const path = getProfileConfigPath()
  if (!existsSync(path)) return {}

  const parsed = jsonParse(readFileSync(path, 'utf-8')) as ProfileConfig
  const profiles = parsed.profiles ?? (parsed as Record<string, TeamModelProfile>)
  return Object.fromEntries(
    Object.entries(profiles).map(([key, profile]) => [
      key.toLowerCase(),
      profile,
    ]),
  )
}

function getBuiltInProfile(alias: string): TeamModelProfile | undefined {
  switch (alias) {
    case 'opus':
    case 'sonnet':
    case 'haiku':
      return { model: alias }
    case 'glm':
      return {
        model: process.env.GLM_AGENT_TEAM_MODEL || 'glm-5.1',
        baseUrl:
          process.env.GLM_ANTHROPIC_BASE_URL ||
          (process.env.ZAI_API_KEY || process.env.GLM_ANTHROPIC_AUTH_TOKEN
            ? 'https://api.z.ai/api/anthropic'
            : 'https://open.bigmodel.cn/api/anthropic'),
        authToken:
          process.env.ZAI_API_KEY ||
          process.env.ZHIPU_API_KEY ||
          process.env.ANTHROPIC_AUTH_TOKEN,
        defaultOpusModel: process.env.GLM_AGENT_TEAM_MODEL || 'glm-5.1',
        defaultSonnetModel: process.env.GLM_AGENT_TEAM_MODEL || 'glm-5.1',
        defaultHaikuModel:
          process.env.GLM_AGENT_TEAM_SMALL_MODEL || 'glm-4.5-air',
        smallFastModel:
          process.env.GLM_AGENT_TEAM_SMALL_MODEL || 'glm-4.5-air',
        apiTimeoutMs: process.env.GLM_API_TIMEOUT_MS || '3000000',
      }
    case 'deepseekvpro':
      return {
        model: process.env.DEEPSEEK_AGENT_TEAM_MODEL || 'deepseek-v4-pro',
        baseUrl:
          process.env.DEEPSEEK_ANTHROPIC_BASE_URL ||
          'https://api.deepseek.com/anthropic',
        apiKey:
          process.env.DEEPSEEK_API_KEY ||
          process.env.DEEPSEEK_ANTHROPIC_AUTH_TOKEN ||
          process.env.ANTHROPIC_API_KEY,
        defaultOpusModel:
          process.env.DEEPSEEK_AGENT_TEAM_MODEL || 'deepseek-v4-pro',
        defaultSonnetModel:
          process.env.DEEPSEEK_AGENT_TEAM_MODEL || 'deepseek-v4-pro',
        defaultHaikuModel:
          process.env.DEEPSEEK_AGENT_TEAM_SMALL_MODEL || 'deepseek-v4-flash',
        smallFastModel:
          process.env.DEEPSEEK_AGENT_TEAM_SMALL_MODEL || 'deepseek-v4-flash',
        availableModels: [
          process.env.DEEPSEEK_AGENT_TEAM_MODEL || 'deepseek-v4-pro',
          process.env.DEEPSEEK_AGENT_TEAM_SMALL_MODEL || 'deepseek-v4-flash',
          'opus',
          'sonnet',
          'haiku',
        ],
        extraEnv: {
          ANTHROPIC_CUSTOM_MODEL_OPTION:
            process.env.DEEPSEEK_AGENT_TEAM_MODEL || 'deepseek-v4-pro',
          ANTHROPIC_CUSTOM_MODEL_OPTION_NAME: 'DeepSeek V4 Pro',
          ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION:
            'DeepSeek V4 Pro via DeepSeek Anthropic-compatible API',
        },
        effortLevel: process.env.DEEPSEEK_EFFORT_LEVEL || 'max',
        apiTimeoutMs: process.env.DEEPSEEK_API_TIMEOUT_MS || '3000000',
      }
    default:
      return undefined
  }
}

function resolveProfile(alias: string): TeamModelProfile | undefined {
  const configured = readConfiguredProfiles()[alias]
  return configured ?? getBuiltInProfile(alias)
}

function settingsEnvForProfile(
  profile: TeamModelProfile,
): Record<string, string> {
  return {
    ...(profile.baseUrl && { ANTHROPIC_BASE_URL: profile.baseUrl }),
    ...(profile.authToken && { ANTHROPIC_AUTH_TOKEN: profile.authToken }),
    ...(profile.apiKey && { ANTHROPIC_API_KEY: profile.apiKey }),
    ANTHROPIC_MODEL: profile.model,
    ...(profile.smallFastModel && {
      ANTHROPIC_SMALL_FAST_MODEL: profile.smallFastModel,
      CLAUDE_CODE_SUBAGENT_MODEL: profile.smallFastModel,
    }),
    ...(profile.defaultOpusModel && {
      ANTHROPIC_DEFAULT_OPUS_MODEL: profile.defaultOpusModel,
    }),
    ...(profile.defaultSonnetModel && {
      ANTHROPIC_DEFAULT_SONNET_MODEL: profile.defaultSonnetModel,
    }),
    ...(profile.defaultHaikuModel && {
      ANTHROPIC_DEFAULT_HAIKU_MODEL: profile.defaultHaikuModel,
    }),
    ...(profile.effortLevel && {
      CLAUDE_CODE_EFFORT_LEVEL: profile.effortLevel,
    }),
    ...(profile.apiTimeoutMs && { API_TIMEOUT_MS: profile.apiTimeoutMs }),
    ...(profile.extraEnv ?? {}),
  }
}

function profileNeedsSettings(profile: TeamModelProfile): boolean {
  return (
    !!profile.baseUrl ||
    !!profile.authToken ||
    !!profile.apiKey ||
    !!profile.apiKeyHelper ||
    !!profile.smallFastModel ||
    !!profile.defaultOpusModel ||
    !!profile.defaultSonnetModel ||
    !!profile.defaultHaikuModel ||
    !!profile.effortLevel ||
    !!profile.apiTimeoutMs ||
    !!profile.extraEnv
  )
}

function writeGeneratedSettings(
  alias: string,
  profile: TeamModelProfile,
): string | undefined {
  if (!profileNeedsSettings(profile)) return undefined

  if (
    (profile.baseUrl || profile.authToken || profile.apiKey) &&
    !profile.authToken &&
    !profile.apiKey &&
    !profile.apiKeyHelper
  ) {
    throw new Error(
      `Agent Team model profile "${alias}" needs authToken, apiKey, or apiKeyHelper.`,
    )
  }

  const dir = getGeneratedSettingsDir()
  mkdirSync(dir, { recursive: true, mode: 0o700 })
  const path = join(dir, `${alias}.settings.json`)
  const settings = {
    model: profile.model,
    availableModels: profile.availableModels ?? [
      profile.model,
      ...(profile.smallFastModel ? [profile.smallFastModel] : []),
      'opus',
      'sonnet',
      'haiku',
    ],
    ...(profile.apiKeyHelper && { apiKeyHelper: profile.apiKeyHelper }),
    env: settingsEnvForProfile(profile),
    teammateDefaultModel: null,
  }
  writeFileSync(path, JSON.stringify(settings, null, 2) + '\n', {
    mode: 0o600,
  })
  chmodSync(path, 0o600)
  return path
}

export function getTeammateModelProfileAliases(): readonly string[] {
  return TEAMMATE_MODEL_PROFILE_ALIASES
}

/**
 * Detect a model profile alias from an actual model name.
 * E.g. 'glm-5.1' → 'glm', 'deepseek-v4-pro[1m]' → 'deepseekvpro'.
 * Returns null for first-party Claude models (no profile needed).
 */
export function detectProfileAliasFromModelName(
  modelName: string,
): string | null {
  if (!modelName) return null
  const lower = modelName.toLowerCase()
  if (lower.startsWith('glm-')) return 'glm'
  if (lower.includes('deepseek')) return 'deepseekvpro'
  return null
}

export function resolveTeammateModelProfile(
  model: string | undefined,
): ResolvedTeammateModelProfile | null {
  if (!model) return null
  const alias = model.trim().toLowerCase()
  if (!(TEAMMATE_MODEL_PROFILE_ALIASES as readonly string[]).includes(alias)) {
    return null
  }

  const profile = resolveProfile(alias)
  if (!profile) return null

  return {
    alias,
    model: profile.model,
    settingsPath: writeGeneratedSettings(alias, profile),
    clearEnv: PROFILE_ENV_KEYS_TO_CLEAR,
  }
}
