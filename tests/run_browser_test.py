import asyncio
import os
import subprocess
import sys
sys.stdout.reconfigure(line_buffering=True)
import time
import urllib.request
from playwright.async_api import async_playwright

PORT = 8098
BASE_URL = f"http://127.0.0.1:{PORT}"

def wait_for_server(timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/health", timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

async def main():
    os.makedirs("docs/browser-screenshots", exist_ok=True)

    print(f"[1/7] Launching dedicated FastAPI process on port {PORT}...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.server:app", "--port", str(PORT), "--log-level", "warning"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        if not wait_for_server():
            raise RuntimeError("FastAPI server failed to start within timeout.")
        print("-> Server healthy and responding to HTTP requests.")

        async with async_playwright() as p:
            print("[2/7] Launching Chromium browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            await context.route("**/*.woff*", lambda r: r.abort())
            await context.route("**/*.woff2*", lambda r: r.abort())
            await context.route("**/*.ttf*", lambda r: r.abort())
            page = await context.new_page()

            page.on("console", lambda m: print(f"Browser Console [{m.type}]: {m.text}"))
            page.on("pageerror", lambda e: print(f"Browser Page Error: {e}"))
            page.on("dialog", lambda d: print(f"Browser Dialog [{d.type}]: {d.message}") or d.accept())

            # 1. Home Dashboard
            print(f"[3/7] Navigating to {BASE_URL}...")
            await page.goto(BASE_URL, wait_until="domcontentloaded")
            await page.wait_for_selector("main", timeout=10000)
            await page.screenshot(path="docs/browser-screenshots/01_dashboard_home.png")
            print("-> Captured docs/browser-screenshots/01_dashboard_home.png")
            title = await page.title()
            print(f"-> Page Title: {title}")
            assert "Growpido" in title

            # 2. Name Search & Candidate Gate
            print("[4/7] Testing Name Search & Candidate Confirmation Gate...")
            await page.fill("#candidate-name-input", "Narendra Modi")
            await page.fill("#candidate-context-input", "Prime Minister of India")
            await page.click("#btn-search-candidates")
            
            print("-> Awaiting public candidate profile search results...")
            await page.wait_for_selector("#candidate-cards-container .btn-confirm-candidate", timeout=30000)
            await page.screenshot(path="docs/browser-screenshots/02_candidate_gate_cards.png")
            print("-> Captured docs/browser-screenshots/02_candidate_gate_cards.png")

            cards_count = await page.locator("#candidate-cards-container > div").count()
            print(f"-> Candidate matches displayed: {cards_count}")
            assert cards_count > 0

            # 3. Confirm Candidate and Launch Deep Intelligence
            print("[5/7] Clicking 'Confirm & Launch Deep Intelligence' on target profile...")
            await page.locator(".btn-confirm-candidate").first.click()
            print("-> Awaiting OSINT Discovery, Claim Audit & Double-Check Verification (up to 300s)...")
            await page.wait_for_selector("#claims-container > div", timeout=300000)
            await page.screenshot(path="docs/browser-screenshots/03_human_gate_table.png")
            print("-> Captured docs/browser-screenshots/03_human_gate_table.png")

            claims_count = await page.locator("#claims-container > div").count()
            verified_count = await page.inner_text("#count-verified")
            partial_count = await page.inner_text("#count-partial")
            refused_count = await page.inner_text("#count-refused")
            print(f"-> Claims rendered in Human Gate: {claims_count} (V:{verified_count}, P:{partial_count}, R:{refused_count})")
            assert claims_count > 0

            # 4. Test Sovereign Human Adjudication Modal
            print("[6/7] Testing Sovereign Human Adjudication Modal...")
            adjudicate_btns = page.locator("#claims-container button:has-text('Adjudicate')")
            if await adjudicate_btns.count() > 0:
                await adjudicate_btns.first.click()
                await page.wait_for_selector("#override-modal:not(.hidden)", timeout=5000)
                await page.fill("#modal-override-notes", "Advisor confirmed against official PMIndia sovereign portal.")
                await page.screenshot(path="docs/browser-screenshots/04_override_modal.png")
                print("-> Captured docs/browser-screenshots/04_override_modal.png")
                await page.click("#modal-save-btn")
                await page.wait_for_selector("#override-modal", state="hidden", timeout=5000)
                print("-> Adjudication recorded.")

            # 5. Approve & Compile One-Page Diagnostic
            print("[7/7] Approving at Human Gate and compiling Diagnostic...")
            await page.click("#btn-approve-diagnostic")
            await page.wait_for_selector("#diagnostic-section:not(.hidden)", timeout=10000)
            
            # Scroll down to ensure Diagnostic section is in view
            await page.locator("#diagnostic-section").scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await page.screenshot(path="docs/browser-screenshots/05_executive_diagnostic.png")
            print("-> Captured docs/browser-screenshots/05_executive_diagnostic.png")

            dossier_rows = await page.locator("#dossier-table-body tr").count()
            gaps_count = await page.locator("#strategic-gaps-grid > div").count()
            sector_text = await page.inner_text("#diag-prospect-sector")
            loc_text = await page.inner_text("#diag-prospect-location")

            print(f"-> Fact Dossier Rows: {dossier_rows}")
            print(f"-> Strategic Gaps Cards: {gaps_count}")
            print(f"-> Sector Chip: {sector_text}")
            print(f"-> Jurisdiction Chip: {loc_text}")

            assert dossier_rows > 0
            assert gaps_count == 3
            assert "India" in loc_text or "Public" in sector_text

            await browser.close()
            print("\n=======================================================")
            print("[SUCCESS] ALL IN-BROWSER UI WORKFLOW TESTS PASSED SUCCESSFULLY!")
            print("=======================================================")

    finally:
        server_proc.terminate()
        server_proc.wait()

if __name__ == "__main__":
    asyncio.run(main())
