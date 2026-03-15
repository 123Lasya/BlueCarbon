import os
import re

html_dir = r"C:\Users\m4827\OneDrive\Desktop\bluecarbon\frontend\admin"

# The sidebar template
ASIDE_TEMPLATE = """    <!-- Sidebar -->
    <aside class="w-64 glass-dark text-white hidden md:flex flex-col relative z-20">
        <div class="p-8 border-b border-white/10 flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-lg shadow-brand-500/20">
                <i data-lucide="leaf" class="w-5 h-5 text-white"></i>
            </div>
            <div>
                <span class="font-bold text-lg tracking-tight leading-none block">GovAdmin</span>
                <span class="text-xs text-slate-400 font-medium tracking-wider uppercase">Portal</span>
            </div>
        </div>
        <nav class="flex-1 px-4 space-y-1.5 mt-6 relative z-10">
            <a href="/api/admin/dashboard" class="flex items-center gap-3 px-4 py-3.5 {nav_dashboard} transition-all group">
                <i data-lucide="layout-dashboard" class="w-5 h-5 {icon_dashboard} transition-colors"></i> Overview & Map
            </a>
            <a href="/api/admin/credit-requests" class="flex items-center gap-3 px-4 py-3.5 {nav_credits} transition-all group">
                <i data-lucide="file-text" class="w-5 h-5 {icon_credits} transition-colors"></i> Credit Requests
            </a>
            <a href="/api/admin/analytics" class="flex items-center gap-3 px-4 py-3.5 {nav_analytics} transition-all group">
                <i data-lucide="bar-chart-2" class="w-5 h-5 {icon_analytics} transition-colors"></i> Analytics
            </a>
            <a href="/api/admin/map" class="flex items-center gap-3 px-4 py-3.5 {nav_map} transition-all group">
                <i data-lucide="map" class="w-5 h-5 {icon_map} transition-colors"></i> National Map View
            </a>
        </nav>

        <!-- User Profile Area -->
        <div class="p-6 border-t border-white/10">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center text-sm font-bold text-slate-300">
                        AD
                    </div>
                    <div>
                        <p class="text-sm font-bold text-white leading-tight">Admin User</p>
                        <p class="text-xs text-slate-400">Government Node</p>
                    </div>
                </div>
                <a href="/api/login" class="text-slate-400 hover:text-red-400 transition-colors p-2 rounded-lg hover:bg-white/5" title="Sign Out">
                    <i data-lucide="log-out" class="w-5 h-5"></i>
                </a>
            </div>
        </div>
    </aside>"""

ACTIVE_NAV = "bg-brand-500/10 rounded-2xl text-brand-400 font-semibold"
ACTIVE_ICON = ""
INACTIVE_NAV = "hover:bg-white/5 rounded-2xl text-slate-300 font-medium"
INACTIVE_ICON = "group-hover:text-white"

def get_sidebar(active_tab):
    return ASIDE_TEMPLATE.format(
        nav_dashboard=ACTIVE_NAV if active_tab == 'dashboard' else INACTIVE_NAV,
        icon_dashboard=ACTIVE_ICON if active_tab == 'dashboard' else INACTIVE_ICON,
        nav_credits=ACTIVE_NAV if active_tab == 'credits' else INACTIVE_NAV,
        icon_credits=ACTIVE_ICON if active_tab == 'credits' else INACTIVE_ICON,
        nav_analytics=ACTIVE_NAV if active_tab == 'analytics' else INACTIVE_NAV,
        icon_analytics=ACTIVE_ICON if active_tab == 'analytics' else INACTIVE_ICON,
        nav_map=ACTIVE_NAV if active_tab == 'map' else INACTIVE_NAV,
        icon_map=ACTIVE_ICON if active_tab == 'map' else INACTIVE_ICON,
    )

pages = {
    'approvals.html': 'dashboard',
    'credit_requests.html': 'credits',
    'analytics.html': 'analytics',
    'map.html': 'map'
}

HEAD_INJECTIONS = """
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Outfit', 'sans-serif'] },
                    colors: {
                        brand: { 50: '#f0fdf4', 100: '#dcfce7', 500: '#22c55e', 600: '#16a34a', 900: '#14532d' },
                        surface: { 50: '#f8fafc', 100: '#f1f5f9', 800: '#1e293b', 900: '#0f172a' }
                    }
                }
            }
        }
    </script>
    <style>
        .glass-panel {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .glass-dark {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(16px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
    </style>
"""

for filename, tab in pages.items():
    filepath = os.path.join(html_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace sidebar
    # We find the aside tag. It starts with <aside and ends with </aside>
    aside_pattern = re.compile(r'<!-- Sidebar -->[\s\S]*?</aside>')
    if aside_pattern.search(content):
        content = aside_pattern.sub(get_sidebar(tab), content)
    else:
        # Some might not have <!-- Sidebar -->, just <aside
        aside_pattern2 = re.compile(r'<aside[\s\S]*?</aside>')
        content = aside_pattern2.sub(get_sidebar(tab), content)

    # Inject tailwind config and styles into head if missing
    if 'tailwind.config' not in content:
        # Ensure Outfit font is loaded
        content = re.sub(r'<link href="https://fonts.googleapis.com/css2\?family=Inter[^>]+>', r'<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">', content)
        
        # inject before </head>
        content = content.replace('</head>', HEAD_INJECTIONS + '\n</head>')

    # Fix body class if it has old ones
    content = re.sub(r'<body class="([^"]+)">', lambda m: '<body class="' + m.group(1).replace("bg-gray-50", "bg-surface-50").replace("font-['Inter']", "") + '">', content)

    # For approvals.html, do the section swap
    if filename == 'approvals.html':
        approved_match = re.search(r'(?s)( +<!-- Approved Projects -->\n +<section(?: class="mb-12")?>.*?</section>\n)', content)
        queue_match = re.search(r'(?s)( +<!-- Verification Queue -->\n +<section(?: class="mb-12")?>\n +<div class="flex justify-between items-end mb-6">.*?</section>\n)', content)

        if approved_match and queue_match:
            # We want Queue first, then Approved
            queue_text = queue_match.group(1)
            approved_text = approved_match.group(1)
            
            # Make sure queue has mb-12, and approved doesn't need it if it's middle, but usually it's fine
            queue_text = queue_text.replace('<section>', '<section class="mb-12">')
            approved_text = approved_text.replace('<section class="mb-12">', '<section>')
            
            start_idx = min(approved_match.start(), queue_match.start())
            end_idx = max(approved_match.end(), queue_match.end())
            
            new_block = queue_text + '\n' + approved_text
            content = content[:start_idx] + new_block + content[end_idx:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updates applied successfully.")
