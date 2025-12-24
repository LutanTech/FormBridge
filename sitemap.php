<?php

header('Content-Type: application/xml; charset=utf-8');

$urls = [
    ['loc' => 'https://formbridge.vercel.app/', 'priority' => '1.0'],
    ['loc' => 'https://formbridge.vercel.app/login', 'priority' => '0.9'],
    ['loc' => 'https://formbridge.vercel.app/register', 'priority' => '0.9'],
    ['loc' => 'https://formbridge.vercel.app/logout', 'priority' => '0.4'],
    ['loc' => 'https://formbridge.vercel.app/account', 'priority' => '0.8'],
    ['loc' => 'https://formbridge.vercel.app/status', 'priority' => '0.8'],
    ['loc' => 'https://formbridge.vercel.app/devices', 'priority' => '0.7'],
    ['loc' => 'https://formbridge.vercel.app/instance', 'priority' => '0.7'],
    ['loc' => 'https://formbridge.vercel.app/logbook', 'priority' => '0.6'],
    ['loc' => 'https://formbridge.vercel.app/submit', 'priority' => '0.6'],
    ['loc' => 'https://formbridge.vercel.app/support', 'priority' => '0.6'],
    ['loc' => 'https://formbridge.vercel.app/verify_email', 'priority' => '0.5'],
    ['loc' => 'https://formbridge.vercel.app/privacy_policy', 'priority' => '0.4'],
    ['loc' => 'https://formbridge.vercel.app/terms', 'priority' => '0.4'],
    ['loc' => 'https://formbridge.vercel.app/404', 'priority' => '0.1'],
];

echo '<?xml version="1.0" encoding="UTF-8"?>';
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
foreach ($urls as $url) {
    echo '<url>';
    echo '<loc>' . htmlspecialchars($url['loc']) . '</loc>';
    echo '<priority>' . $url['priority'] . '</priority>';
    echo '</url>';
}
echo '</urlset>';
