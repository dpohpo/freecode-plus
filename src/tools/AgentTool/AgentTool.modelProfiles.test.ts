import { describe, expect, test } from 'bun:test'
import { inputSchema } from './AgentTool.js'

describe('AgentTool model profile schema', () => {
  test('accepts Agent Team model profile aliases', () => {
    const parsed = inputSchema().safeParse({
      description: 'Open teammate',
      prompt: 'Read package.json',
      name: 'glm-worker',
      team_name: 'demo',
      model: 'glm',
    })

    expect(parsed.success).toBe(true)
  })
})
