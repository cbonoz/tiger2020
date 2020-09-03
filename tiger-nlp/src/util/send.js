const CKB = require('@nervosnetwork/ckb-sdk-core').default;
/* eslint-disable */

export const sendCapacity = async (key, capacity, dest) => {
	const nodeUrl = process.env.NODE_URL || 'http://localhost:8114'; // example node url
	const privateKey =
		process.env.PRIV_KEY || key || '0x0c0bf4655054a15a07c8384438864cf4a31ea2256a60f5aef57c68b0550d6103';
	const blockAssemblerCodeHash = '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8'; // transcribe the block_assembler.code_hash in the ckb.toml from the ckb project

	const ckb = new CKB(nodeUrl); // instantiate the JS SDK with provided node url

	const secp256k1Dep = await ckb.loadSecp256k1Dep(); // load the dependencies of secp256k1 algorithm which is used to verify the signature in transaction's witnesses.

	const publicKey = ckb.utils.privateKeyToPublicKey(privateKey);
	/**
   * to see the public key
   */

	// console.log(`Public key: ${publicKey}`)

	const publicKeyHash = `0x${ckb.utils.blake160(publicKey, 'hex')}`;
	/**
   * to see the public key hash
   */
	// console.log(`Public key hash: ${publicKeyHash}`)

	const addresses = {
		mainnetAddress: ckb.utils.pubkeyToAddress(publicKey, {
			prefix: 'ckb'
		}),
		testnetAddress: ckb.utils.pubkeyToAddress(publicKey, {
			prefix: 'ckt'
		})
	};

	/**
   * to see the addresses
   */
	console.log(JSON.stringify(addresses, null, 2));

	/**
   * calculate the lockHash by the address publicKeyHash
   * 1. the publicKeyHash of the address is required in the args field of lock script
   * 2. compose the lock script with the code hash(as a miner, we use blockAssemblerCodeHash here), and args
   * 3. calculate the hash of lock script via ckb.utils.scriptToHash method
   */

	const lockScript = {
		hashType: 'type',
		codeHash: blockAssemblerCodeHash,
		args: publicKeyHash
	};
	/**
   * to see the lock script
   */
	// console.log(JSON.stringify(lockScript, null, 2))

	const lockHash = ckb.utils.scriptToHash(lockScript);
	/**
   * to see the lock hash
   */
	console.log(lockHash);

	// method to fetch all unspent cells by lock hash
	const unspentCells = await ckb.loadCells({
		lockHash
	});

	/**
   * to see the unspent cells
   */
	console.log(unspentCells, capacity);

	/**
   * send transaction
   */
	const toAddress = ckb.utils.privateKeyToAddress(
		dest.includes('0x') ? dest : '0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
		{
			prefix: 'ckt'
		}
	);

	const rawTransaction = ckb.generateRawTransaction({
		fromAddress: addresses.testnetAddress,
		toAddress,
		capacity: BigInt(capacity),
		fee: BigInt(100000),
		safeMode: true,
		cells: unspentCells,
		deps: ckb.config.secp256k1Dep
	});

	rawTransaction.witnesses = rawTransaction.inputs.map(() => '0x');
	rawTransaction.witnesses[0] = {
		lock: '',
		inputType: '',
		outputType: ''
	};

	const signedTx = ckb.signTransaction(privateKey)(rawTransaction);
	/**
   * to see the signed transaction
   */
	console.log(JSON.stringify(signedTx, null, 2));

	const realTxHash = await ckb.rpc.sendTransaction(signedTx);
	/**
   * to see the real transaction hash
   */
	console.log(`The real transaction hash is: ${realTxHash}`);
	return realTxHash;
};
