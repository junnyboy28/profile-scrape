from playwright.sync_api import sync_playwright
import re
import json

def debug_print(message, debug=True):
    if debug:
        print(f"DEBUG: {message}")

def clean_text(text):
    if not text:
        return "N/A"
    cleaned = ' '.join(text.split())
    cleaned = re.sub(r'\u2026\s*see more', '', cleaned)
    cleaned = re.sub(r'See more', '', cleaned)
    cleaned = re.sub(r'Show more', '', cleaned)
    return cleaned.strip()

# def extract_skills(page, debug=True):
#     skills = set()
#     try:
#         # Try to locate and click the "Show all" button for skills, if available
#         show_buttons = [
#             "button.artdeco-button:has-text('Show all')",
#             "button:has-text('Show all skills')",
#             ".pvs-list__footer-wrapper button"
#         ]
        
#         for button in show_buttons:
#             try:
#                 page.click(button, timeout=2000)
#                 page.wait_for_timeout(2000)
#                 debug_print("Clicked skills expansion button", debug)
#                 break
#             except Exception:
#                 continue

#         # Updated skill selector based on your provided path
#         skill_selector = "#profile-content > div > div.scaffold-layout.scaffold-layout--breakpoint-xl.scaffold-layout--main-aside.scaffold-layout--reflow.pv-profile.pvs-loader-wrapper__shimmer--animate > div > div > main > section:nth-child(8) > div.pGcZqWrQGSvWiFktAXMaZhsPYTbLtCflMw > ul > li span[aria-hidden='true']"
        
#         elements = page.query_selector_all(skill_selector)
#         for element in elements:
#             skill_text = clean_text(element.inner_text())
#             if skill_text and skill_text != "N/A":
#                 # Filter to ensure only valid skills are added
#                 if len(skill_text.split()) <= 4 and not any(char.isdigit() for char in skill_text):
#                     skills.add(skill_text)

#         return sorted(list(skills))  # Return sorted skills list

#     except Exception as e:
#         debug_print(f"Error extracting skills: {e}", debug)
#         return []



def extract_follower_count(page):
    try:
        follower_selectors = [
            "span:has-text('followers')",
            ".pv-top-card--list span:has-text('followers')",
            "[data-test-id='follower-count']",
            ".pv-top-card--list span.t-bold",
            ".pvs-header__subtitle span.pvs-header__subtitle-text"
        ]
        for selector in follower_selectors:
            elem = page.query_selector(selector)
            if elem:
                text = elem.inner_text()
                match = re.search(r'(\d+(?:,\d+)?)\s*followers?', text.lower())
                if match:
                    return int(match.group(1).replace(',', ''))
    except Exception:
        pass
    return 0

def extract_location(page):
    location_selectors = [
        ".pv-top-card--list-bullet li",
        "span.text-body-small",
        ".pv-text-details__left-panel.mt2 span.text-body-small",
        "[data-test-id='location']"
    ]
    for selector in location_selectors:
        try:
            elements = page.query_selector_all(selector)
            for element in elements:
                text = clean_text(element.inner_text())
                if text and "," in text:
                    if not any(x in text.lower() for x in ['he/him', 'she/her', 'they/them', 'followers', 'connections']):
                        return text
        except Exception:
            continue
    return "N/A"

def scrape_linkedin_profile(profile_url, cookies, debug=True):
    profile_data = {
        "person": {
            "backgroundUrl": "N/A",
            "firstName": "N/A",
            "followerCount": 0,
            "headline": "N/A",
            "lastName": "N/A",
            "location": "N/A",
            "photoUrl": "N/A",
            # "skills": [],
            "summary": "N/A",
            "linkedInUrl": profile_url
        }
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        context.add_cookies(cookies)
        page = context.new_page()

        try:
            debug_print(f"Navigating to {profile_url}", debug)
            page.goto(profile_url, wait_until='domcontentloaded')
            page.wait_for_selector("h1", timeout=15000)
            page.wait_for_timeout(5000)

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)

            name_elem = page.query_selector("h1")
            if name_elem:
                full_name = clean_text(name_elem.inner_text())
                name_parts = full_name.split()
                if name_parts:
                    profile_data["person"]["firstName"] = name_parts[0]
                    profile_data["person"]["lastName"] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else "N/A"

            headline_selectors = [
                "div.text-body-medium",
                ".pv-text-details__left-panel div",
                "[data-field='headline']",
                ".ph5 .text-body-medium"
            ]
            for selector in headline_selectors:
                elem = page.query_selector(selector)
                if elem:
                    headline_text = clean_text(elem.inner_text())
                    if headline_text != "N/A":
                        profile_data["person"]["headline"] = headline_text
                        break

            profile_data["person"]["location"] = extract_location(page)

            profile_data["person"]["followerCount"] = extract_follower_count(page)

            photo_selectors = [
                "img.pv-top-card-profile-picture__image",
                ".pv-top-card__photo img",
                "img[alt*='profile']",
                ".pv-top-card__non-self-photo-wrapper img"
            ]
            for selector in photo_selectors:
                element = page.query_selector(selector)
                if element:
                    photo_url = element.get_attribute("src")
                    if photo_url:
                        profile_data["person"]["photoUrl"] = photo_url
                        break

            bg_selectors = [
                "div.profile-background-image img",
                ".pv-top-card__background-image img",
                "img[data-test-id='profile-background-image']",
                ".profile-background-image__image"
            ]
            for selector in bg_selectors:
                element = page.query_selector(selector)
                if element:
                    bg_url = element.get_attribute("src")
                    if bg_url:
                        profile_data["person"]["backgroundUrl"] = bg_url
                        break

            about_selectors = [
                "#about ~ div .full-width div:not(:has(button))",
                "[data-generated-suggestion-target='about'] div",
                "#about ~ div .white-space-pre-wrap",
                ".pv-shared-text-with-see-more > span > span:first-child"
            ]
            for selector in about_selectors:
                elements = page.query_selector_all(selector)
                for element in elements:
                    summary_text = clean_text(element.inner_text())
                    if summary_text != "N/A" and len(summary_text) > 15:
                        profile_data["person"]["summary"] = summary_text
                        break

            # profile_data["person"]["skills"] = extract_skills(page, debug)

        except Exception as e:
            debug_print(f"Error during scraping: {str(e)}", debug)
        finally:
            browser.close()

    return profile_data

if __name__ == "__main__":
    profile_url = "https://www.linkedin.com/in/example-profile/"
    cookies = [
        {
            "name": "li_at",
            "value": "YOUR_COOKIE_VALUE",
            "domain": ".linkedin.com",
            "path": "/"
        }
    ]
    result = scrape_linkedin_profile(profile_url, cookies, debug=True)
    print(json.dumps(result, indent=2))
