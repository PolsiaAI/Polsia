import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test("loads and shows metrics cards", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText("Dashboard")).toBeVisible();
    await expect(page.getByText("Tasks Today")).toBeVisible();
    await expect(page.getByText("MRR")).toBeVisible();
  });

  test("shows agent status grid", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText("Agent Status")).toBeVisible();
  });

  test("sidebar navigation links are present", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText("Finance")).toBeVisible();
    await expect(page.getByText("Agents")).toBeVisible();
    await expect(page.getByText("Tasks")).toBeVisible();
  });
});
