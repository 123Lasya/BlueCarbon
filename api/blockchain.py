from web3 import Web3
import json

RPC_URL = ""

PRIVATE_KEY = ""

CONTRACT_ADDRESS = ""

w3 = Web3(Web3.HTTPProvider(RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)

# ABI of smart contract
ABI =[     ]
############ smart contract code ##############
# // SPDX-License-Identifier: MIT
# pragma solidity ^0.8.20;

# contract BlueCarbonRegistry {

#     address public governmentAuthority;

#     constructor() {
#         governmentAuthority = msg.sender;
#     }

#     modifier onlyGovernment() {
#         require(msg.sender == governmentAuthority, "Only government can perform this action");
#         _;
#     }

#     struct CarbonCredit {
#         uint256 creditId;
#         string projectId;
#         address owner;
#         uint256 creditsAmount;
#         uint256 carbonAmountTons;
#         string location;
#         uint256 timestamp;
#         bool active;
#     }

#     struct CreditTransaction {
#         uint256 transactionId;
#         uint256 creditId;
#         address seller;
#         address buyer;
#         uint256 creditsTransferred;
#         uint256 pricePerCredit;
#         uint256 totalValue;
#         uint256 timestamp;
#     }

#     uint256 public nextCreditId = 1;
#     uint256 public nextTransactionId = 1;

#     mapping(uint256 => CarbonCredit) public carbonCredits;
#     mapping(uint256 => CreditTransaction) public creditTransactions;

#     event CarbonCreditMinted(
#         uint256 creditId,
#         string projectId,
#         address owner,
#         uint256 creditsAmount
#     );

#     event CarbonCreditTransferred(
#         uint256 transactionId,
#         uint256 creditId,
#         address seller,
#         address buyer,
#         uint256 creditsTransferred
#     );

#     // ==========================
#     //  Mint Carbon Credits
#     // ==========================
#     function mintCarbonCredits(
#         string memory projectId,
#         address owner,
#         uint256 creditsAmount,
#         uint256 carbonAmountTons,
#         string memory location
#     ) public onlyGovernment {

#         carbonCredits[nextCreditId] = CarbonCredit(
#             nextCreditId,
#             projectId,
#             owner,
#             creditsAmount,
#             carbonAmountTons,
#             location,
#             block.timestamp,
#             true
#         );

#         emit CarbonCreditMinted(
#             nextCreditId,
#             projectId,
#             owner,
#             creditsAmount
#         );

#         nextCreditId++;
#     }

#     // ==========================
#     // Transfer Carbon Credits
#     // ==========================
#     function transferCarbonCredits(
#         uint256 creditId,
#         address buyer,
#         uint256 creditsToTransfer,
#         uint256 pricePerCredit
#     ) public {

#         CarbonCredit storage credit = carbonCredits[creditId];

#         require(credit.active == true, "Credit batch not active");
#         require(credit.creditsAmount >= creditsToTransfer, "Not enough credits available");

#         uint256 totalValue = creditsToTransfer * pricePerCredit;

#         credit.creditsAmount -= creditsToTransfer;

#         creditTransactions[nextTransactionId] = CreditTransaction(
#             nextTransactionId,
#             creditId,
#             msg.sender,
#             buyer,
#             creditsToTransfer,
#             pricePerCredit,
#             totalValue,
#             block.timestamp
#         );

#         emit CarbonCreditTransferred(
#             nextTransactionId,
#             creditId,
#             msg.sender,
#             buyer,
#             creditsToTransfer
#         );

#         nextTransactionId++;
#     }

#     // ==========================
#     // View Credit Details
#     // ==========================
#     function getCredit(uint256 creditId) public view returns (CarbonCredit memory) {
#         return carbonCredits[creditId];
#     }

#     // ==========================
#     // View Transaction Details
#     // ==========================
#     function getTransaction(uint256 transactionId) public view returns (CreditTransaction memory) {
#         return creditTransactions[transactionId];
#     }

# }
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
