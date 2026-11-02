// SSE (text/event-stream) を fetch のストリームで受け取るための小さなパーサです。
// DOC: https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation

export type SSEEvent = {
  event: string
  data: string
}

export type SSEParser = {
  // デコード済みの文字列を渡すと、完成したイベントを返します。
  push: (chunk: string) => SSEEvent[]
}

export function createSSEParser(): SSEParser {
  let buffer = ""
  let eventType = ""
  let dataLines: string[] = []

  const processLine = (line: string, events: SSEEvent[]) => {
    // 空行でイベントを確定します。
    if (line === "") {
      if (dataLines.length > 0) {
        events.push({ event: eventType || "message", data: dataLines.join("\n") })
      }
      eventType = ""
      dataLines = []
      return
    }
    // ":" で始まる行はコメントです。
    if (line.startsWith(":")) {
      return
    }
    const colon = line.indexOf(":")
    const field = colon === -1 ? line : line.slice(0, colon)
    let value = colon === -1 ? "" : line.slice(colon + 1)
    if (value.startsWith(" ")) {
      value = value.slice(1)
    }
    if (field === "data") {
      dataLines.push(value)
    } else if (field === "event") {
      eventType = value
    }
  }

  return {
    push(chunk) {
      buffer += chunk
      const events: SSEEvent[] = []
      const lineEnd = /\r\n|\r|\n/g
      let start = 0
      let match: RegExpExecArray | null
      while ((match = lineEnd.exec(buffer)) !== null) {
        // 末尾の \r は次のチャンクの \n と組で CRLF かもしれないので、次まで待ちます。
        if (match[0] === "\r" && match.index === buffer.length - 1) {
          break
        }
        processLine(buffer.slice(start, match.index), events)
        start = lineEnd.lastIndex
      }
      // 改行で終わっていない行は、次のチャンクとつなげるために残しておきます。
      buffer = buffer.slice(start)
      return events
    },
  }
}

export type LabLogEntry = {
  kind: "message" | "error"
  text: string
}

// /api/app/lab が返すイベントの data を、画面に出す 1 件に変換します。
export function parseLabEvent(data: string): LabLogEntry | null {
  let payload: unknown
  try {
    payload = JSON.parse(data)
  } catch {
    return null
  }
  if (typeof payload !== "object" || payload === null || !("data" in payload)) {
    return null
  }
  const body = payload.data as { message?: unknown; error?: unknown; sentAt?: unknown }
  if (typeof body.error === "string") {
    return { kind: "error", text: body.error }
  }
  if (typeof body.message === "string" && typeof body.sentAt === "string") {
    return { kind: "message", text: `[${body.sentAt}]\n${body.message}` }
  }
  return null
}
