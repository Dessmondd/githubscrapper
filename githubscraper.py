from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import argparse
import time


parser = argparse.ArgumentParser(description='GitHub Scraper')
parser.add_argument('-g', '--commits', type=int, default=None, help='Specify the number of commits to check')

args = parser.parse_args()



def check_sensitive_info(html_content):
    sensitive_keywords = ['password', 'api_key', 'secret_key', 'access_token']  # Add more keywords if needed
    for keyword in sensitive_keywords:
        if keyword in html_content.lower():
            return True, keyword
    return False, None

lets_scrape = input("Enter the GitHub username: ")
repo = f"https://github.com/{lets_scrape}?tab=repositories"

chrome_options = Options()  # Run Chrome in headless mode
chrome_service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get(repo)
time.sleep(5)  # Allow time for the page to load

	# Find all repository links
repo_links = driver.find_elements(By.XPATH, '//h3[@class="wb-break-all"]/a')
links = [link.get_attribute('href') for link in repo_links]

	# Loop through each repository link
for link in links:
    driver.get(link)  # Navigate to the repository link directly
    time.sleep(2)

    		# Scroll to the "Code" tab to bring it into view
    code_tab = driver.find_element(By.XPATH, '//span[contains(text(), "Code")]')
    driver.execute_script("arguments[0].click();", code_tab)
    time.sleep(2)

    		
    driver.get(link + '/commits') # Navigate to the commits page through the URL (alternate approach)
    time.sleep(2)

    # Find all file links in the commits page
    file_links = driver.find_elements(By.XPATH, '//a[contains(@class, "Link--primary")]')
    
    # Check if the number of commits to check is specified
    commits_to_check = args.commits if args.commits else len(file_links)
    file_urls = [file_link.get_attribute('href') for file_link in file_links[:commits_to_check]]

    
    for file_url in file_urls:
        driver.get(file_url)
        time.sleep(2)

        # Extract HTML content
        html_content = driver.find_element(By.TAG_NAME, 'body').text

        # Check for sensitive information
        sensitive, keyword = check_sensitive_info(html_content)
        if sensitive:
            print(f"Potential sensitive information found in {file_url}: {keyword}")

driver.quit()