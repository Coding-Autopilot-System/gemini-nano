/**
 * Chrome Gemini Nano HTTP Bridge
 * Exposes Chrome's window.ai Prompt API as a local HTTP endpoint.
 *
 * Prerequisites:
 *   1. Enable the flag in Chrome:  chrome://flags/#prompt-api-for-gemini-nano  → Enabled
 *   2. Download the model:         chrome://components/ → "Optimization Guide On Device Model" → Update
 *   3. Restart Chrome, then start this server.
 *
 * Chrome Dev/Canary preferred (flag available by default); stable works after manual flag toggle.
 *
 * Usage:
 *   npm install
 *   node server.js          # start bridge
 *   node server.js --probe  # check availability and exit
 */

const express = require('express');
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const PORT = 8081;
const PROBE_MODE = process.argv.includes('--probe');

// Chrome paths: Dev/Canary preferred; stable as fallback
const CHROME_PATHS = [
  `${process.env.LOCALAPPDATA}\\Google\\Chrome Dev\\Application\\chrome.exe`,
  `${process.env.LOCALAPPDATA}\\Google\\Chrome SxS\\Application\\chrome.exe`,
  'C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`,
];

// Flags that enable window.ai in Chrome Dev/Canary and stable (Chrome 127+)
const CHROME_FLAGS = [
  '--enable-features=OptimizationGuideOnDeviceModel,PromptAPIForGeminiNano',
  '--optimization-guide-on-device-model-disabled=false',
  '--disable-features=MediaRouter',
];

// Use real Chrome profile so flags set in chrome://flags persist
const USER_DATA_DIR = path.join(
  process.env.LOCALAPPDATA || '',
  'Google', 'Chrome', 'User Data'
);

let browser = null;
let page = null;
let nanoStatus = 'not-initialized';

function findChrome() {
  return CHROME_PATHS.find(p => { try { fs.accessSync(p); return true; } catch { return false; } });
}

async function launchBrowser() {
  const executablePath = findChrome();
  if (!executablePath) {
    throw new Error(
      'Chrome not found. Install Chrome stable (v127+), Dev, or Canary.\n' +
      '  Dev:    https://www.google.com/chrome/dev/\n' +
      '  Stable: https://www.google.com/chrome/'
    );
  }

  console.log(`Chrome: ${executablePath}`);

  const launchArgs = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    ...CHROME_FLAGS,
  ];

  browser = await puppeteer.launch({ executablePath, headless: 'new', args: launchArgs });
  page = await browser.newPage();
  await page.goto('about:blank');

  const caps = await page.evaluate(async () => {
    if (!window.ai || !window.ai.languageModel) return { available: 'unavailable', reason: 'window.ai not present' };
    try {
      const c = await window.ai.languageModel.capabilities();
      return { available: c.available };
    } catch (e) {
      return { available: 'error', reason: e.message };
    }
  });

  nanoStatus = caps.available;

  if (nanoStatus === 'readily') {
    console.log('Gemini Nano: ready');
  } else if (nanoStatus === 'after-download') {
    console.warn('Gemini Nano: model downloading — wait a few minutes, then restart this server');
    console.warn('  Visit chrome://components/ → "Optimization Guide On Device Model" → Update');
  } else {
    console.warn(`Gemini Nano: ${nanoStatus}${caps.reason ? ' — ' + caps.reason : ''}`);
    console.warn('  Step 1: chrome://flags/#prompt-api-for-gemini-nano  → Enable → Relaunch Chrome');
    console.warn('  Step 2: chrome://components/ → "Optimization Guide On Device Model" → Update');
    console.warn('  Step 3: Restart this server');
  }

  return nanoStatus;
}

if (PROBE_MODE) {
  (async () => {
    const chrome = findChrome();
    console.log(chrome ? `Chrome found: ${chrome}` : 'Chrome: NOT FOUND');
    if (!chrome) process.exit(1);
    try {
      const status = await launchBrowser();
      console.log(`window.ai status: ${status}`);
      await browser.close();
      process.exit(status === 'readily' ? 0 : 2);
    } catch (e) {
      console.error(e.message);
      process.exit(1);
    }
  })();
} else {
  const app = express();
  app.use(express.json());
  app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    next();
  });

  app.get('/health', (_req, res) => {
    res.json({ status: nanoStatus === 'readily' ? 'ok' : 'degraded', nano_status: nanoStatus, model: 'gemini-nano', engine: 'window.ai' });
  });

  app.get('/v1/models', (_req, res) => {
    res.json({
      object: 'list',
      data: [{ id: 'gemini-nano', object: 'model', owned_by: 'chrome', description: "Chrome's built-in Gemini Nano (window.ai)" }],
    });
  });

  app.post('/v1/chat/completions', async (req, res) => {
    if (!page) return res.status(503).json({ error: 'Chrome not initialized' });
    if (nanoStatus !== 'readily') {
      return res.status(503).json({
        error: 'Gemini Nano not available',
        nano_status: nanoStatus,
        hint: nanoStatus === 'after-download'
          ? 'Model still downloading — check chrome://components/'
          : 'Enable chrome://flags/#prompt-api-for-gemini-nano, then restart this server',
      });
    }

    const messages = req.body.messages || [];
    const prompt = messages.map(m => `${m.role}: ${m.content}`).join('\n') + '\nassistant:';

    try {
      const result = await page.evaluate(async (promptText) => {
        const session = await window.ai.languageModel.create();
        const response = await session.prompt(promptText);
        session.destroy();
        return response;
      }, prompt);

      res.json({
        id: `chatcmpl-nano-${Date.now()}`,
        object: 'chat.completion',
        model: 'gemini-nano',
        choices: [{ index: 0, message: { role: 'assistant', content: result }, finish_reason: 'stop' }],
      });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  (async () => {
    if (!process.env.SKIP_CHROME) {
      try {
        await launchBrowser();
      } catch (err) {
        console.error('Chrome launch failed:', err.message);
        console.error('Server starting anyway — /v1/chat/completions will return 503 until Chrome is ready.');
      }
    }
    app.listen(PORT, () => {
      console.log(`Chrome Gemini Nano bridge → http://localhost:${PORT}`);
    });
  })();
}
