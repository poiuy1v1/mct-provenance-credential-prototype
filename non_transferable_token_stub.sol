// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MCTNonTransferableCredentialStub
/// @custom:warning This file is a non-production, unaudited research stub.
/// @custom:warning Do not deploy this contract to mainnet, testnet, or any value-bearing environment.
/// @custom:warning It omits ERC-721 compliance, access control, metadata standards, upgrade safety, pause/recovery logic, and legal/institutional governance.
/// @notice Minimal, non-production credential stub for Paper 1 v207.
/// @dev This contract is NOT an ERC-20 token, NOT a cryptocurrency, and NOT a
/// financial asset. It is a locked credential representation inspired by the
/// ERC-5192 soulbound-token interface. It is not audited and it omits production-grade access control,
/// metadata storage, upgradeability, and ERC-721 compliance for clarity.
interface IERC5192 {
    event Locked(uint256 tokenId);
    event Unlocked(uint256 tokenId);
    function locked(uint256 tokenId) external view returns (bool);
}

contract MCTNonTransferableCredentialStub is IERC5192 {
    error NonTransferable();
    error InvalidRecipient();
    error UnknownCredential(uint256 tokenId);

    struct Credential {
        address recipient;
        bytes32 contributionHash;
        string contributionType;
        string evidenceURI;
        uint256 issuedAt;
        bool exists;
    }

    uint256 public nextTokenId = 1;
    mapping(uint256 => Credential) public credentials;
    mapping(address => uint256[]) private holderCredentials;

    event CredentialIssued(
        uint256 indexed tokenId,
        address indexed recipient,
        bytes32 indexed contributionHash,
        string contributionType,
        string evidenceURI
    );

    /// @notice Issues a locked, non-transferable research-provenance credential.
    /// @dev In a production design, issuance would be governed by curator/oracle
    /// checks and off-chain legal/institutional rules. This stub intentionally
    /// keeps only the non-transferable audit shape.
    function issueCredential(
        address recipient,
        bytes32 contributionHash,
        string calldata contributionType,
        string calldata evidenceURI
    ) external returns (uint256 tokenId) {
        if (recipient == address(0)) revert InvalidRecipient();
        tokenId = nextTokenId++;
        credentials[tokenId] = Credential({
            recipient: recipient,
            contributionHash: contributionHash,
            contributionType: contributionType,
            evidenceURI: evidenceURI,
            issuedAt: block.timestamp,
            exists: true
        });
        holderCredentials[recipient].push(tokenId);
        emit CredentialIssued(tokenId, recipient, contributionHash, contributionType, evidenceURI);
        emit Locked(tokenId);
    }

    /// @notice ERC-5192-style lock check. All issued credentials are locked.
    function locked(uint256 tokenId) external view override returns (bool) {
        if (!credentials[tokenId].exists) revert UnknownCredential(tokenId);
        return true;
    }

    /// @notice Returns all credential ids issued to a recipient.
    function credentialsOf(address recipient) external view returns (uint256[] memory) {
        return holderCredentials[recipient];
    }

    /// @notice Deliberately reverts: MCT credentials are non-transferable.
    function transferFrom(address, address, uint256) external pure {
        revert NonTransferable();
    }

    /// @notice Deliberately reverts: MCT credentials are non-transferable.
    function safeTransferFrom(address, address, uint256) external pure {
        revert NonTransferable();
    }

    /// @notice Deliberately reverts: MCT credentials are non-transferable.
    function safeTransferFrom(address, address, uint256, bytes calldata) external pure {
        revert NonTransferable();
    }
}
