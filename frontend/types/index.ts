// =============================================================================
// types/index.ts
// =============================================================================
// Shared TypeScript types across the frontend.
// =============================================================================

export interface Creator {
  id: number
  tiktok_handle: string
  email: string
  is_active: boolean
  created_at: string
}

export interface CreatorDNA {
  primary_niche: string
  secondary_niches: string[]
  tone: string
  hook_style: string
  avg_video_length: string
  audience_type: string
  content_style: string
  posting_frequency: string | null
  raw_dna: Record<string, unknown>
  updated_at: string
}

export interface ContentIdea {
  id: number
  hook: string
  shot_list: string[]
  cta: string
  angle_type: string
  source_revenue: string
  feedback: 'made_it' | 'not_my_style' | null
  delivered_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  creator_id: number
  tiktok_handle: string
  message?: string
}

export type AngleType =
  | 'curiosity_gap'
  | 'problem_agitate_solve'
  | 'transformation'
  | 'social_proof'
  | 'urgency_deal'
  | 'demonstration'
