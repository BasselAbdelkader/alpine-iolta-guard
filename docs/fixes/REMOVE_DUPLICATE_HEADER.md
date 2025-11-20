# Remove Duplicate Firm Header

**Issue:** Firm information appearing in page headers when it's already in sidebar

---

## Quick CSS Fix

If you want to hide the duplicate header immediately, add this to your CSS:

**File:** `/usr/share/nginx/html/css/main.css`

```css
/* Hide duplicate firm header in page content */
.page-header .firm-info,
.content-header .firm-info,
header .firm-info {
    display: none !important;
}

/* Or if it has specific class/id */
#firmHeaderInfo,
.firm-header-text {
    display: none !important;
}
```

---

## To Find and Remove Permanently

### **Step 1: Identify Where It Appears**

Please check:
1. Which pages show this header? (Dashboard, Clients, Reports, etc.)
2. Where on the page? (Top, below navigation, in content area, etc.)
3. Is it visible on screen or only when printing?

### **Step 2: Common Locations**

**A. Print Stylesheets:**
Check: `/usr/share/nginx/html/css/print.css`
```css
/* Often reports include firm header for printing */
@media print {
    .report-header::before {
        content: "Firm Name | Address | Phone";
    }
}
```

**B. Report Templates:**
Check files like:
- `/usr/share/nginx/html/html/reports/*.html`
- Look for hardcoded firm info in headers

**C. JavaScript Dynamic Headers:**
Check if any JS files add firm info to page headers:
```bash
docker exec iolta_frontend_alpine grep -r "innerHTML.*Insurance\|textContent.*212" /usr/share/nginx/html/js/
```

**D. Common Header Template:**
Some pages might include a shared header file that has the firm info.

---

## Temporary Solution

Add this to **every page** where you see the duplicate header:

```html
<style>
    /* Hide duplicate firm information */
    .firm-header-duplicate {
        display: none !important;
    }
</style>
```

---

## Need More Info

To help you remove this permanently, I need to know:

1. **Which pages show it?** (list of page names)
2. **Screenshot or exact location?** (top of page, below nav, etc.)
3. **HTML around the text?** (right-click → Inspect Element, copy the HTML)

Once you provide this, I can:
- Find the exact location in the code
- Remove it permanently
- Update the correct files

---

## Alternative: JavaScript Solution

If the header is added dynamically, you can remove it with JavaScript:

```javascript
// Add to each page's JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Remove any element containing the firm address
    const elements = document.querySelectorAll('*');
    elements.forEach(el => {
        if (el.textContent.includes('1200 Insurance Plaza')) {
            // Hide or remove the parent container
            const parent = el.closest('.header, .page-header, div');
            if (parent) {
                parent.style.display = 'none';
            }
        }
    });
});
```

---

**Status:** Need more information to provide exact fix
**Temporary Fix:** Use CSS `display: none` as shown above
**Permanent Fix:** Requires knowing exact location in code
