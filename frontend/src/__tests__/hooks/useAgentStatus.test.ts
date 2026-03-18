import { act, renderHook } from "@testing-library/react";
import { useAgentStatus } from "@/hooks/useAgentStatus";

const mockStatuses = [
  { agent_type: "finance", last_run_status: "completed", last_run_at: null, tasks_today: 1, tasks_total: 5 },
];

let fetchMock: jest.Mock;

beforeEach(() => {
  jest.useFakeTimers();
  fetchMock = jest.fn().mockResolvedValue(mockStatuses);
  jest.mock("@/lib/api", () => ({ api: { get: fetchMock } }), { virtual: true });
});

afterEach(() => {
  jest.useRealTimers();
  jest.resetModules();
});

// Re-mock api for each test
jest.mock("@/lib/api", () => ({
  api: {
    get: jest.fn(),
  },
}));

import { api } from "@/lib/api";
const mockApiGet = api.get as jest.MockedFunction<typeof api.get>;

describe("useAgentStatus", () => {
  it("starts in loading state", () => {
    mockApiGet.mockResolvedValue([]);
    const { result } = renderHook(() => useAgentStatus());
    expect(result.current.loading).toBe(true);
    expect(result.current.statuses).toEqual([]);
  });

  it("fetches statuses on mount", async () => {
    mockApiGet.mockResolvedValue(mockStatuses);
    const { result } = renderHook(() => useAgentStatus());

    await act(async () => {});

    expect(result.current.loading).toBe(false);
    expect(result.current.statuses).toEqual(mockStatuses);
    expect(result.current.error).toBeNull();
  });

  it("polls at the given interval", async () => {
    mockApiGet.mockResolvedValue(mockStatuses);
    renderHook(() => useAgentStatus(5000));

    await act(async () => {});
    expect(mockApiGet).toHaveBeenCalledTimes(1);

    await act(async () => { jest.advanceTimersByTime(5000); });
    expect(mockApiGet).toHaveBeenCalledTimes(2);

    await act(async () => { jest.advanceTimersByTime(5000); });
    expect(mockApiGet).toHaveBeenCalledTimes(3);
  });

  it("sets error on fetch failure", async () => {
    mockApiGet.mockRejectedValue(new Error("Network error"));
    const { result } = renderHook(() => useAgentStatus());

    await act(async () => {});

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toContain("Network error");
  });

  it("stops polling on unmount", async () => {
    mockApiGet.mockResolvedValue(mockStatuses);
    const { unmount } = renderHook(() => useAgentStatus(1000));

    await act(async () => {});
    expect(mockApiGet).toHaveBeenCalledTimes(1);

    unmount();
    await act(async () => { jest.advanceTimersByTime(5000); });
    // No additional calls after unmount
    expect(mockApiGet).toHaveBeenCalledTimes(1);
  });
});
