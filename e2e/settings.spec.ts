import { test, expect } from "@playwright/test";

test.describe("Settings page", () => {
  test("loads company config", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.getByText("Company Profile")).toBeVisible();
    await expect(page.getByText("Scheduler")).toBeVisible();
  });

  test("save button is present", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.getByRole("button", { name: "Save Settings" })).toBeVisible();
  });
});
