from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import sys

def test_html():
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    try:
        driver.get("file:///usr/src/app/index.html")

        h1 = driver.find_element(By.TAG_NAME, "h1")
        assert h1 is not None, "FAIL: No h1 found"
        print("PASS: h1 found:", h1.text)

        h5 = driver.find_element(By.TAG_NAME, "h5")
        assert h5 is not None, "FAIL: No h5 found"
        print("PASS: h5 found:", h5.text)

        assert "Parbati Sapkota" in driver.title, "FAIL: Title not found"
        print("PASS: Title found:", driver.title)

        print("\nAll tests passed!")

    except Exception as e:
        print("TEST FAILED:", str(e))
        sys.exit(1)

    finally:
        driver.quit()

if __name__ == "__main__":
    test_html()