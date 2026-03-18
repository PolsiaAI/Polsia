import { render, screen } from "@testing-library/react";
import { AgentStatusGrid } from "@/components/dashboard/AgentStatusGrid";

// Mock the hook
jest.mock("@/hooks/useAgentStatus", () => ({
  useAgentStatus: jest.fn(),
}));

import { useAgentStatus } from "@/hooks/useAgentStatus";
const mockUseAgentStatus = useAgentStatus as jest.MockedFunction<typeof useAgentStatus>;

const mockStatuses = [
  { agent_type: "social_media", last_run_status: "completed", last_run_at: null, tasks_today: 3, tasks_total: 10 },
  { agent_type: "finance", last_run_status: "running", last_run_at: null, tasks_today: 1, tasks_total: 5 },
  { agent_type: "competitor_research", last_run_status: "failed", last_run_at: null, tasks_today: 0, tasks_total: 2 },
  { agent_type: "orchestrator", last_run_status: null, last_run_at: null, tasks_today: 0, tasks_total: 0 },
];

describe("AgentStatusGrid", () => {
  it("shows loading skeletons when loading=true", () => {
    mockUseAgentStatus.mockReturnValue({ statuses: [], loading: true, error: null });
    const { container } = render(<AgentStatusGrid />);
    expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });

  it("renders agent cards when loaded", () => {
    mockUseAgentStatus.mockReturnValue({ statuses: mockStatuses, loading: false, error: null });
    render(<AgentStatusGrid />);
    expect(screen.getByText("Social")).toBeInTheDocument();
    expect(screen.getByText("Finance")).toBeInTheDocument();
    expect(screen.getByText("Research")).toBeInTheDocument();
    expect(screen.getByText("Orchestrator")).toBeInTheDocument();
  });

  it("shows task count per agent", () => {
    mockUseAgentStatus.mockReturnValue({ statuses: mockStatuses, loading: false, error: null });
    render(<AgentStatusGrid />);
    expect(screen.getByText("3 tasks today")).toBeInTheDocument();
    expect(screen.getByText("1 tasks today")).toBeInTheDocument();
  });

  it("shows 'completed' status badge", () => {
    mockUseAgentStatus.mockReturnValue({ statuses: mockStatuses, loading: false, error: null });
    render(<AgentStatusGrid />);
    expect(screen.getByText("completed")).toBeInTheDocument();
  });

  it("shows 'idle' for agents with no last run status", () => {
    mockUseAgentStatus.mockReturnValue({ statuses: mockStatuses, loading: false, error: null });
    render(<AgentStatusGrid />);
    expect(screen.getByText("idle")).toBeInTheDocument();
  });

  it("applies green style for completed status", () => {
    mockUseAgentStatus.mockReturnValue({
      statuses: [{ agent_type: "finance", last_run_status: "completed", last_run_at: null, tasks_today: 0, tasks_total: 0 }],
      loading: false,
      error: null,
    });
    render(<AgentStatusGrid />);
    const badge = screen.getByText("completed");
    expect(badge.className).toContain("text-green-400");
  });

  it("applies red style for failed status", () => {
    mockUseAgentStatus.mockReturnValue({
      statuses: [{ agent_type: "ads_management", last_run_status: "failed", last_run_at: null, tasks_today: 0, tasks_total: 0 }],
      loading: false,
      error: null,
    });
    render(<AgentStatusGrid />);
    const badge = screen.getByText("failed");
    expect(badge.className).toContain("text-red-400");
  });
});
