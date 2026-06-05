#!/usr/bin/env node
/**
 * Vercel CLI Deployment Script (Cross-Platform)
 * Usage: node deploy.cjs [project-path] [options]
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const isWindows = os.platform() === 'win32';
const ALLOWED_COMMANDS = new Set(['vercel', 'npm', 'pnpm', 'yarn']);
function log(msg) { console.error(msg); }
function commandExists(cmd) {
  if (!ALLOWED_COMMANDS.has(cmd)) throw new Error(`Command not in whitelist: ${cmd}`);
  try {
    if (isWindows) { return spawnSync('where', [cmd], { stdio: 'ignore' }).status === 0; }
    else { return spawnSync('sh', ['-c', `command -v "$1"`, '--', cmd], { stdio: 'ignore' }).status === 0; }
  } catch { return false; }
}
function getCommandOutput(cmd, args) {
  try {
    const result = spawnSync(cmd, args, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'], shell: isWindows });
    return result.status === 0 ? (result.stdout || '').trim() : null;
  } catch { return null; }
}
function parseArgs(args) {
  const result = { projectPath: '.', prod: true, yes: false, skipBuild: false };
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--prod') result.prod = true;
    else if (arg === '--yes' || arg === '-y') result.yes = true;
    else if (arg === '--skip-build') result.skipBuild = true;
    else if (!arg.startsWith('-')) result.projectPath = arg;
    else { log(`Unknown option: ${arg}`); process.exit(1); }
  }
  return result;
}
function checkVercelInstalled() {
  // Check local npx first
  const npxResult = spawnSync('npx', ['vercel', '--version'], { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'], shell: isWindows });
  if (npxResult.status === 0) {
    const version = (npxResult.stdout || '').trim();
    log(`Vercel CLI version: ${version}`);
    return 'npx';
  }
  if (commandExists('vercel')) {
    const version = getCommandOutput('vercel', ['--version']) || 'unknown';
    log(`Vercel CLI version: ${version}`);
    return 'vercel';
  }
  log('Error: Vercel CLI is not installed');
  process.exit(1);
}
function checkLoginStatus(vercelCmd) {
  log('Checking login status...');
  try {
    const args = vercelCmd === 'npx' ? ['vercel', 'whoami'] : ['whoami'];
    const cmd = vercelCmd === 'npx' ? 'npx' : 'vercel';
    const result = spawnSync(cmd, args, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], shell: isWindows });
    const output = (result.stdout || '').trim();
    if (result.status === 0 && output && !output.includes('Error') && !output.includes('not logged in')) {
      const match = output.match(/Logged in as\s+(.+)/i);
      log(`Logged in as: ${match ? match[1] : output}`);
      return true;
    }
  } catch {}
  return false;
}
function checkProject(projectPath) {
  const absPath = path.resolve(projectPath);
  if (!fs.existsSync(absPath) || !fs.statSync(absPath).isDirectory()) {
    log(`Error: Project directory does not exist: ${absPath}`);
    process.exit(1);
  }
  log(`Project path: ${absPath}`);
  return absPath;
}
function runBuildIfNeeded(projectPath) {
  const packageJsonPath = path.join(projectPath, 'package.json');
  if (!fs.existsSync(packageJsonPath)) { log('No package.json found, skipping build step'); return true; }
  let packageJson;
  try { packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8')); } catch (error) { return true; }
  if (!packageJson.scripts || !packageJson.scripts.build) { log('No build script found, skipping'); return true; }
  log('Running pre-deployment build...');
  const result = spawnSync('npm', ['run', 'build'], { cwd: projectPath, stdio: 'inherit', shell: isWindows });
  if (result.status !== 0) { log('Build FAILED!'); process.exit(1); }
  log('Build completed successfully!');
  return true;
}
function doDeploy(projectPath, options, vercelCmd) {
  log('');
  log('Starting deployment...');
  log('');
  const args = vercelCmd === 'npx' ? ['vercel'] : [];
  if (options.yes) args.push('--yes');
  if (options.prod) { args.push('--prod'); log('Deployment environment: Production'); }
  log(`Executing: ${vercelCmd} ${args.join(' ')}`);
  log('');
  log('========================================');
  try {
    const result = spawnSync(vercelCmd, args, {
      cwd: projectPath,
      encoding: 'utf8',
      stdio: ['inherit', 'pipe', 'pipe'],
      timeout: 300000,
      shell: isWindows
    });
    const output = (result.stdout || '') + (result.stderr || '');
    log(output);
    if (result.status !== 0) throw new Error('Deployment command failed');
    const aliasedMatch = output.match(/Aliased:\s*(https:\/\/[a-zA-Z0-9.-]+\.vercel\.app)/i);
    const productionUrl = aliasedMatch ? aliasedMatch[1] : null;
    const deploymentMatch = output.match(/Production:\s*(https:\/\/[a-zA-Z0-9.-]+\.vercel\.app)/i);
    const deploymentUrl = deploymentMatch ? deploymentMatch[1] : null;
    const finalUrl = productionUrl || deploymentUrl;
    log('');
    log('========================================');
    log('Deployment successful!');
    log('========================================');
    if (finalUrl) {
      log(`Your site is live! Visit: ${finalUrl}`);
      console.log(JSON.stringify({ status: 'success', url: finalUrl }));
    } else {
      console.log(JSON.stringify({ status: 'success', message: 'Deployment successful' }));
    }
  } catch (error) {
    log(error.message || '');
    log('Deployment failed');
    process.exit(1);
  }
}
function main() {
  log('========================================');
  log('Vercel CLI Project Deployment');
  log('========================================');
  log('');
  const args = process.argv.slice(2);
  const options = parseArgs(args);
  const vercelCmd = checkVercelInstalled();
  log('');
  if (!checkLoginStatus(vercelCmd)) { log('Error: Not logged in'); process.exit(1); }
  log('');
  const projectPath = checkProject(options.projectPath);
  if (!options.skipBuild) runBuildIfNeeded(projectPath);
  doDeploy(projectPath, options, vercelCmd);
}
main();
