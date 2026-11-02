import { describe, expect, it } from "vitest"
import { createSSEParser, parseLabEvent } from "./sse"

describe("createSSEParser", () => {
  it("1 チャンクに複数イベントがあっても全部取り出せます", () => {
    const parser = createSSEParser()
    expect(parser.push("data: a\n\ndata: b\n\n")).toEqual([
      { event: "message", data: "a" },
      { event: "message", data: "b" },
    ])
  })

  it("行がチャンクをまたいでも 1 イベントになります", () => {
    const parser = createSSEParser()
    expect(parser.push('data: {"a":')).toEqual([])
    expect(parser.push(' 1}\n')).toEqual([])
    expect(parser.push("\n")).toEqual([{ event: "message", data: '{"a": 1}' }])
  })

  it("CRLF と CR の改行も扱えます (CRLF がチャンクで割れても OK です)", () => {
    const parser = createSSEParser()
    expect(parser.push("data: a\r")).toEqual([])
    expect(parser.push("\n\r\ndata: b\r\r\n")).toEqual([
      { event: "message", data: "a" },
      { event: "message", data: "b" },
    ])
  })

  it("末尾の \\r は次のチャンクが来てから改行として扱います", () => {
    const parser = createSSEParser()
    expect(parser.push("data: c\r\r")).toEqual([])
    expect(parser.push("data: d")).toEqual([{ event: "message", data: "c" }])
  })

  it("複数の data 行は改行でつなぎ、コメント行は無視します", () => {
    const parser = createSSEParser()
    expect(parser.push(": keep-alive\nevent: custom\ndata: x\ndata:y\n\n")).toEqual([
      { event: "custom", data: "x\ny" },
    ])
  })

  it("空行が来るまではイベントにしません", () => {
    const parser = createSSEParser()
    expect(parser.push("data: unfinished\n")).toEqual([])
  })
})

describe("parseLabEvent", () => {
  it("message イベントは時刻つきの行にします", () => {
    const data = JSON.stringify({
      requestId: "rq-1",
      data: { message: "hello", sentAt: "2026-01-01T00:00:00+0000" },
    })
    expect(parseLabEvent(data)).toEqual({ kind: "message", text: "[2026-01-01T00:00:00+0000]\nhello" })
  })

  it("error イベントはエラーとして返します", () => {
    const data = JSON.stringify({ requestId: "rq-1", data: { error: "boom", sentAt: "t" } })
    expect(parseLabEvent(data)).toEqual({ kind: "error", text: "boom" })
  })

  it("JSON でないものや形が違うものは null です", () => {
    expect(parseLabEvent("not json")).toBeNull()
    expect(parseLabEvent(JSON.stringify({ foo: 1 }))).toBeNull()
    expect(parseLabEvent("null")).toBeNull()
  })
})
