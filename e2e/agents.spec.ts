import { test, expect } from "@playwright/test";

test.describe("Agents page", () => {
  test("lists all agents with Run Now button", async ({ page }) => {
    await page.goto("/agents");
    await expect(page.getByText("Agents")).toBeVisible();
    await expect(page.getByRole("button", { name: "Run Now" }).first()).toBeVisible();
  });

  test("trigger button shows queued confirmation", async ({ page }) => {
    await page.goto("/agents");
    const firstButton = page.getByRole("button", { name: "Run Now" }).first();
    await firstButton.click();
    // Expect either "Triggering…" or a success message
    await expect(page.locator("text=/queued|Triggering/")).toBeVisible({ timeout: 5000 });
  });
});
