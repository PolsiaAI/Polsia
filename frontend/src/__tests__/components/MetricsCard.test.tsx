import { render, screen } from "@testing-library/react";
import { MetricsCard } from "@/components/dashboard/MetricsCard";

describe("MetricsCard", () => {
  it("renders title and value", () => {
    render(<MetricsCard title="MRR" value="$5,000" />);
    expect(screen.getByText("MRR")).toBeInTheDocument();
    expect(screen.getByText("$5,000")).toBeInTheDocument();
  });

  it("renders subtitle when provided", () => {
    render(<MetricsCard title="Tasks" value={10} subtitle="3 failed" />);
    expect(screen.getByText("3 failed")).toBeInTheDocument();
  });

  it("shows loading skeleton when loading=true", () => {
    const { container } = render(<MetricsCard title="MRR" value="$0" loading />);
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("applies green color for upward trend", () => {
    render(<MetricsCard title="MRR" value="$100" subtitle="+10%" trend="up" />);
    const subtitle = screen.getByText("+10%");
    expect(subtitle).toHaveClass("text-green-400");
  });

  it("applies red color for downward trend", () => {
    render(<MetricsCard title="Churn" value="5%" subtitle="Above target" trend="down" />);
    const subtitle = screen.getByText("Above target");
    expect(subtitle).toHaveClass("text-red-400");
  });
});
