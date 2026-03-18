import { act, renderHook } from "@testing-library/react";
import { useActivityFeed } from "@/hooks/useActivityFeed";

let mockWsInstance: {
  onopen: (() => void) | null;
  onmessage: ((e: { data: string }) => void) | null;
  onclose: (() => void) | null;
  onerror: (() => void) | null;
  close: jest.Mock;
  readyState: number;
};

const MockWebSocket = jest.fn().mockImplementation(() => {
  mockWsInstance = { onopen: null, onmessage: null, onclose: null, onerror: null, close: jest.fn(), readyState: 0 };
  return mockWsInstance;
});

(global as any).WebSocket = MockWebSocket;

describe("useActivityFeed", () => {
  beforeEach(() => MockWebSocket.mockClear());

  it("initialises with empty events and disconnected state", () => {
    const { result } = renderHook(() => useActivityFeed());
    expect(result.current.events).toEqual([]);
    expect(result.current.connected).toBe(false);
  });

  it("sets connected=true on WebSocket open", () => {
    const { result } = renderHook(() => useActivityFeed());
    act(() => { mockWsInstance.onopen?.(); });
    expect(result.current.connected).toBe(true);
  });

  it("adds events when messages arrive", () => {
    const { result } = renderHook(() => useActivityFeed());
    act(() => { mockWsInstance.onopen?.(); });

    const event = { id: 1, agent_type: "finance", action: "snapshot", summary: "Revenue captured", level: "info", created_at: new Date().toISOString() };
    act(() => { mockWsInstance.onmessage?.({ data: JSON.stringify(event) }); });

    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0].summary).toBe("Revenue captured");
  });

  it("sets connected=false on WebSocket close", () => {
    const { result } = renderHook(() => useActivityFeed());
    act(() => { mockWsInstance.onopen?.(); });
    act(() => { mockWsInstance.onclose?.(); });
    expect(result.current.connected).toBe(false);
  });

  it("ignores malformed WebSocket messages", () => {
    const { result } = renderHook(() => useActivityFeed());
    act(() => { mockWsInstance.onopen?.(); });
    act(() => { mockWsInstance.onmessage?.({ data: "not json {{{" }); });
    expect(result.current.events).toHaveLength(0);
  });
});
