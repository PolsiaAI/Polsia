import { render, screen } from "@testing-library/react";
import { Sidebar } from "@/components/layout/Sidebar";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

// Mock next/link
jest.mock("next/link", () => {
  return function MockLink({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) {
    return <a href={href} className={className}>{children}</a>;
  };
});

describe("Sidebar", () => {
  it("renders all nav items", () => {
    render(<Sidebar />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Agents")).toBeInTheDocument();
    expect(screen.getByText("Finance")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("highlights the active route", () => {
    render(<Sidebar />);
    const dashboardLink = screen.getByText("Dashboard").closest("a");
    expect(dashboardLink).toHaveClass("bg-indigo-600");
  });

  it("shows the app title", () => {
    render(<Sidebar />);
    expect(screen.getByText("Polsia")).toBeInTheDocument();
  });
});
