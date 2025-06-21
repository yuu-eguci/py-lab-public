import { describe, it, expect } from "vitest"
import formatDate from "./formatDate"

// Vitest doc: https://vitest.dev/api/

describe("formatDate", () => {
  it("should format date as `Month day, year`", () => {
    const date = new Date("2023-03-15")
    const result = formatDate(date)
    expect(result).toBe("March 15, 2023")
  })
})
