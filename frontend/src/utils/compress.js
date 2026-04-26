import * as fflate from 'fflate';

export function compressBigIntSync(bigIntValue) {
    // 1. BigInt to Uint8Array
    let hex = bigIntValue.toString(16);
    if (hex.length % 2 !== 0) hex = '0' + hex;
    const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));

    // 2. Synchronous Zlib/Deflate (similar speed to zstd for these sizes)
    const compressedBytes = fflate.zlibSync(bytes);

    // 3. Uint8Array back to BigInt
    const compressedHex = Array.from(compressedBytes)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

    return BigInt('0x' + compressedHex);
}

export function decompressBigIntSync(compressedBigInt) {
    // 1. BigInt to Uint8Array
    let hex = compressedBigInt.toString(16);
    if (hex.length % 2 !== 0) hex = '0' + hex;
    const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));

    // 2. Synchronous Unzlib
    const decompressedBytes = fflate.unzlibSync(bytes);

    // 3. Uint8Array back to original BigInt
    const originalHex = Array.from(decompressedBytes)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

    return BigInt('0x' + originalHex);
}
