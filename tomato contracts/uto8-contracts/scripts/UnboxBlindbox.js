//generate an array which contains 1 to length of BlindBox's total amount
const web3 = require('web3');
//const express = require('express');
const Tx = require('ethereumjs-tx').Transaction;
const piamonContractAddress = '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512';
const piamonContractABI = require('../piamon-abi.json');
const web3js = new web3(
  //new web3.providers.HttpProvider('https://rinkeby.infura.io/YOUR_API_KEY')
  new web3.providers.HttpProvider('http://127.0.0.1:8545/')
);

const myAddress = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';
const privateKey = Buffer.from(
  'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
  'hex'
);
var contract = new web3js.eth.Contract(
  piamonContractABI,
  piamonContractAddress
);

async function main() {
  // var piamonBoxArray = [];
  // for (let i = 1; i < 8000; i++) {
  //   piamonBoxArray.push(i);
  // }

  // shuffle(piamonBoxArray);
  // //console.log(piamonBoxArray);

  await sendRawTransaction(txData);
}

const txData = {
  from: myAddress,
  gasPrice: web3js.utils.toHex(20 * 1e9),
  gasLimit: web3js.utils.toHex(210000),
  to: piamonContractAddress,
  value: '0x0',
  data: contract.methods.addPiamonBoxId(0, 1).encodeABI(),
};

const sendRawTransaction = (txData) =>
  web3js.eth.getTransactionCount(myAddress).then((txCount) => {
    console.log(txData);
    const newNonce = web3.utils.toHex(txCount);
    const transaction = new Tx(
      { ...txData, nonce: newNonce },
      { hardfork: 'homestead' }
    );
    transaction.sign(privateKey);
    const serializedTx = transaction.serialize().toString('hex');
    web3js.eth
      .sendSignedTransaction('0x' + serializedTx)
      .on('transactionHash', (txHash) => {
        console.log('transactionHash:', txHash);
      })
      .on('receipt', (receipt) => {
        console.log('receipt:', receipt);
      })
      .on('confirmation', (confirmationNumber, receipt) => {
        if (confirmationNumber >= 1) {
          console.log('confirmations:', confirmationNumber, receipt);
        }
      })
      .on('error:', (error) => {
        console.error(error);
      });
  });

// function shuffle(array) {
//   let currentIndex = array.length,
//     randomIndex;

//   // While there remain elements to shuffle.
//   while (currentIndex != 0) {
//     // Pick a remaining element.
//     randomIndex = Math.floor(Math.random() * currentIndex);
//     currentIndex--;

//     // And swap it with the current element.
//     [array[currentIndex], array[randomIndex]] = [
//       array[randomIndex],
//       array[currentIndex],
//     ];
//   }

//   return array;
// }

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

//randomize the array

//loop the array to upload to SalesBatch contract
