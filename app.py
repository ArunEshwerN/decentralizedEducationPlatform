from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from web3 import Web3
import httpx

app = Flask(__name__)
app.secret_key = 'abc'  # Set a secret key for sessions

# Use httpx to send files to IPFS via API
def add_file_to_ipfs(file):
    files = {'file': file}
    response = httpx.post('http://127.0.0.1:5001/api/v0/add', files=files)
    return response.json()

# Connect to local Ethereum node (Ganache)
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check if connection is successful
if web3.is_connected():
    print("Connected to Ganache")

# Your deployed contract address and ABI
contract_address = '0x5C3F71c488eAF4c8F9EC4916287c4acb261be89D'
contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "courseName",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "ipfsHash",
                "type": "string"
            }
        ],
        "name": "CourseCompleted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "courseName",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "courseFee",
                "type": "uint256"
            }
        ],
        "name": "CoursePurchased",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "userId",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "credentialHash",
                "type": "string"
            }
        ],
        "name": "CredentialIssued",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "message",
                "type": "string"
            }
        ],
        "name": "DebugLog",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "refundAmount",
                "type": "uint256"
            }
        ],
        "name": "EtherRefunded",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "name": "assignmentExists",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "credentials",
        "outputs": [
            {
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "userId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "credentialHash",
                "type": "string"
            },
            {
                "internalType": "bool",
                "name": "isValid",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "name": "userCourses",
        "outputs": [
            {
                "internalType": "string",
                "name": "courseName",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "courseFee",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "isPurchased",
                "type": "bool"
            },
            {
                "internalType": "bool",
                "name": "isCompleted",
                "type": "bool"
            },
            {
                "internalType": "string",
                "name": "assignmentHash",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "_userId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "_credentialHash",
                "type": "string"
            }
        ],
        "name": "issueCredential",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_user",
                "type": "address"
            }
        ],
        "name": "validateCredential",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_user",
                "type": "address"
            }
        ],
        "name": "getCredential",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            },
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "courseName",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "courseFee",
                "type": "uint256"
            }
        ],
        "name": "purchaseCourse",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
        "payable": True
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "courseName",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "ipfsHash",
                "type": "string"
            }
        ],
        "name": "completeCourse",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "fundContract",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
        "payable": True
    },
    {
        "inputs": [],
        "name": "getContractBalance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    }
]
























# Load the contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# @app.route('/')
# def home():
#     return render_template('index.html')  # Render the form page

@app.route('/issue_credential', methods=['POST'])
def issue_credential():
    try:
        name = request.form['name']
        user_id = request.form['user_id']
        file = request.files['credential_file']
        
        # Add file to IPFS and get the hash
        ipfs_response = add_file_to_ipfs(file)
        credential_hash = ipfs_response['Hash']

        print(f"IPFS Hash: {credential_hash}")  # Add a print statement to check IPFS hash
        
        # Send transaction to issue credential using the IPFS hash
        tx_hash = contract.functions.issueCredential(name, user_id, credential_hash).transact({
            'from': web3.eth.accounts[0]
        })
        web3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Transaction Hash: {tx_hash.hex()}")  # Log the transaction hash

        return jsonify({
            "status": "Credential Issued Successfully",
            "ipfs_hash": credential_hash  # Return the IPFS hash
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# @app.route('/validate_credential', methods=['POST'])
# def validate_credential():
#     try:
#         # Access the ethereum address from the form
#         ethereum_address = request.form['ethereum_address']
        
#         # Call the smart contract to validate the credential
#         is_valid = contract.functions.validateCredential(ethereum_address).call()
        
#         return jsonify({"is_valid": is_valid})
    
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route('/validate_credential', methods=['POST'])
def validate_credential():
    try:
        ethereum_address = request.form['ethereum_address']
        is_valid = contract.functions.validateCredential(ethereum_address).call()
        if is_valid:
            session['logged_in'] = True
        return jsonify({"is_valid": is_valid})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/purchase_course', methods=['POST'])
def purchase_course():
    user_address = request.form['user_address']
    course_fee = web3.to_wei(request.form['course_fee'], 'ether')
    try:
        tx_hash = contract.functions.purchaseCourse().transact({
            'from': user_address,
            'value': course_fee  # Ether to send
        })
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"status": "Course Purchased Successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/complete_course', methods=['POST'])
def complete_course():
    user_address = request.form['user_address']
    try:
        tx_hash = contract.functions.completeCourse().transact({
            'from': web3.eth.accounts[0]  # Contract owner issues the reward
        })
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"status": "Course Completed and Reward Issued"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/')
def landing():
    if 'logged_in' in session:
        return redirect(url_for('main'))
    return render_template('landing.html')

@app.route('/main')
def main():
    if 'logged_in' not in session:
        return redirect(url_for('landing'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('landing'))




if __name__ == '__main__':
    app.run(debug=True)
