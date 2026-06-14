/**
 * Health check test for chrome-bridge — no Chrome installation required.
 * Spawns the bridge server, waits for it to listen, hits /health, then asserts.
 */

const { spawn } = require('child_process');
const http = require('http');

const PORT = 8081;
const TIMEOUT_MS = 10_000;

function waitForPort(port, timeoutMs) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;
    function attempt() {
      const req = http.get({ host: '127.0.0.1', port, path: '/health' }, (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
      });
      req.on('error', () => {
        if (Date.now() > deadline) {
          reject(new Error(`Server did not start on port ${port} within ${timeoutMs}ms`));
        } else {
          setTimeout(attempt, 250);
        }
      });
      req.setTimeout(1000, () => req.destroy());
    }
    attempt();
  });
}

async function run() {
  const server = spawn(process.execPath, ['server.js'], {
    env: { ...process.env, SKIP_CHROME: '1' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  let failed = false;

  try {
    const { statusCode, body } = await waitForPort(PORT, TIMEOUT_MS);

    if (statusCode !== 200) {
      throw new Error(`/health returned HTTP ${statusCode}`);
    }

    const json = JSON.parse(body);
    if (!Object.prototype.hasOwnProperty.call(json, 'status')) {
      throw new Error(`/health response missing 'status' field: ${body}`);
    }
    if (!Object.prototype.hasOwnProperty.call(json, 'nano_status')) {
      throw new Error(`/health response missing 'nano_status' field: ${body}`);
    }

    console.log(`PASS /health responded: ${body}`);
  } catch (err) {
    console.error(`FAIL ${err.message}`);
    failed = true;
  } finally {
    server.kill('SIGTERM');
  }

  process.exit(failed ? 1 : 0);
}

run();
