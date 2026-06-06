// =============================================================================
// lib/utils.ts
// =============================================================================

import { clsx, type ClassValue } from 'clsx'
import { AngleType } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export const angleConfig: Record<AngleType, {
  label: string
  color: string
  bg: string
  border: string
}> = {
  curiosity_gap: {
    label: 'curiosity gap',
    color: 'text-purple-700 dark:text-purple-300',
    bg: 'bg-purple-50 dark:bg-purple-950',
    border: 'border-purple-300 dark:border-purple-700',
  },
  problem_agitate_solve: {
    label: 'problem → solve',
    color: 'text-orange-700 dark:text-orange-300',
    bg: 'bg-orange-50 dark:bg-orange-950',
    border: 'border-orange-300 dark:border-orange-700',
  },
  transformation: {
    label: 'transformation',
    color: 'text-teal-700 dark:text-teal-300',
    bg: 'bg-teal-50 dark:bg-teal-950',
    border: 'border-teal-300 dark:border-teal-700',
  },
  social_proof: {
    label: 'social proof',
    color: 'text-blue-700 dark:text-blue-300',
    bg: 'bg-blue-50 dark:bg-blue-950',
    border: 'border-blue-300 dark:border-blue-700',
  },
  urgency_deal: {
    label: 'urgency deal',
    color: 'text-red-700 dark:text-red-300',
    bg: 'bg-red-50 dark:bg-red-950',
    border: 'border-red-300 dark:border-red-700',
  },
  demonstration: {
    label: 'demonstration',
    color: 'text-green-700 dark:text-green-300',
    bg: 'bg-green-50 dark:bg-green-950',
    border: 'border-green-300 dark:border-green-700',
  },
}

export const accentColor: Record<AngleType, string> = {
  curiosity_gap: 'bg-purple-500',
  problem_agitate_solve: 'bg-orange-500',
  transformation: 'bg-teal-500',
  social_proof: 'bg-blue-500',
  urgency_deal: 'bg-red-500',
  demonstration: 'bg-green-500',
}

export function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric'
  })
}

export function getInitials(handle: string) {
  return handle.slice(0, 2).toUpperCase()
}
