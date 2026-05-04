#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
Automated monthly hwdata update script.

This script automates the monthly update workflow:
1. Creates a feature branch (e.g., apr-update)
2. Downloads latest ID files
3. Updates hwdata.spec
4. Creates commits
5. Pushes and creates a PR

Usage:
  ./monthly-update.py              # Full automation
  ./monthly-update.py --local-only # Test locally without push/PR
"""

import argparse
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


class Colors:  # pylint: disable=too-few-public-methods
    """Terminal colors for output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def log(message, color=None):
    """Print colored log message."""
    if color:
        print(f"{color}{message}{Colors.ENDC}")
    else:
        print(message)


def run_command(cmd, check=True, capture=True):
    """Run shell command and return output.

    Note: Uses shell=True for convenience with git/make commands.
    All command strings are constructed internally, not from user input.
    """
    log(f"Running: {cmd}", Colors.OKCYAN)
    result = subprocess.run(
        cmd,
        shell=True,  # Safe here: all commands are hardcoded, no user input
        capture_output=capture,
        text=True,
        check=False
    )
    if check and result.returncode != 0:
        log(f"Command failed with exit code {result.returncode}", Colors.FAIL)
        if result.stderr:
            log(f"Error: {result.stderr}", Colors.FAIL)
        sys.exit(1)
    return result


def get_current_branch():
    """Get current git branch name."""
    result = run_command("git rev-parse --abbrev-ref HEAD")
    return result.stdout.strip()


def get_month_name():
    """Get current month name in lowercase (e.g., 'apr')."""
    return datetime.now().strftime("%b").lower()


def check_clean_working_tree():
    """Ensure working tree is clean."""
    result = run_command("git status --porcelain")
    if result.stdout.strip():
        log("Error: Working tree is not clean. Commit or stash changes first.", Colors.FAIL)
        sys.exit(1)


def create_update_branch(month):
    """Create and checkout monthly update branch."""
    branch_name = f"{month}-update"
    log(f"\n📝 Creating branch: {branch_name}", Colors.HEADER)

    # Check if branch already exists
    result = run_command(f"git rev-parse --verify {branch_name}", check=False)
    if result.returncode == 0:
        log(f"Branch {branch_name} already exists. Checking it out.", Colors.WARNING)
        run_command(f"git checkout {branch_name}")
    else:
        run_command(f"git checkout -b {branch_name}")

    return branch_name


def download_files():
    """Download latest ID files."""
    log("\n⬇️  Downloading latest ID files...", Colors.HEADER)

    # Check if pnp.ids.csv exists
    if not Path("pnp.ids.csv").exists():
        log("⚠️  pnp.ids.csv not found!", Colors.WARNING)
        log("Please manually download from https://uefi.org/uefi-pnp-export", Colors.WARNING)
        log("and save as pnp.ids.csv, then run this script again.", Colors.WARNING)
        sys.exit(1)

    # Run configure
    run_command("./configure")

    # Run make download
    result = run_command("make download", check=False)
    if result.returncode != 0:
        log("Warning: make download had issues, but continuing...", Colors.WARNING)

    log("✅ Download complete", Colors.OKGREEN)


def validate_files():
    """Run make check to validate files."""
    log("\n✅ Validating ID files...", Colors.HEADER)
    result = run_command("make check", check=False, capture=False)
    if result.returncode != 0:
        log("Validation failed! Fix errors before continuing.", Colors.FAIL)
        sys.exit(1)
    log("✅ Validation passed", Colors.OKGREEN)


def get_file_dates():
    """Extract dates from pci.ids and usb.ids headers."""
    dates = {}

    # PCI date
    result = run_command("grep 'Date:' pci.ids | head -n1 | cut -d' ' -f5")
    dates['pci'] = result.stdout.strip() if result.stdout else 'unknown'

    # USB date
    result = run_command("grep 'Date:' usb.ids | head -n1 | cut -d' ' -f6")
    dates['usb'] = result.stdout.strip() if result.stdout else 'unknown'

    return dates


def get_pci_stats():
    """Get PCI changes statistics using compare-pci-ids.py."""
    # Save current pci.ids as old
    if not Path("pci.ids.old").exists():
        result = run_command("git show HEAD:pci.ids > pci.ids.old", check=False)
        if result.returncode != 0:
            return None

    result = run_command("./compare-pci-ids.py pci.ids.old pci.ids 2>/dev/null", check=False)
    if result.returncode == 0:
        return result.stdout
    return None


def detect_changes():
    """Detect which files changed for commit message."""
    changes = []

    result = run_command("git diff --name-only pci.ids", check=False)
    if result.stdout.strip():
        changes.append("pci")

    result = run_command("git diff --name-only usb.ids", check=False)
    if result.stdout.strip():
        changes.append("usb")

    result = run_command("git diff --name-only oui.txt iab.txt pnp.ids", check=False)
    if result.stdout.strip():
        changes.append("vendor ids")

    return changes


def get_current_version():
    """Get current version from hwdata.spec."""
    result = run_command("awk '/Version:/ { print $2 }' hwdata.spec")
    return result.stdout.strip()


def bump_version(current_version):
    """Bump minor version number."""
    parts = current_version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    return '.'.join(parts)


def update_spec_file(new_version, changes):
    """Update hwdata.spec with new version and changelog."""
    log(f"\n📝 Updating hwdata.spec to version {new_version}...", Colors.HEADER)

    # Read spec file
    with open('hwdata.spec', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Update version
    for i, line in enumerate(lines):
        if line.startswith('Version:'):
            lines[i] = f'Version: {new_version}\n'
            break

    # Create changelog entry
    today = datetime.now().strftime("%a %b %d %Y")

    # Get git user info
    result = run_command("git config user.name")
    user_name = result.stdout.strip()
    result = run_command("git config user.email")
    user_email = result.stdout.strip()

    # Determine changelog message
    if changes:
        change_list = ", ".join(changes)
        changelog_msg = f"Update {change_list}"
    else:
        changelog_msg = "Update hardware IDs"

    # Find %changelog section
    changelog_index = None
    for i, line in enumerate(lines):
        if line.startswith('%changelog'):
            changelog_index = i
            break

    if changelog_index is not None:
        # Insert new entry after %changelog line
        new_entry = f"* {today} {user_name} <{user_email}> - {new_version}-1\n- {changelog_msg}\n\n"
        lines.insert(changelog_index + 1, new_entry)

    # Write back
    with open('hwdata.spec', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    log(f"✅ Updated to version {new_version}", Colors.OKGREEN)


def create_commit(changes):
    """Create git commit with appropriate message."""
    log("\n💾 Creating commit...", Colors.HEADER)

    # Stage files
    files_to_add = ["hwdata.spec"]
    if "pci" in changes:
        files_to_add.append("pci.ids")
    if "usb" in changes:
        files_to_add.append("usb.ids")
    if "vendor ids" in changes:
        files_to_add.extend(["oui.txt", "iab.txt", "pnp.ids"])

    # Create commit message
    if changes:
        change_list = " and ".join(changes)
        commit_msg = f"Update {change_list}"
    else:
        commit_msg = "Update hardware IDs"

    run_command(f"git add {' '.join(files_to_add)}")
    run_command(f"git commit -s -m '{commit_msg}'")
    log(f"✅ Committed: {commit_msg.split(chr(10), maxsplit=1)[0]}", Colors.OKGREEN)


def create_pr(branch_name, new_version, dates, pci_stats, local_only=False):
    """Push branch and create pull request."""
    if local_only:
        log("\n⏭️  Skipping push and PR creation (local-only mode)", Colors.WARNING)
        return

    log(f"\n🚀 Pushing branch {branch_name}...", Colors.HEADER)
    run_command(f"git push -u origin {branch_name}")

    # Create PR description
    pr_title = f"Monthly update - {datetime.now().strftime('%B %Y')}"

    pr_body = f"""Automated monthly update of hardware IDs to version {new_version}

## Updated Files
- PCI IDs: {dates.get('pci', 'N/A')}
- USB IDs: {dates.get('usb', 'N/A')}
- Vendor IDs (OUI/IAB/PNP): Updated

"""

    if pci_stats:
        pr_body += f"## PCI Changes\n```\n{pci_stats}```\n\n"

    pr_body += """## Testing
- [ ] `make check` passes
- [ ] Packit builds successful
- [ ] Tests pass on all targets

🤖 Generated by monthly-update.py automation
"""

    # Create PR using gh CLI
    log("\n📬 Creating pull request...", Colors.HEADER)

    # Write PR body to temp file (safer than escaping)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(pr_body)
        body_file = f.name

    try:
        cmd = f'gh pr create --title "{pr_title}" --body-file "{body_file}"'
        result = run_command(cmd, check=False)
    finally:
        # Clean up temp file
        Path(body_file).unlink(missing_ok=True)

    if result.returncode != 0:
        log("Failed to create PR automatically. Create it manually on GitHub:", Colors.WARNING)
        log(f"  Title: {pr_title}", Colors.WARNING)
        log(f"  Body: {pr_body}", Colors.WARNING)
    else:
        log("✅ Pull request created!", Colors.OKGREEN)
        if result.stdout:
            log(result.stdout.strip())


def cleanup():
    """Cleanup temporary files."""
    if Path("pci.ids.old").exists():
        Path("pci.ids.old").unlink()


def main():  # pylint: disable=too-many-statements
    """Main execution flow."""
    parser = argparse.ArgumentParser(description="Automate monthly hwdata updates")
    parser.add_argument("--local-only", action="store_true",
                       help="Execute locally without pushing or creating PR (test mode)")
    args = parser.parse_args()

    local_only = args.local_only
    if local_only:
        log("🔧 LOCAL-ONLY MODE - Will make local changes but not push or create PR\n",
            Colors.WARNING)

    log("🤖 Starting monthly hwdata update automation...", Colors.HEADER)

    # Step 1: Check prerequisites
    if not Path("hwdata.spec").exists():
        log("Error: Not in hwdata repository root", Colors.FAIL)
        sys.exit(1)

    # Check for gh CLI (only needed if not local-only)
    if not local_only:
        result = run_command("which gh", check=False)
        if result.returncode != 0:
            log("Error: 'gh' CLI not found. Install it from https://cli.github.com/", Colors.FAIL)
            sys.exit(1)

    # Step 2: Check clean working tree
    original_branch = get_current_branch()
    if original_branch != "master":
        log(f"Warning: Not on master branch (currently on {original_branch})", Colors.WARNING)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)

    check_clean_working_tree()

    # Step 3: Create branch
    month = get_month_name()
    branch_name = create_update_branch(month)

    try:
        # Step 4: Download files
        download_files()

        # Step 5: Validate
        validate_files()

        # Step 6: Get statistics
        dates = get_file_dates()
        pci_stats = get_pci_stats()

        # Step 7: Detect changes
        changes = detect_changes()

        if not changes:
            log("\n⚠️  No changes detected in ID files!", Colors.WARNING)
            log("This might mean:", Colors.WARNING)
            log("  - Files are already up to date", Colors.WARNING)
            log("  - Download failed silently", Colors.WARNING)
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                cleanup()
                sys.exit(0)

        # Step 8: Update spec file
        current_version = get_current_version()
        new_version = bump_version(current_version)
        update_spec_file(new_version, changes)

        # Step 9: Create commit
        create_commit(changes)

        # Step 10: Create PR (or skip if local-only)
        create_pr(branch_name, new_version, dates, pci_stats, local_only=local_only)

        # Cleanup
        cleanup()

        if local_only:
            log("\n✨ LOCAL CHANGES COMPLETE!", Colors.OKGREEN)
            log(f"\nYou are now on branch: {branch_name}", Colors.OKGREEN)
            log("Changes have been committed locally.", Colors.OKGREEN)
            log("\nTo reset and undo all changes:", Colors.WARNING)
            log(f"  git checkout {original_branch}", Colors.WARNING)
            log(f"  git branch -D {branch_name}", Colors.WARNING)
            log("\nTo push and create PR manually:", Colors.OKCYAN)
            log(f"  git push -u origin {branch_name}", Colors.OKCYAN)
            log("  gh pr create", Colors.OKCYAN)
        else:
            log("\n✨ All done! Review the PR and merge when ready.", Colors.OKGREEN)
            log(f"Branch: {branch_name}", Colors.OKGREEN)

    except KeyboardInterrupt:
        log("\n\n⚠️  Interrupted by user", Colors.WARNING)
        cleanup()
        sys.exit(1)
    except Exception as e:
        log(f"\n❌ Error: {e}", Colors.FAIL)
        cleanup()
        raise


if __name__ == "__main__":
    main()
