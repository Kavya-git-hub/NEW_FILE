import scrapy


class DetailsSpider(scrapy.Spider):
    name = "Details"
    allowed_domains = ["www.bhhsamb.com"]
    start_urls = ["https://www.bhhsamb.com/roster/Agents"]

    def parse(self, response):
        # Locate the agent elements on the page
        agents = response.css('div.agent-card')  # Adjust the selector based on the actual page structure

        for agent in agents:
            # Extract details for each agent
            name = agent.css('h2.agent-name::text').get()
            phone = agent.css('span.agent-phone::text').get()
            email = agent.css('a.agent-email::attr(href)').re_first(r'mailto:(.+)')
            profile_url = agent.css('a::attr(href)').get()

            yield {
                'name': name,
                'phone': phone,
                'email': email,
                'profile_url': response.urljoin(profile_url),
            }

        # Handle pagination if applicable
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)





import scrapy
import json
from scrapy.crawler import CrawlerProcess

class AgentSpider(scrapy.Spider):
    name = 'agent_spider'
    start_urls = ['https://www.bhhsamb.com/agents']

    def parse(self, response):
        # Extract profile links on the current page
        profile_links = response.xpath('//div[@class="agent-card"]//a[@class="agent-link"]/@href').getall()
        for link in profile_links:
            yield response.follow(link, self.parse_agent)

        # Handle pagination and follow next page links
        next_page = response.xpath('//a[@title="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_agent(self, response):
        # Extract agent details
        name = response.xpath('//h1[@class="agent-name"]/text()').get()
        job_title = response.xpath('//p[@class="agent-title"]/text()').get()
        image_url = response.xpath('//div[@class="agent-photo"]//img/@src').get()
        address = response.xpath('//div[@class="agent-address"]//text()').get()

        contact_details = {}
        contact_items = response.xpath('//div[@class="contact-info"]//p')
        for item in contact_items:
            label = item.xpath('.//strong/text()').get().strip(": ")
            value = item.xpath('.//text()').getall()[-1].strip()
            contact_details[label] = value

        social_accounts = {}
        social_links = response.xpath('//div[@class="social-icons"]//a')
        for link in social_links:
            platform = link.xpath('./@title').get().lower()
            url = link.xpath('./@href').get()
            social_accounts[platform] = url

        offices = response.xpath('//div[@class="agent-offices"]//text()').getall()
        offices = [office.strip() for office in offices if office.strip()]

        languages = response.xpath('//div[@class="agent-languages"]//text()').getall()
        languages = [language.strip() for language in languages if language.strip()]

        description = response.xpath('//div[@class="agent-description"]//text()').get()

        yield {
            "name": name,
            "job_title": job_title,
            "image_url": response.urljoin(image_url),
            "address": address,
            "contact_details": contact_details,
            "social_accounts": social_accounts,
            "offices": offices,
            "languages": languages,
            "description": description,
        }

# Configure the Scrapy process
process = CrawlerProcess(settings={
    'FEEDS': {
        'agents.json': {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 4,
        },
        'agents.csv': {
            'format': 'csv',
            'encoding': 'utf8',
            'store_empty': False,
        },
    },
    'LOG_LEVEL': 'INFO',
    'ROBOTSTXT_OBEY': True,
})

if __name__ == "__main__":
    process.crawl(AgentSpider)
    process.start()




import scrapy

class AgentSpider(scrapy.Spider):
    name = 'agent'
    start_urls = [
        'https://www.bhhsamb.com/agents/51039-didi-pache',
    ]

    def parse(self, response):
        yield {
            'name': response.xpath("//h1[@class='agent-name']/text()").get().strip(),
            'job_title': response.xpath("//div[@class='agent-title']/text()").get().strip(),
            'image_url': response.xpath("//img[@class='agent-photo']/@src").get(),
            'address': " ".join(response.xpath("//div[@class='agent-address']/text()").getall()).strip(),
            'contact_details': {
                contact.xpath("span[@class='contact-label']/text()").get().strip(): contact.xpath("span[@class='contact-number']/text()").get().strip()
                for contact in response.xpath("//div[@class='contact-item']")
            },
            'social_accounts': {
                account.xpath("@class").re_first("social-(\w+)"): account.xpath("@href").get()
                for account in response.xpath("//a[contains(@class, 'social')]")
            },
            'offices': response.xpath("//div[@class='offices']/text()").getall(),
            'languages': response.xpath("//div[@class='languages']/text()").getall(),
            'description': " ".join(response.xpath("//div[@class='agent-description']/p//text()").getall()).strip(),
        }
