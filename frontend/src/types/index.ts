export interface SolveRequest {
  problem_description: string
  additional_info: string
}

export interface SolveResponse {
  needs_more_info?: boolean
  questions?: string[]
  solution?: string
  asp_code?: string
  visualization_html?: string
  log?: string
  error?: string
  not_suitable?: boolean
  suggested_tool?: string
  reason?: string
}

export interface ProblemExample {
  id: string
  name: string
  category: string
  description: string
  problem_description: string
}

export interface HistoryEntry {
  id: string
  timestamp: Date
  problem: string
  solution?: string
  aspCode?: string
  status: 'pending' | 'solved' | 'error'
}

export type SolverState = 'idle' | 'loading' | 'awaiting_info' | 'solved' | 'error' | 'not_suitable'
