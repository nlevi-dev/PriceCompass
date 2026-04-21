
const chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
const base = BigInt(chars.length);

export function bitsToBaseN(bits) {
    let n = BigInt(bits);
    let result;
    if (n === 0n) {
        result = chars[0];
    } else {
        let arr = [];
        while (n > 0n) {
            arr.push(chars[Number(n % base)]);
            n = n / base;
        }
        result = arr.reverse().join('');
    }
    return result;
}

export function baseNtoBits(bNString) {
    const str = String(bNString);
    let result = 0n;
    for (let i = 0; i < str.length; i++) {
        const char = str[i];
        const index = chars.indexOf(char);
        if (index === -1) {
            throw new Error(`Invalid character "${char}" found in BaseN string!`);
        }
        result = (result * base) + BigInt(index);
    }
    const maxBits = Math.ceil(str.length * Math.log2(Number(base)));
    return BigInt.asUintN(maxBits, result);
}

export function bitsToInt(bits, from, len) {
    const b = BigInt(bits);
    const start = BigInt(from);
    const rangeLength = BigInt(len);
    const shifted = b >> start;
    const mask = (1n << rangeLength) - 1n;
    return Number(shifted & mask);
}

export function intToBits(number) {
    return BigInt(number);
}

export function bitsToFloat(bits, from, lenMantissa, lenExponent, round = []) {
    const b = BigInt(bits);
    const start = BigInt(from);
    const m_mask = (1n << BigInt(lenMantissa)) - 1n;
    const m_bits = (b >> start) & m_mask;
    const e_mask = (1n << BigInt(lenExponent)) - 1n;
    const e_bits = (b >> (start + BigInt(lenMantissa))) & e_mask;

    const bias = (1 << (lenExponent - 1)) - 1;
    const max_e = e_mask;

    if (e_bits === max_e && m_bits === 0n) {
        return null;
    }

    let float;

    if (e_bits === 0n) {
        float = Number(m_bits) * Math.pow(2, 1 - bias - lenMantissa);
    } else {
        const mantissaValue = 1 + (Number(m_bits) / Math.pow(2, lenMantissa));
        const actualExponent = Number(e_bits) - bias;
        float = mantissaValue * Math.pow(2, actualExponent);
    }

    for (const [threshold, precision] of round) {
        if (float <= threshold) {
            const p = Math.pow(10, precision);
            return Math.round(float * p) / p;
        }
    }

    return float;
}

export function floatToBits(number, lenMantissa, lenExponent) {
    if (number === null) {
        const max_e = (1n << BigInt(lenExponent)) - 1n;
        return max_e << BigInt(lenMantissa);
    }

    if (number === 0) return 0n;

    const bias = (1 << (lenExponent - 1)) - 1;
    const max_e = (1 << lenExponent) - 1;
    
    let exponent = Math.floor(Math.log2(number));
    let biasedExponent = exponent + bias;

    let m_bits;
    let e_bits;

    if (biasedExponent <= 0) {
        e_bits = 0n;
        m_bits = BigInt(Math.round(number / Math.pow(2, 1 - bias - lenMantissa)));
    } else if (biasedExponent >= max_e) {
        e_bits = BigInt(max_e - 1);
        m_bits = (1n << BigInt(lenMantissa)) - 1n;
    } else {
        e_bits = BigInt(biasedExponent);
        const fractionalPart = (number / Math.pow(2, exponent)) - 1;
        m_bits = BigInt(Math.round(fractionalPart * Math.pow(2, lenMantissa)));
    }

    return (e_bits << BigInt(lenMantissa)) | m_bits;
}

export function bitsToBitmask(bits, from, len) {
    const b = BigInt(bits);
    const start = Number(from);
    const rangeLength = BigInt(len);
    const result = [];
    let shifted = b >> BigInt(start);
    for (let i = 0; i < rangeLength; i++) {
        result.push((shifted & 1n) === 1n);
        shifted >>= 1n;
    }
    return result;
}

export function bitmaskToBits(bitmask) {
    if (!Array.isArray(bitmask)) {
        throw new Error("Input must be an array of booleans.");
    }
    let result = 0n;
    for (let i = 0; i < bitmask.length; i++) {
        if (bitmask[i]) {
            result |= (1n << BigInt(i));
        }
    }
    return result;
}

export function appendBits(segments) {
    let result = 0n;
    let currentShift = 0n;
    for (const [ value, length ] of segments) {
        const bValue = BigInt(value);
        const bLength = BigInt(length);
        const mask = (1n << bLength) - 1n;
        const cleanValue = bValue & mask;
        result |= (cleanValue << currentShift);
        currentShift += bLength;
    }
    return result;
}