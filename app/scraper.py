# Import required libraries
from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import json

def scrape_linkedin_profile(profile_url, cookies, debug=True):
    def debug_print(message):
        if debug:
            print(f"DEBUG: {message}")

    def extract_identifier(url):
        return url.split("/in/")[-1].strip("/   ")

    def clean_text(text):
        if not text:
            return "N/A"
        # Remove extra whitespace and newlines
        cleaned = ' '.join(text.split())
        # Remove "... see more" and similar phrases
        cleaned = re.sub(r'…\s*see more', '', cleaned)
        cleaned = re.sub(r'See more', '', cleaned)
        cleaned = re.sub(r'Show more', '', cleaned)
        return cleaned.strip()

    def extract_follower_count(page):
        try:
            follower_selectors = [
                "span:has-text('followers')",
                ".pv-top-card--list span:has-text('followers')",
                "[data-test-id='follower-count']",
                ".pv-top-card--list span.t-bold"
            ]
            
            for selector in follower_selectors:
                elem = page.query_selector(selector)
                if elem:
                    text = elem.inner_text()
                    match = re.search(r'(\d+(?:,\d+)?)\s*followers?', text.lower())
                    if match:
                        return int(match.group(1).replace(',', ''))
        except Exception as e:
            debug_print(f"Error extracting follower count: {str(e)}")
        return 0

    profile_data = {
        "person": {
            "publicIdentifier": "",
            "linkedInUrl": "",
            "firstName": "N/A",
            "lastName": "N/A",
            "headline": "N/A",
            "location": "N/A",
            "summary": "N/A",
            "photoUrl": "N/A",
            "backgroundUrl": "N/A",
            "openToWork": False,
            "premium": False,
            "pronoun": "N/A",
            "followerCount": 0,
            "positions": [],
            "schools": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        
        try:
            # Navigate and wait for content
            page.goto(profile_url, wait_until='networkidle')
            page.wait_for_selector("h1", timeout=10000)
            page.wait_for_timeout(2000)  # Additional wait for dynamic content

            # Basic profile data
            profile_data["person"]["linkedInUrl"] = profile_url
            profile_data["person"]["publicIdentifier"] = extract_identifier(profile_url)

            # Name extraction
            name_elem = page.query_selector("h1")
            if name_elem:
                full_name = clean_text(name_elem.inner_text())
                name_parts = full_name.split()
                if name_parts:
                    profile_data["person"]["firstName"] = name_parts[0]
                    profile_data["person"]["lastName"] = name_parts[-1] if len(name_parts) > 1 else "N/A"

            # Headline extraction
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

            # Location extraction
            location_selectors = [
                "span.text-body-small:has-text('Area')",
                "span.text-body-small:has-text('Greater')",
                "[data-field='location']",
                ".pv-text-details__left-panel.mt2 span.text-body-small",
                ".ph5 .text-body-small"
            ]
            
            for selector in location_selectors:
                element = page.query_selector(selector)
                if element:
                    location_text = clean_text(element.inner_text())
                    if "area" in location_text.lower() or "greater" in location_text.lower():
                        profile_data["person"]["location"] = location_text
                        break

            # Enhanced summary/about extraction
            about_selectors = [
                "#about ~ .pvs-list__outer-container .visually-hidden",
                "section#about div.inline-show-more-text span",
                "section#about div.pv-shared-text-with-see-more span",
                "#about .pv-shared-text-with-see-more span",
                "[data-field='about_section'] span",
                "section.summary div.inline-show-more-text",
                "#about .display-flex span",
                ".pv-shared-text-with-see-more"
            ]
            
            for selector in about_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        summary_text = clean_text(element.inner_text())
                        if summary_text != "N/A" and len(summary_text) > 10:
                            profile_data["person"]["summary"] = summary_text
                            debug_print(f"Found summary: {summary_text[:50]}...")
                            break
                    if profile_data["person"]["summary"] != "N/A":
                        break
                except Exception as e:
                    debug_print(f"Error with summary selector {selector}: {str(e)}")

            # Profile photo
            photo_selectors = [
                "img.pv-top-card-profile-picture__image",
                ".pv-top-card__photo img",
                "img[alt*='profile']"
            ]
            for selector in photo_selectors:
                element = page.query_selector(selector)
                if element:
                    photo_url = element.get_attribute("src")
                    if photo_url:
                        profile_data["person"]["photoUrl"] = photo_url
                        break

            # Background photo
            bg_selectors = [
                "div.profile-background-image img",
                ".pv-top-card__background-image img",
                "img[data-test-id='profile-background-image']"
            ]
            for selector in bg_selectors:
                element = page.query_selector(selector)
                if element:
                    bg_url = element.get_attribute("src")
                    if bg_url:
                        profile_data["person"]["backgroundUrl"] = bg_url
                        break

            # Skills extraction
            try:
                # Try to click "Show all skills" button
                show_skills_selectors = [
                    "button:has-text('Show all skills')",
                    "button:has-text('skills')",
                    ".pv-skills-section__additional-skills",
                    "button.pvs-profile-section__action-button"
                ]
                
                for selector in show_skills_selectors:
                    try:
                        show_button = page.query_selector(selector)
                        if show_button:
                            show_button.click()
                            page.wait_for_timeout(1000)
                            break
                    except Exception:
                        continue

                skills_selectors = [
                    ".skill-categories-card li .display-flex span",
                    ".skills-section-expandable-list span.mr1",
                    "section#skills .pvs-list__outer-container .visually-hidden",
                    "section#skills .pv-skill-category-entity__name-text",
                    "#skills ~ .pvs-list__outer-container .visually-hidden",
                    ".pv-skill-categories-section li .pv-skill-category-entity__name-text",
                    ".pvs-list__outer-container .artdeco-list__item"
                ]

                skills_found = set()
                
                for selector in skills_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        for element in elements:
                            skill_text = clean_text(element.inner_text())
                            if skill_text != "N/A" and len(skill_text) > 1:
                                if not any(x in skill_text.lower() for x in ['endorsed', 'show all', 'see more', 'skills']):
                                    skills_found.add(skill_text)
                                    debug_print(f"Found skill: {skill_text}")
                    except Exception as e:
                        debug_print(f"Error with skills selector {selector}: {str(e)}")
                
                profile_data["person"]["skills"] = list(skills_found)

            except Exception as e:
                debug_print(f"Error during skills extraction: {str(e)}")

            # Follower count
            profile_data["person"]["followerCount"] = extract_follower_count(page)

            # Premium status
            premium_badge = page.query_selector("span.premium-icon")
            profile_data["person"]["premium"] = bool(premium_badge)

            # Open to work status
            open_to_work = page.query_selector("div:has-text('Open to work')")
            profile_data["person"]["openToWork"] = bool(open_to_work)

            # Experience/Positions
            experience_sections = page.query_selector_all("section#experience .artdeco-list__item")
            for section in experience_sections:
                try:
                    title_elem = section.query_selector(".t-bold span")
                    company_elem = section.query_selector(".t-normal span")
                    dates_elem = section.query_selector("time")
                    
                    if title_elem and company_elem:
                        position = {
                            "title": clean_text(title_elem.inner_text()),
                            "company": clean_text(company_elem.inner_text()),
                            "dateRange": clean_text(dates_elem.inner_text()) if dates_elem else "N/A",
                            "description": "N/A"
                        }
                        desc_elem = section.query_selector(".show-more-less-text")
                        if desc_elem:
                            position["description"] = clean_text(desc_elem.inner_text())
                        profile_data["person"]["positions"].append(position)
                except Exception as e:
                    debug_print(f"Error extracting position: {str(e)}")

            # Education/Schools
            education_sections = page.query_selector_all("section#education .artdeco-list__item")
            for section in education_sections:
                try:
                    school_elem = section.query_selector(".t-bold span")
                    degree_elem = section.query_selector(".t-normal span")
                    dates_elem = section.query_selector("time")
                    
                    if school_elem:
                        school = {
                            "schoolName": clean_text(school_elem.inner_text()),
                            "degree": clean_text(degree_elem.inner_text()) if degree_elem else "N/A",
                            "dateRange": clean_text(dates_elem.inner_text()) if dates_elem else "N/A"
                        }
                        profile_data["person"]["schools"].append(school)
                except Exception as e:
                    debug_print(f"Error extracting school: {str(e)}")

        except Exception as e:
            debug_print(f"Error during scraping: {str(e)}")
        finally:
            browser.close()

    return profile_data

def scrape_with_debug(profile_url, cookies):
    print("\nStarting comprehensive profile scrape...")
    result = scrape_linkedin_profile(profile_url, cookies, debug=True)
    print("\nFinal results:")
    print(json.dumps(result, indent=2))
    return result

# Example usage
if __name__ == "__main__":
    # Example profile data
    profile_data = {
        "profile_url": "https://www.linkedin.com/in/example-profile/",
        "cookies": [
            {
                "name": "li_at",
                "value": "YOUR_COOKIE_VALUE",
                "domain": ".linkedin.com",
                "path": "/"
            }
        ]
    }
    
    result = scrape_with_debug(profile_data["profile_url"], profile_data["cookies"])