import { render, screen, act } from "@testing-library/react";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";

// Mock WebSocket
let mockWsInstance: {
  onopen: (() => void) | null;
  onmessage: ((e: { data: string }) => void) | null;
  onclose: (() => void) | null;
  onerror: (() => void) | null;
  close: jest.Mock;
  readyState: number;
};

const MockWebSocket = jest.fn().mockImplementation(() => {
  mockWsInstance = {
    onopen: null,
    onmessage: null,
    onclose: null,
    onerror: null,
    close: jest.fn(),
    readyState: 1,
  };
  return mockWsInstance;
});

(global as any).WebSocket = MockWebSocket;

describe("ActivityFeed", () => {
  beforeEach(() => {
    MockWebSocket.mockClear();
  });

  it("renders empty state when no events", () => {
    render(<ActivityFeed />);
    expect(screen.getByText(/No activity yet/i)).toBeInTheDocument();
  });

  it("shows 'Live' status when connected", () => {
    render(<ActivityFeed />);
    act(() => { mockWsInstance.onopen?.(); });
    expect(screen.getByText("Live")).toBeInTheDocument();
  });

  it("renders events received via WebSocket", async () => {
    render(<ActivityFeed />);
    act(() => { mockWsInstance.onopen?.(); });

    const event = {
      id: 1,
      agent_type: "social_media",
      action: "post_tweet",
      summary: "Posted a tweet about our launch",
      level: "success",
      created_at: new Date().toISOString(),
    };

    act(() => {
      mockWsInstance.onmessage?.({ data: JSON.stringify(event) });
    });

    expect(screen.getByText("social_media")).toBeInTheDocument();
    expect(screen.getByText("Posted a tweet about our launch")).toBeInTheDocument();
  });

  it("shows reconnecting state when disconnected", () => {
    render(<ActivityFeed />);
    act(() => { mockWsInstance.onclose?.(); });
    expect(screen.getByText(/Reconnecting/i)).toBeInTheDocument();
  });
});
