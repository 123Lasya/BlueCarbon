# from web3 import Web3
# import json

# RPC_URL = "hghhvg"

# PRIVATE_KEY = "njnjn"

# CONTRACT_ADDRESS = "jnjnjn"

# w3 = Web3(Web3.HTTPProvider(RPC_URL))

# account = w3.eth.account.from_key(PRIVATE_KEY)

# # ABI of smart contract
# ABI =[]
# contract = w3.eth.contract(
#     address=CONTRACT_ADDRESS,
#     abi=ABI
# )
# def mint_credits(project_id, owner, credits, carbon_amount, location):

#     nonce = w3.eth.get_transaction_count(account.address)

#     tx = contract.functions.mintCarbonCredits(
#         project_id,
#         owner,
#         credits,
#         carbon_amount,
#         location
#     ).build_transaction({
#         "from": account.address,
#         "nonce": nonce,
#         "gas": 2000000,
#         "gasPrice": w3.to_wei("20", "gwei")
#     })

#     signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

#     return w3.to_hex(tx_hash)
# def transfer_credits(credit_id, buyer, credits, price):

#     nonce = w3.eth.get_transaction_count(account.address)

#     tx = contract.functions.transferCarbonCredits(
#         credit_id,
#         buyer,
#         credits,
#         price
#     ).build_transaction({
#         "from": account.address,
#         "nonce": nonce,
#         "gas": 2000000,
#         "gasPrice": w3.to_wei("20", "gwei")
#     })

#     signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

#     return w3.to_hex(tx_hash)
from web3 import Web3
import json

RPC_URL = "http://10.97.108.144:7545"

PRIVATE_KEY = "0xbee88a90dddba72f785abf84852a42a82aedfc60140e5ed81e33e39b3a629d7b"

CONTRACT_ADDRESS = "0xd2a5bC10698FD955D1Fe6cb468a17809A08fd005"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)

# ABI of smart contract
ABI = [
    {
        "inputs":[
            {"internalType":"string","name":"projectId","type":"string"},
            {"internalType":"address","name":"owner","type":"address"},
            {"internalType":"uint256","name":"creditsAmount","type":"uint256"},
            {"internalType":"uint256","name":"carbonAmountTons","type":"uint256"},
            {"internalType":"string","name":"location","type":"string"}
        ],
        "name":"mintCarbonCredits",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    },
    {
        "inputs":[
            {"internalType":"uint256","name":"creditId","type":"uint256"},
            {"internalType":"address","name":"buyer","type":"address"},
            {"internalType":"uint256","name":"creditsToTransfer","type":"uint256"},
            {"internalType":"uint256","name":"pricePerCredit","type":"uint256"}
        ],
        "name":"transferCarbonCredits",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    }
]

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)
def mint_credits(project_id, owner, credits, carbon_amount, location):

    nonce = w3.eth.get_transaction_count(account.address)

    tx = contract.functions.mintCarbonCredits(
        project_id,
        owner,
        credits,
        carbon_amount,
        location
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 2000000,
        "gasPrice": w3.to_wei("20", "gwei")
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return w3.to_hex(tx_hash)
def transfer_credits(credit_id, buyer, credits, price):

    nonce = w3.eth.get_transaction_count(account.address)

    tx = contract.functions.transferCarbonCredits(
        credit_id,
        buyer,
        credits,
        price
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 2000000,
        "gasPrice": w3.to_wei("20", "gwei")
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return w3.to_hex(tx_hash)