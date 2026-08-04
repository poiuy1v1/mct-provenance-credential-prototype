// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/// @custom:warning Non-production, unaudited, non-deployable research stub.
contract NonTransferableCredentialStub { error NonTransferable(); function transferFrom(address,address,uint256) external pure { revert NonTransferable(); } }
