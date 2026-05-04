# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

hwdata is a hardware identification database that aggregates and maintains various hardware and vendor information files:
- **pci.ids** - PCI vendor and device IDs
- **usb.ids** - USB vendor and device IDs  
- **oui.txt** - IEEE MAC address assignments (24-bit)
- **iab.txt** - IEEE MAC address assignments (36-bit)
- **pnp.ids** - UEFI PnP vendor IDs

The project is packaged as an RPM and installed to /usr/share/hwdata/ on Fedora/RHEL systems.

## Build System

The project uses a custom configure script (not autotools) that generates `Makefile.inc` with installation paths. The main Makefile handles building, testing, and packaging.

### Essential Commands

```bash
# Initial setup (generates Makefile.inc)
./configure [--prefix=/usr] [--disable-blacklist]

# Download latest upstream ID files
make download

# Validate all ID files (runs multiple checks)
make check

# Install to system
make install

# Create release tarball
make create-archive

# Build SRPM
make srpm-x
```

## ID File Formats

### pci.ids
Hierarchical format with strict sorting requirements:
- Vendor line: `VVVV<space(s)>Vendor Name`
- Device line: `<tab>DDDD<space(s)>Device Name`
- IDs are 4-digit hex, must be in ascending order
- Subsystem lines: `<tab><tab>SSSS SSSS<space(s)>Subsystem Name`

### usb.ids  
Similar hierarchical format to pci.ids with vendor/device structure.

### pnp.ids
Simple two-column format:
- `XXX<tab>Company Name`
- XXX is a 3-character alphanumeric PnP ID
- Sorted case-insensitively

### oui.txt / iab.txt
IEEE MAC address vendor assignments, downloaded directly from standards-oui.ieee.org.

## Scripts

### Automation

**monthly-update.py**  
Automates the entire monthly update workflow: creates branch, downloads files, updates spec, commits, and creates PR. See "Automated Monthly Updates" section for details.

### Validation

**check-pci-ids.py**  
Validates that pci.ids maintains correct sorting order for vendor and device IDs. Fails if any ID is less than or equal to the previous ID.

**check-usb-ids.sh**  
Runs lsusb and python-hwdata tests inside a container to validate usb.ids. Skips if NO_DOCKER=1.

**compare-pci-ids.py**  
Compares two pci.ids files and reports statistics on vendors/devices added, removed, or renamed. Usage: `./compare-pci-ids.py old.pci.ids new.pci.ids`

### Processing

**process-pnp-ids.py**  
Converts UEFI PnP ID CSV export to the pnp.ids format.

## Update Workflow

When updating ID files from upstream sources:

1. Run `make download` to fetch latest versions
2. Files are downloaded with `.downloaded` suffix
3. Files are converted to UTF-8 (`.utf8` suffix)
4. Line endings are normalized with dos2unix (`.converted` suffix)
5. Patches are applied (for usb.ids and pnp.ids)
6. Run `make check` to validate all files
7. Check dates in pci.ids and usb.ids headers
8. Commit changes and update hwdata.spec changelog

The Makefile automatically handles encoding detection and conversion from iso-8859 or cp12xx to UTF-8.

### Known Issue: pnp.ids.csv Download

The UEFI PnP export URL (https://uefi.org/uefi-pnp-export) is protected by Cloudflare bot detection and often fails with automated downloads. 

**Workaround:**
1. Manually visit https://uefi.org/uefi-pnp-export in a browser
2. Download the CSV file
3. Save it as `pnp.ids.csv` in the project directory
4. Run `make download` - it will skip the download and use your file
5. Continue with normal workflow

The Makefile checks for an existing `pnp.ids.csv` file before attempting download. The file is preserved by `make clean` to avoid requiring repeated manual downloads.

## Testing

Tests are located in `tests/` directory and use the beakerlib framework:

- `tests/syntax/` - Validates installed files with lspci/lsusb
- `tests/ids-files/` - File presence and format checks
- `tests/python-hwdata/` - Tests python-hwdata binding

Tests are run via Packit CI on pull requests against all Fedora releases.

## Automated Monthly Updates

The `monthly-update.py` script automates the monthly update workflow. It:
1. Creates the feature branch (e.g., `apr-update`)
2. Downloads and validates ID files
3. Updates hwdata.spec version and changelog
4. Creates commits with proper messages
5. Pushes and creates a GitHub PR

**Prerequisites:**
- Clean working tree on master branch
- `gh` CLI installed and authenticated
- `pnp.ids.csv` manually downloaded (see Known Issue below)

**Usage:**
```bash
# Make sure pnp.ids.csv is up to date (manual download)
# Then run:
./monthly-update.py

# Or test locally without pushing/creating PR:
./monthly-update.py --local-only
# To undo: git checkout master && git branch -D <month>-update
```

The script automatically:
- Detects which files changed for commit messages
- Generates PCI statistics using compare-pci-ids.py
- Creates PR description with file dates and statistics
- Handles errors gracefully with clear messages

After the script completes, review the PR, wait for CI/Sourcery, and merge when ready.

## Manual Release Process

If you need to do updates manually, follow this workflow:

1. **Create feature branch** with month name: `jan-update`, `feb-update`, `mar-update`, etc.
2. **Set up and download**:
   ```bash
   ./configure
   make download
   make check
   ```
3. **Update hwdata.spec**:
   - Bump Version field
   - Add %changelog entry with current date and description
4. **Commit and push** changes to GitHub
   - Commit message should reflect what changed: "Update pci and vendor ids", "Update pci, usb and vendor ids", "Update vendor ids", etc.
   - Components: `pci` (pci.ids), `usb` (usb.ids), `vendor ids` (oui.txt, iab.txt, pnp.ids)
5. **Automated CI** runs on GitHub:
   - Packit builds the package for all Fedora releases
   - Tests execute automatically
   - Sourcery AI reviews the changes
6. **Wait period** (typically ~1 day) to allow users to review and provide feedback
7. **Merge PR** via GitHub UI
8. **Create and push tag**:
   ```bash
   make tag      # Creates signed tag v{VERSION}
   git push origin v{VERSION}
   ```
9. **Create GitHub release** via GitHub UI

Tag format depends on branch:
- rhel branches: `v{VERSION}-{RELEASE}`  
- Other branches: `v{VERSION}`

**Note**: The Makefile targets `make create-archive` and `make srpm-x` exist for local testing but are not used in the standard release process. GitHub/Packit handles package building.

## File Encoding Requirements

All ID files MUST be valid UTF-8. The `make check` target validates this with iconv. Files downloaded from upstream may be in various encodings (iso-8859, cp1252) and are automatically converted during the download process.

## Further Automation Opportunities

The `monthly-update.py` script handles the core update workflow. Additional automation could include:

### GitHub Actions Integration

Create `.github/workflows/` for:
- **auto-tag-release.yml** - On PR merge to master, automatically create tag and GitHub release:
  ```yaml
  on:
    pull_request:
      types: [closed]
      branches: [master]
  jobs:
    tag-release:
      if: github.event.pull_request.merged == true
      steps:
        - name: Create tag
          run: make tag && git push origin --tags
        - name: Create GitHub release
          run: gh release create $TAG_NAME --generate-notes
  ```

- **monthly-reminder.yml** - Scheduled workflow to remind maintainer on 1st of month:
  ```yaml
  on:
    schedule:
      - cron: '0 9 1 * *'  # 9 AM on 1st of each month
  jobs:
    remind:
      steps:
        - name: Create reminder issue
          run: |
            gh issue create --title "Monthly update due" \
              --body "Run ./monthly-update.py to create update PR"
  ```

- **pnp-check.yml** - Check if pnp.ids.csv needs updating (compare local date vs UEFI site)

### Auto-Merge Strategy

For fully automated updates (use with caution):
1. PR created by `monthly-update.py`
2. Wait for CI green + 24 hours
3. If no negative comments, auto-merge via GitHub Actions
4. Auto-create tag and release

**Risks:**
- Upstream file corruption (mitigated by `make check`)
- Breaking changes (mitigated by 24-hour wait + community review)
- Silent test failures (monitor CI logs carefully)

Recommended: Keep manual merge approval as final safety gate.
