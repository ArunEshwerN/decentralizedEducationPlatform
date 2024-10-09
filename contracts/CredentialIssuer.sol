// SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;
    contract CredentialIssuer {
        struct Credential {
        string name;
        string userId;
        string credentialHash; // IPFS hash for credential storage
        bool isValid;
    }
    struct Course {
        string courseName;
        uint courseFee; // Fee in wei (Ether)
        bool isPurchased;
        bool isCompleted;
        string assignmentHash; // IPFS hash for the assignment
    }
    mapping(address => Credential) public credentials; // Mapping for issued credentials
    mapping(address => mapping(string => Course)) public userCourses; // Track course data for each user by course name
    mapping(string => bool) public assignmentExists; // To check if the assignment already exists (plagiarism check)
    event CredentialIssued(address indexed user, string name, string userId, string credentialHash);
    event CoursePurchased(address indexed user, string courseName, uint courseFee);
    event CourseCompleted(address indexed user, string courseName, string ipfsHash);
    event EtherRefunded(address indexed user, uint refundAmount);
    event DebugLog(address indexed user, string message);

    // Issue a credential for a user and store IPFS hash
    function issueCredential(string memory _name, string memory _userId, string memory _credentialHash) public {
    credentials[msg.sender] = Credential({
    name: _name,
    userId: _userId,
    credentialHash: _credentialHash,
    isValid: true
    });
    emit CredentialIssued(msg.sender, _name, _userId, _credentialHash);
    }
    // Validate if a credential exists and is valid
    function validateCredential(address _user) public view returns (bool) {
    return credentials[_user].isValid;
    }
    // Get credential information including the IPFS hash
    function getCredential(address _user) public view returns (string memory, string memory, string memory, bool) {
    Credential memory cred = credentials[_user];
    return (cred.name, cred.userId, cred.credentialHash, cred.isValid);
    }
    // Purchase a course
    function purchaseCourse(string memory courseName, uint courseFee) public payable {
    require(msg.value >= courseFee, "Insufficient Ether to purchase the course.");
    require(!userCourses[msg.sender][courseName].isPurchased, "You have already purchased this course.");
    // Store course data for the user
    userCourses[msg.sender][courseName] = Course({
    courseName: courseName,
    courseFee: courseFee,
    isPurchased: true,
    isCompleted: false,
    assignmentHash: ""
    });
    emit CoursePurchased(msg.sender, courseName, courseFee);
    }

    // Submit an assignment and complete the course
    function completeCourse(string memory courseName, string memory ipfsHash) public {
        require(userCourses[msg.sender][courseName].isPurchased, "You haven't purchased this course.");
        require(!userCourses[msg.sender][courseName].isCompleted, "You have already completed this course.");

        emit DebugLog(msg.sender, "Passed purchase and completion checks");

        // Store assignment hash and mark the course as completed
        userCourses[msg.sender][courseName].assignmentHash = ipfsHash;
        userCourses[msg.sender][courseName].isCompleted = true;
        emit CourseCompleted(msg.sender, courseName, ipfsHash);

        // Refund double the course fee
        uint refundAmount = userCourses[msg.sender][courseName].courseFee * 2;
        require(address(this).balance >= refundAmount, "Contract has insufficient funds to issue refund.");
        
        emit DebugLog(msg.sender, "Passed refund check, transferring refund");

        // Transfer the refund to the user
        payable(msg.sender).transfer(refundAmount);
        emit EtherRefunded(msg.sender, refundAmount);
    }


    // Function to fund the contract with Ether (for refund payouts)
    function fundContract() public payable {}
    // Function to check the contract balance
    function getContractBalance() public view returns (uint) {
    return address(this).balance;
    }
}