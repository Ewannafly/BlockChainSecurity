import os
import requests
import time
import csv
import json

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

# 从 Etherscan API 获取合约的 Runtime Bytecode
def get_runtime_bytecode(address):
    url = f"{BASE_URL}?module=proxy&action=eth_getCode&address={address}&tag=latest&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "result" in data and data["result"] != "0x":
        return data["result"]  # 直接返回 Runtime Bytecode
    return None

# CSV 文件名（存储合约地址）
csv_filename = "ADDRESS.csv"
contract_addresses = read_contract_addresses(csv_filename)

# 创建 bytecode 目录（如果不存在）
os.makedirs("bytecode", exist_ok=True)

# 逐个查询合约的 Runtime Bytecode
for address in contract_addresses:
    runtime_bytecode = get_runtime_bytecode(address)

    if runtime_bytecode:
        # 保存 runtime bytecode 到 bytecode 目录
        filename = os.path.join("bytecode", f"{address}_runtime_bytecode.txt")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(runtime_bytecode)

        print(f"合约 {address} 的 Runtime Bytecode 已保存为 {filename}.")
    else:
        print(f"未能获取合约 {address} 的 Runtime Bytecode.")

    # 避免 API 速率限制，暂停 1 秒
    time.sleep(1)

print("所有合约 Runtime Bytecode 下载完成！")
