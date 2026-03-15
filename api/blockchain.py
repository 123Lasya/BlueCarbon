from web3 import Web3
import json

RPC_URL = ""

PRIVATE_KEY = ""

CONTRACT_ADDRESS = ""

w3 = Web3(Web3.HTTPProvider(RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)

# ABI of smart contract
ABI =[     ]
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

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return w3.to_hex(tx_hash)
