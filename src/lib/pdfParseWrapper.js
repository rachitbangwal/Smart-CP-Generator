const fs = require('fs');
const path = require('path');

// Override the default pdf-parse behavior that tries to load test files
const originalReadFileSync = fs.readFileSync;
fs.readFileSync = function (filePath, options) {
    if (filePath.includes('pdf-parse/test/data')) {
        // Return an empty buffer for test files
        return Buffer.from('');
    }
    return originalReadFileSync(filePath, options);
};

module.exports = require('pdf-parse');
