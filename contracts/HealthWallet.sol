// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HealthWallet {
    struct Record {
        string fileHash;
        uint256 timestamp;
        address patient;
    }

    // Mapping from record ID to Record details
    mapping(uint256 => Record) public records;
    
    // Mapping: patientAddress => (doctorAddress => isAuthorized)
    mapping(address => mapping(address => bool)) public permissions;

    event RecordStored(uint256 indexed recordId, string fileHash, address indexed patient);
    event AccessGranted(address indexed patient, address indexed doctor);
    event AccessRevoked(address indexed patient, address indexed doctor);

    function storeRecord(uint256 recordId, string memory fileHash) public {
        records[recordId] = Record(fileHash, block.timestamp, msg.sender);
        emit RecordStored(recordId, fileHash, msg.sender);
    }

    function grantAccess(address doctor) public {
        permissions[msg.sender][doctor] = true;
        emit AccessGranted(msg.sender, doctor);
    }

    function revokeAccess(address doctor) public {
        permissions[msg.sender][doctor] = false;
        emit AccessRevoked(msg.sender, doctor);
    }

    function checkAccess(address patient, address doctor) public view returns (bool) {
        return permissions[patient][doctor];
    }
}