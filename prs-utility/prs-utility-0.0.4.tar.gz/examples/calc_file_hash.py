"""计算文件的 hash 值"""
import prs_utility

with open(__file__) as fp:
    content = fp.read()
file_hash = prs_utility.keccak256(content)
print('file hash:', file_hash)
