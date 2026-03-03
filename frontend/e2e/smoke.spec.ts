import { test, expect } from "@playwright/test";

/**
 * Minimal smoke test: login page loads.
 * Optional in CI; run with: npm run test:e2e
 */
test("login page loads", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator('text=AKTU Academic Autonomy Portal').first()).toBeVisible();
  await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
  await expect(page.getByLabel(/password/i)).toBeVisible();
});
