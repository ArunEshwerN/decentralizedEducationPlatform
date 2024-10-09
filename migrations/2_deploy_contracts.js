const CredentialIssuer = artifacts.require("CredentialIssuer");

module.exports = function (deployer) {
    deployer.deploy(CredentialIssuer);
};
