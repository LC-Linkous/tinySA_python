# Security Policy

## Supported versions

This is an unofficial, community-maintained project under active development.
Security-relevant fixes are applied to the latest release on the `main` branch
only. There is no back-porting to older versions.

| Version | Supported          |
| ------- | ------------------ |
| latest (`main` / newest release) | :white_check_mark: |
| older releases | :x: |

## Reporting a vulnerability

Please **do not open a public issue** for security-sensitive reports.

Use GitHub's private vulnerability reporting:
**Security -> Report a vulnerability** on the repository. This opens a private
advisory visible only to the maintainers.

When reporting, please include:

- A description of the issue and its impact
- Steps to reproduce (OS, Python version, tinySA model and firmware version)
- Any relevant logs or a minimal proof of concept

You can expect an initial acknowledgment within a reasonable window. Once a fix
is available, we will coordinate disclosure and credit the reporter unless
anonymity is requested.

## Scope

In-scope examples:

- Unsafe construction or handling of serial commands sent to the device
- Path handling issues in file read/write helpers (captures, screenshots,
  exported data)
- Unsafe handling of device responses that could affect the host

Out of scope:

- Vulnerabilities in tinySA firmware or official tinySA software — report
  those upstream through the official tinySA channels
- **Hardware damage from misuse.** This library drives real hardware over
  serial; operating outside the device's documented limits is a user
  responsibility, not a software vulnerability. The library's guardrails are
  best-effort, not guarantees.
