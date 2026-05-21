# Swiss Ephemeris Data Files

This directory contains Swiss Ephemeris data files (`.se1` format) for high-precision planetary calculations.

## Files Downloaded

The following files have been downloaded from: https://www.astro.com/ftp/swisseph/ephe/

- `seplm06.se1` - Moon ephemeris (600 BC - 600 AD)
- `seplm12.se1` - Moon ephemeris (600 - 1200)
- `seplm18.se1` - Moon ephemeris (1200 - 1800)
- `seplm24.se1` - Moon ephemeris (1800 - 2400)
- `seplm30.se1` - Moon ephemeris (2400 - 3000)
- `seplm36.se1` - Moon ephemeris (3000 - 3600)
- `seplm42.se1` - Moon ephemeris (3600 - 4200)
- `seplm48.se1` - Moon ephemeris (4200 - 4800)
- `seplm54.se1` - Moon ephemeris (4800 - 5400)
- `sepl_06.se1` - Planets ephemeris (-3000 to 3000)
- `sepl_12.se1` - Planets ephemeris
- `sepl_18.se1` - Planets ephemeris

## Coverage

These files provide coverage for dates from approximately **3000 BC to 5400 AD**, which includes:
- ✅ Kali Yuga epoch (3101 BC)
- ✅ Historical dates
- ✅ Modern dates
- ✅ Future dates

## Date Range Limitations

### Moshier Ephemeris (built-in)
- Range: ~625 BC to 2999 AD (JD 625000.50 to 2818000.50)
- ❌ Does NOT cover 3101 BC

### Swiss Ephemeris Files (these files)
- Range: ~3000 BC to 5400 AD (with these files)
- ✅ COVERS 3101 BC
- Higher precision than Moshier

## File Size

Total size: ~96 KB (12 files × 2.6 KB each)

These are highly compressed binary files containing planetary positions.

## Licensing

**IMPORTANT**: These files are part of Swiss Ephemeris, which is dual-licensed:

1. **GPL v2+** (free for open source projects)
2. **Commercial License** (required for proprietary software)

See `LICENSING_IMPORTANT.md` in the parent directory for details.

## Usage

The code automatically looks for this directory and uses these files:

```python
# In console_drik_debug.py:
eph_path = os.path.join(script_dir, 'eph_data')
swe.set_ephe_path(eph_path)
```

## Downloading More Files

If you need extended date ranges, download additional files from:
https://www.astro.com/ftp/swisseph/ephe/

Example:
```bash
cd eph_data
curl -O https://www.astro.com/ftp/swisseph/ephe/sepl_00.se1  # For older dates
curl -O https://www.astro.com/ftp/swisseph/ephe/seplm60.se1  # For future dates
```

## File Naming Convention

- `seplm*.se1` - Moon ephemeris files (m = moon)
- `sepl_*.se1` - Planet ephemeris files
- Numbers indicate century ranges

## Do Not Commit to Git

These files are binary and not necessary for version control. The `.gitignore` file excludes them.

To set up on a new system:
1. Create `eph_data` directory
2. Download files using the curl commands above
3. Or run the provided download script (if available)

## Verification

Check that files are being used:

```bash
python3 console_drik_debug.py -3100 1 23
```

Should show planetary positions without "outside range" errors.
