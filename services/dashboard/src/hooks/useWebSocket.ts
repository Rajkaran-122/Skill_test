import { useCallback, useEffect, useRef, useState } from 'react'

interface WebSocketOptions {
  url: string
  onMessage?: (data: unknown) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

interface WebSocketState {
  isConnected: boolean
  lastMessage: unknown | null
  error: string | null
}

export function useWebSocket({ url, onMessage, reconnectInterval = 3000, maxReconnectAttempts = 10 }: WebSocketOptions) {
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    lastMessage: null,
    error: null,
  })
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>()

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        setState((s) => ({ ...s, isConnected: true, error: null }))
        reconnectAttemptsRef.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setState((s) => ({ ...s, lastMessage: data }))
          onMessage?.(data)
        } catch {
          // Non-JSON message (e.g., "pong")
        }
      }

      ws.onclose = () => {
        setState((s) => ({ ...s, isConnected: false }))
        // Reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(1.5, reconnectAttemptsRef.current)
          reconnectTimerRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, delay)
        }
      }

      ws.onerror = () => {
        setState((s) => ({ ...s, error: 'Connection error' }))
      }

      wsRef.current = ws
    } catch (err) {
      setState((s) => ({ ...s, error: 'Failed to connect' }))
    }
  }, [url, onMessage, reconnectInterval, maxReconnectAttempts])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((data: string) => {
    wsRef.current?.send(data)
  }, [])

  return { ...state, sendMessage }
}
