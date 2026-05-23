import { CLAUDE_OPUS_4_6_CONFIG } from '../model/configs.js'
import { getDefaultMainLoopModel } from '../model/model.js'
import {
  getAPIProvider,
  isFirstPartyAnthropicBaseUrl,
} from '../model/providers.js'

// @[MODEL LAUNCH]: Update the fallback model below.
// When the user has never set teammateDefaultModel in /config, new teammates
// use Opus 4.6. Must be provider-aware so Bedrock/Vertex/Foundry customers get
// the correct model ID.
export function shouldUseMainLoopModelFallbackForTeammates(): boolean {
  return getAPIProvider() === 'firstParty' && !isFirstPartyAnthropicBaseUrl()
}

export function getHardcodedTeammateModelFallback(
  mainLoopFallback?: string,
): string {
  if (shouldUseMainLoopModelFallbackForTeammates()) {
    return mainLoopFallback ?? getDefaultMainLoopModel()
  }

  return CLAUDE_OPUS_4_6_CONFIG[getAPIProvider()]
}
