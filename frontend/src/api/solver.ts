import type { SolveRequest, SolveResponse } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || ''

export async function solveProblem(request: SolveRequest): Promise<SolveResponse> {
  const response = await fetch(`${API_BASE}/solve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail?.error || data.error || 'Failed to solve problem')
  }

  return data
}
