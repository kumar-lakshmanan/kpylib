__created__ = "24-Apr-2025"
__updated__ = "2025-07-07"
__author__ = "kayma"

from playwright.sync_api import sync_playwright, Playwright
import kTools

class WebScrapper:
    
    def __init__(self, baseUrl=None, scrappingLogicFn=None, headless=True):
        self.tls = kTools.KTools()
        
        self.headless = headless
        
        self.baseUrl = baseUrl
        
        self.scrappingLogicFn = scrappingLogicFn
        
        self.browser = None
        
        self.page = None
        
        self.scrappedData = None
        
    def doScrap(self):
        self.tls.debug("Scrapping starts...")
        self.scrappedData = None
        
        if self.baseUrl and self.scrappingLogicFn:
            
            #Get playwright manager
            with sync_playwright() as pw:
                
                #Open Browser
                self.browser = pw.chromium.launch(headless=self.headless)
                self.tls.debug("Browser ready")
                
                #Open Tab
                self.page = self.browser.new_page()                
                
                #Navigate to
                self.tls.debug(f"Loading page {self.baseUrl}")
                self.page.goto(self.baseUrl)
                
                self.tls.debug(f"Running scrapping logic...")
                self.scrappedData = self.scrappingLogicFn(self.page, self.browser, pw)
                    
                # Close the browser
                self.tls.debug(f"Scrapping done!")
                self.browser.close()
                
        return self.scrappedData     


def localScrapper(page, browser, playright):
    returnValue = None
    
    ftdTag = page.locator("span:has-text('First Trade Date')")
    grandparent = ftdTag.locator("..").locator("..")  
    children = grandparent.locator(":scope > *")
    count = children.count()
    if count==2:
        child = children.nth(1)
        if child.evaluate('el => el.tagName') == "SPAN":
            returnValue = child.text_content()

    return returnValue
         
    
# Example Usage
if __name__ == '__main__':
    
    ws = WebScrapper()
    ws.baseUrl = "https://messari.io/project/cardano/"
    ws.headless = True
    ws.scrappingLogicFn = localScrapper
    ret = ws.doScrap()
    print(f"Fetched Return: {ret}")
    