"""根据 PRS 协议组合 block data, 并且使用 privateKey 进行签名"""
import prs_utility

with open(__file__) as fp:
    content = fp.read()

data = {
    'file_hash': prs_utility.keccak256(content),
}
key_pair = prs_utility.create_key_pair()
private_key = key_pair['privateKey']
sig = prs_utility.sign_block_data(data, private_key)
print('signature:', sig)
