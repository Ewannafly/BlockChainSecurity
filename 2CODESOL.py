import requests
import time
import csv
import os

# 替换为你的 Etherscan API Key
API_KEY = "JT72N13QWX63DDTBVS9MSC6WP5JZ12PA7K"
BASE_URL = "https://api.etherscan.io/api"

# 读取 CSV 文件中的智能合约地址
def read_contract_addresses(csv_filename):
    addresses = []
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        for row in reader:
            if row:  # 确保不为空
                addresses.append(row[0])  # 取第一列（合约地址）
    return addresses

# CSV 文件名（存储合约地址）
csv_filename = "ADDRESS.csv"
contract_addresses = read_contract_addresses(csv_filename)

# 创建 source_code 目录（如果不存在）
os.makedirs("source_code", exist_ok=True)

# 逐个查询智能合约源码
for address in contract_addresses:
    url = f"{BASE_URL}?module=contract&action=getsourcecode&address={address}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "1" and data["result"]:
        contract_info = data["result"][0]
        contract_name = contract_info["ContractName"]
        source_code = contract_info["SourceCode"]

        # 处理无合约名的情况
        contract_name = contract_name if contract_name else "UnknownContract"

        # 保存源码到 source_code 目录
        filename = os.path.join("source_code", f"{address}.sol")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(source_code)

        print(f"合约 {contract_name} ({address}) 的源码已保存为 {filename}.")
    
    # 避免 API 速率限制，暂停 1 秒
    time.sleep(1)

print("所有合约源码下载完成！")
