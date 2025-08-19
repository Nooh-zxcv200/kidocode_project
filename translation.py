import asyncio
import json
import google.generativeai as genai
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

# ✅ Insert your Gemini API key here
genai.configure(api_key="you can type your api key right here")

async def main():
    # Deep crawling configuration
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2,
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )

    print("🌐 Crawling website...")

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(
            url="https://playground-a66636.webflow.io/id",
            config=config
        )

        print(f"✅ Crawled {len(results)} pages.\n")

        issues = []
        model = genai.GenerativeModel("gemini-1.5-flash")

        print("🤖 Analyzing translation with Gemini...\n")

        for r in results:
            prompt = f"""
            You are a native Indonesian language expert.
            The following text is translated into Indonesian but may sound unnatural.
            Identify any unnatural phrases or vocabulary and suggest improvements.

            Text:
            {r.markdown[:1500]}
            """

            try:
                response = model.generate_content(prompt)
                issues.append({
                    "url": r.url,
                    "issues_found": response.text
                })
                print(f"✅ Checked: {r.url}")
            except Exception as e:
                issues.append({
                    "url": r.url,
                    "issues_found": f"[!] Gemini API error: {str(e)}"
                })
                print(f"❌ Failed: {r.url}")

        # Save to JSON
        with open("gemini_translation_issues_full.json", "w", encoding="utf-8") as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)

        print("\n📁 Saved to gemini_translation_issues_full.json")

if __name__ == "__main__":
    asyncio.run(main())
