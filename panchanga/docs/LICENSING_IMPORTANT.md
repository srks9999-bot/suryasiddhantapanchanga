# ⚠️ LICENSING - READ BEFORE PRODUCTION USE

## Critical Information About Swiss Ephemeris Licensing

### TL;DR

**Using Moshier ephemeris does NOT exempt you from Swiss Ephemeris licensing.**

Even though Moshier calculations don't require external data files, you're still using the Swiss Ephemeris library (pyswisseph), which is dual-licensed.

## Swiss Ephemeris License Summary

| Your App Type | License Required | Cost | Action Needed |
|---------------|------------------|------|---------------|
| **Open Source (GPL)** | GPL v2+ | **FREE** | ✅ Make your app open source |
| **Proprietary/Commercial** | Commercial License | **€250-500** | ⚠️ Purchase license from Astrodienst |

## The Dual License

### Option 1: GNU GPL v2 or Later (FREE)

**You can use Swiss Ephemeris for FREE if:**
- ✅ Your entire application is open source
- ✅ You use a GPL-compatible license (GPL, LGPL, MIT, Apache 2.0, etc.)
- ✅ You make source code available to users
- ✅ You allow users to modify and redistribute

**Examples of GPL-compatible use:**
- Open source astrology website (source published)
- Educational project (publicly available)
- Research tool (shared with community)
- Free app with published source code

### Option 2: Commercial License (PAID)

**You MUST purchase a commercial license if:**
- ❌ Your app is proprietary (closed source)
- ❌ You sell the software or service
- ❌ You don't want to open source your code
- ❌ Your app is for commercial use

**Examples requiring commercial license:**
- Paid mobile app (even if using Moshier)
- Commercial astrology service
- SaaS platform (even if free tier)
- Internal corporate tool
- Any proprietary software

## Common Misconceptions

### ❌ WRONG: "Moshier is license-free"
**Reality**: Moshier calculations are part of Swiss Ephemeris library. Library license applies.

### ❌ WRONG: "No data files = no license needed"
**Reality**: License covers the **code/library**, not just data files.

### ❌ WRONG: "pyswisseph is just Python bindings"
**Reality**: It's a wrapper around Swiss Ephemeris C library. Same license.

### ❌ WRONG: "It's open source, so I can use it freely"
**Reality**: Open source ≠ free for commercial use. GPL requires your app to be GPL too.

## What Does "Proprietary" Mean?

Your software is proprietary if:
- You don't publish the source code
- Users can't modify or redistribute it
- You retain exclusive rights
- You use a non-GPL-compatible license

**Even if it's free**, if you don't open source it, it's proprietary!

## Your Project: Pandit Allocation System

### Questions to Ask

1. **Will you open source the entire application?**
   - If YES → Can use GPL version (free)
   - If NO → Need commercial license

2. **Will users have access to source code?**
   - If YES → Can use GPL version (free)
   - If NO → Need commercial license

3. **Is this a commercial service?**
   - If YES and closed source → Need commercial license
   - If YES and open source → GPL version OK

4. **Will this be a SaaS platform?**
   - If YES and closed source → Need commercial license
   - If YES and open source → GPL version OK

## Recommendation for Your Project

### Option A: Open Source (FREE)
```
✅ Pros:
   - No licensing fees
   - Can use Moshier or Swiss ephemeris
   - Legal for production
   - Community benefits

❌ Cons:
   - Must publish all source code
   - Others can copy/modify
   - Less control over IP
```

### Option B: Commercial License (PAID)
```
✅ Pros:
   - Keep source code private
   - Full commercial rights
   - Professional support available
   - More control over IP

❌ Cons:
   - €250-500 one-time fee
   - Legal agreement required
   - May limit distribution
```

### Option C: Alternative Libraries (FREE for all uses)

Consider these alternatives if you want to avoid GPL:

#### 1. **PyEphem** (MIT/LGPL)
```python
pip install ephem
```
- License: LGPL (more permissive than GPL)
- Accuracy: Good (arcseconds)
- Use: Free for commercial/proprietary
- Limitation: Older algorithms

#### 2. **Skyfield** (MIT License)
```python
pip install skyfield
```
- License: **MIT** (very permissive!)
- Accuracy: Excellent (uses JPL data)
- Use: **Free for any purpose** including commercial
- Modern Python library
- Highly recommended!

#### 3. **Astropy** (BSD License)
```python
pip install astropy
```
- License: **BSD 3-Clause** (very permissive!)
- Accuracy: Excellent
- Use: **Free for any purpose**
- Professional astronomy library

## Skyfield: The Best Alternative

If you want to avoid GPL licensing issues, **Skyfield is highly recommended**:

### Skyfield Advantages

```python
from skyfield.api import load, wgs84

# Free for commercial use, MIT license
# Excellent accuracy
# Modern Python API
# JPL ephemeris data (can download)

# Example:
ts = load.timescale()
t = ts.utc(2026, 1, 15)
eph = load('de421.bsp')  # JPL ephemeris

sun = eph['sun']
moon = eph['moon']
earth = eph['earth']

# Calculate positions
astrometric = earth.at(t).observe(sun)
alt, az, d = astrometric.apparent().altaz()
```

**License**: MIT (permissive for commercial use)  
**Accuracy**: Equal to Swiss Ephemeris  
**Cost**: **FREE for any use**  
**Support**: Active development, good docs  

## How to Proceed

### Step 1: Decide Your Licensing Strategy

```
┌─────────────────────────────────────────┐
│  Will you open source your app?         │
├─────────────────────────────────────────┤
│  YES → Use Swiss Ephemeris (GPL)       │
│  NO  → Option A: Buy commercial license │
│        Option B: Use Skyfield (MIT)     │
└─────────────────────────────────────────┘
```

### Step 2: If Open Source (GPL)
- ✅ Continue using pyswisseph
- ✅ Choose GPL-compatible license for your project
- ✅ Publish source code
- ✅ FREE to use in production

### Step 3: If Proprietary
**Option A**: Purchase Swiss Ephemeris commercial license
- Contact: swisseph@astro.com
- Cost: ~€250-500
- Get legal commercial license

**Option B**: Switch to Skyfield (recommended)
- MIT license (permissive)
- Free for commercial use
- Excellent accuracy
- No licensing concerns

## Swiss Ephemeris Commercial License

### How to Purchase

1. **Contact Astrodienst**
   - Website: https://www.astro.com/swisseph/
   - Email: swisseph@astro.com
   - Explain your use case

2. **Provide Information**
   - Your application description
   - Commercial or non-commercial
   - Distribution method

3. **Purchase License**
   - One-time fee (~€250-500)
   - Receive license certificate
   - Legal to use in production

4. **Compliance**
   - Keep license certificate
   - May need to credit Swiss Ephemeris
   - Follow license terms

## Legal Disclaimer

**I am not a lawyer. This is not legal advice.**

This document provides general information about Swiss Ephemeris licensing based on publicly available information. For legal advice specific to your situation:

- Consult a lawyer specializing in software licensing
- Contact Astrodienst directly: swisseph@astro.com
- Review the full license text at: https://www.astro.com/swisseph/

## Summary Table

| What You're Doing | Swiss Ephemeris | Skyfield | PyEphem |
|-------------------|-----------------|----------|---------|
| Open source app | ✅ GPL (free) | ✅ MIT (free) | ✅ LGPL (free) |
| Closed source app | ⚠️ Need license | ✅ MIT (free) | ⚠️ LGPL (complex) |
| Commercial SaaS | ⚠️ Need license | ✅ MIT (free) | ⚠️ LGPL (complex) |
| Internal tool | ⚠️ Need license | ✅ MIT (free) | ⚠️ LGPL (complex) |
| Research/education | ✅ GPL OK | ✅ MIT (free) | ✅ LGPL (free) |

## Recommendation

### For Development/Testing
- ✅ Continue using Swiss Ephemeris (no issues)

### For Production

**If Open Source:**
- ✅ Use Swiss Ephemeris with GPL license

**If Proprietary:**
- 🌟 **Recommended**: Switch to **Skyfield** (MIT license, free for commercial)
- Or: Purchase Swiss Ephemeris commercial license

## More Information

- Swiss Ephemeris: https://www.astro.com/swisseph/
- GPL License: https://www.gnu.org/licenses/gpl-3.0.html
- Skyfield: https://rhodesmill.org/skyfield/
- PyEphem: https://rhodesmill.org/pyephem/

---

**When in doubt, contact Astrodienst or consult a lawyer before production deployment.**

## References

1. Swiss Ephemeris Homepage: https://www.astro.com/swisseph/
2. Swiss Ephemeris License Page: https://www.astro.com/swisseph/swephinfo_e.htm#_Toc505244798
3. GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
4. Skyfield (MIT): https://rhodesmill.org/skyfield/
5. Contact: swisseph@astro.com
