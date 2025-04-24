import requests
import csv
from bs4 import BeautifulSoup

# Etherscan Verified Contracts URL
base_url = "https://etherscan.io/contractsVerified/"
pages_to_scrape = 5  # 设置爬取的页数，可调整
contracts = []

# 遍历多个页面
for page in range(1, pages_to_scrape + 1):
    url = f"{base_url}{page}?ps=100"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code != 200:
        print(f"无法访问 {url}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    table_rows = soup.select("table tbody tr")

    for row in table_rows:
        columns = row.find_all("td")
        if len(columns) >= 2:  # 确保有数据
            # 提取合约地址
            contract_link = columns[0].find("a", href=True)
            if contract_link and contract_link["href"].startswith("/address/"):
                contract_address = contract_link["href"].split("/")[-1]  # 从URL中提取地址
                contract_name = columns[1].text.strip()
                contracts.append([contract_address, contract_name])

    print(f"已爬取 {url}")

# 保存到 CSV 文件
csv_filename = "ADDRESS.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Contract Address", "Contract Name"])
    writer.writerows(contracts)

print(f"数据已保存至 {csv_filename}")
# 去CSV把#code去掉