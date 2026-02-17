import { defineStore } from 'pinia'

export type ToastVariant = 'success' | 'error' | 'warning' | 'info'

export interface ToastItem {
  id: number
  title: string
  description?: string
  variant: ToastVariant
}

interface ToastTimer {
  timerId: ReturnType<typeof setTimeout>
  remaining: number
  startedAt: number
}

const DEFAULT_DURATIONS: Record<ToastVariant, number> = {
  success: 3000,
  info: 4000,
  warning: 5000,
  error: 6000,
}

let toastSequence = 0

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: [] as ToastItem[],
    timers: {} as Record<number, ToastTimer>,
  }),
  actions: {
    push(payload: Omit<ToastItem, 'id'> & { duration?: number }) {
      const id = ++toastSequence
      const item: ToastItem = {
        id,
        title: payload.title,
        description: payload.description,
        variant: payload.variant,
      }
      this.items.push(item)

      const duration = payload.duration ?? DEFAULT_DURATIONS[payload.variant]
      this.startTimer(id, duration)

      return id
    },
    startTimer(id: number, duration: number) {
      const timerId = window.setTimeout(() => {
        this.remove(id)
      }, duration)
      this.timers[id] = { timerId, remaining: duration, startedAt: Date.now() }
    },
    pause(id: number) {
      const timer = this.timers[id]
      if (!timer) return
      clearTimeout(timer.timerId)
      timer.remaining -= Date.now() - timer.startedAt
    },
    resume(id: number) {
      const timer = this.timers[id]
      if (!timer || timer.remaining <= 0) return
      this.startTimer(id, timer.remaining)
    },
    remove(id: number) {
      const timer = this.timers[id]
      if (timer) {
        clearTimeout(timer.timerId)
        delete this.timers[id]
      }
      this.items = this.items.filter((item) => item.id !== id)
    },
  },
})
